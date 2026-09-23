"""Offline tests: synthetic prices, no network. Run with:  pytest -q"""
import numpy as np
import pandas as pd
import pytest

from app.models import candles, features, model, predict
from app.core import config, data


def synthetic_prices(n=1500, seed=0):
    rng = np.random.default_rng(seed)
    ret = rng.normal(0.0004, 0.012, n)
    close = 100 * np.exp(np.cumsum(ret))
    open_ = np.r_[close[0], close[:-1]] * (1 + rng.normal(0, 0.002, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, n)))
    idx = pd.bdate_range(end="2026-09-18", periods=n)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                         "volume": rng.integers(1_000, 5_000, n).astype(float)}, index=idx)


def downtrend(n=30, start=100.0, step=1.0):
    idx = pd.bdate_range(end="2026-09-18", periods=n)
    close = start - step * np.arange(n)
    open_ = close + step * 0.6
    return pd.DataFrame({"open": open_, "high": open_ + 0.2, "low": close - 0.2, "close": close,
                         "volume": 1000.0}, index=idx)


def add_bar(df, o, h, l, c):
    ts = df.index[-1] + pd.tseries.offsets.BDay(1)
    df.loc[ts] = [o, h, l, c, 1000.0]
    return df


def test_features_do_not_peek_into_the_future():
    df = synthetic_prices()
    full = features.build_features(df)
    cut = features.build_features(df.iloc[:1200])
    pd.testing.assert_frame_equal(full.iloc[:1200], cut, check_exact=False, atol=1e-9)


def test_target_has_no_label_for_unfinished_windows():
    df = synthetic_prices()
    y, _ = features.build_target(df["close"], 5)
    assert y.iloc[-5:].isna().all() and y.iloc[:-5].notna().all()


def test_hammer_detected_after_decline():
    df = downtrend()
    last = df["close"].iloc[-1]
    add_bar(df, last - 0.1, last + 0.1, last - 3.0, last + 0.05)  # tiny body, long lower wick
    assert candles.detect(df)["hammer"].iloc[-1]


def test_hammer_shape_ignored_in_uptrend():
    df = downtrend()[::-1].reset_index(drop=True)
    df.index = pd.bdate_range(end="2026-09-18", periods=len(df))
    last = df["close"].iloc[-1]
    add_bar(df, last - 0.1, last + 0.1, last - 3.0, last + 0.05)
    assert not candles.detect(df)["hammer"].iloc[-1]


def test_bullish_engulfing_detected():
    df = downtrend()
    prev_open, prev_close = df["open"].iloc[-1], df["close"].iloc[-1]
    add_bar(df, prev_close - 0.3, prev_open + 1.0, prev_close - 0.5, prev_open + 0.8)
    assert candles.detect(df)["bullish_engulfing"].iloc[-1]


def test_walk_forward_reports_sane_metrics():
    m = model.walk_forward(synthetic_prices())
    assert 0.3 < m["accuracy"] < 0.7          # random data must not look predictive
    assert 0.4 < m["auc"] < 0.6
    assert m["samples"] > 500


@pytest.fixture
def patched(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "signals.db")
    monkeypatch.setattr(data, "get_prices", lambda symbol, period=None: synthetic_prices())
    monkeypatch.setattr(data, "get_live_quote", lambda symbol: {
        "symbol": symbol, "price": 101.25, "previous_close": 100.0,
        "change": 1.25, "change_pct": 0.0125, "as_of": "2026-09-23T00:00:00+00:00",
        "source": "yahoo",
    })
    monkeypatch.setattr(data, "get_news", lambda q, max_items=30: [
        {"title": "Stock surges to record high on strong growth", "source": "X",
         "published": pd.Timestamp.now(tz="UTC").to_pydatetime(), "link": "http://x"},
        {"title": "Analysts warn of recession fears", "source": "Y",
         "published": pd.Timestamp.now(tz="UTC").to_pydatetime(), "link": "http://y"},
    ])


def test_signal_shape(patched):
    r = predict.get_signal("TEST")
    assert r["signal"] in {"bullish", "bearish", "neutral"}
    assert 0 < r["probability_up"] < 1
    assert len(r["candles"]) == 60
    assert r["sentiment"]["headline_count"] == 2
    assert r["live"]["price"] == 101.25


def test_api(patched):
    from fastapi.testclient import TestClient
    from app.api import app
    c = TestClient(app)
    assert len(c.get("/api/watchlist").json()) == len(config.WATCHLIST)
    r = c.get("/api/signal/EURUSD=X")
    assert r.status_code == 200 and r.json()["signal"]
    q = c.get("/api/quote/EURUSD=X")
    assert q.status_code == 200 and q.json()["price"] == 101.25


# ---- commodities, market-aware wording and material mode ----

from app.services import material, sentiment


def test_symbol_class_inference():
    assert config.infer_class("GC=F") == "commodity"
    assert config.infer_class("USDJPY=X") == "forex"
    assert config.infer_class("SOL-USD") == "crypto"
    assert config.infer_class("TSLA") == "stock"
    assert {a["class"] for a in config.WATCHLIST} == {"stock", "crypto", "forex", "commodity"}


def test_commodity_wording_is_understood():
    assert sentiment.lexicon_score("OPEC announces output cut as inventory draw deepens", "commodity") > 0
    assert sentiment.lexicon_score("Supply glut and inventory build weigh on prices", "commodity") < 0
    # "inflation" is bad for shares, but not counted against commodities
    assert sentiment.lexicon_score("Inflation report due", "stock") < 0
    assert sentiment.lexicon_score("Inflation report due", "commodity") == 0


def test_phrase_words_are_not_double_counted():
    # "strong dollar" is one bearish phrase for commodities, not bullish "strong" + bearish phrase
    assert sentiment.lexicon_score("A strong dollar pressures the market", "commodity") == -1.0


def test_material_bullish_and_bearish():
    up = material.analyze("Earnings beat estimates and profits surge. Analysts upgrade the stock after strong growth.", "stock")
    down = material.analyze("Regulators open an investigation into fraud. Shares plunge on weak guidance and recession fears.", "stock")
    assert up["label"] == "bullish" and up["score"] > 0
    assert down["label"] == "bearish" and down["score"] < 0
    assert up["pushing_up"] and not up["pushing_down"]


def test_single_sentence_cannot_dominate():
    one = material.analyze("Shares surge to a record high after a strong quarter.", "stock")
    assert one["signals"] == 1 and abs(one["score"]) < 0.5


def test_material_rejects_empty_and_fragments():
    with pytest.raises(ValueError):
        material.analyze("   ")
    with pytest.raises(ValueError):
        material.analyze("Up. Down.")


def test_combine_nudges_but_never_overrides(patched):
    auto = predict.get_signal("TEST")
    strongly_bullish = {"score": 1.0}
    c = predict.combine(auto, strongly_bullish)
    assert abs(c["probability_up"] - auto["probability_up"]) <= config.MATERIAL_WEIGHT + 1e-6
    assert 0 < c["probability_up"] < 1


def test_material_api_modes(patched):
    from fastapi.testclient import TestClient
    from app.api import app
    c = TestClient(app)
    text = "Gold rallies as safe-haven demand grows. Analysts turn bullish on gold after a supply disruption."

    alone = c.post("/api/material", json={"symbol": "GC=F", "text": text, "combine": False}).json()
    assert alone["combined"] is None and alone["material"]["label"] == "bullish"

    both = c.post("/api/material", json={"symbol": "GC=F", "text": text, "combine": True}).json()
    assert both["combined"]["material_shift"] >= 0 and both["auto"]["signal"]

    assert c.post("/api/material", json={"symbol": "GC=F", "text": "", "combine": False}).status_code == 422
    assert c.post("/api/material", json={"symbol": "GC=F", "text": "x" * 20001, "combine": False}).status_code == 422
    kinds = {k["key"]: k["hints"] for k in c.get("/api/classes").json()}
    assert kinds["commodity"] and kinds["forex"]


# ---- advanced features ----

from app.core import fetcher
from app.services import history, metrics


def test_url_fetch_mock():
    # Don't actually fetch in tests; just check the function signature
    assert callable(fetcher.fetch_url)


def test_pdf_extract_rejects_bad_pdf():
    with pytest.raises(ValueError):
        fetcher.extract_pdf(b"not a pdf at all")


def test_csv_extract_works():
    csv_text = "symbol,price,change\nAAPL,150.0,+1.2\nMSFT,300.0,-0.5"
    csv_data = csv_text.encode("utf-8")
    r = fetcher.extract_csv(csv_data)
    assert "symbol" in r["text"].lower() and "150.0" in r["text"]
def test_history_log_and_retrieve(patched, tmp_path):
    config.DB_PATH = tmp_path / "test.db"
    signal = {"probability_up": 0.65, "signal": "bullish"}
    history.log_signal("AAPL", signal)
    hist = history.get_history("AAPL")
    assert len(hist) == 1 and hist[0]["symbol"] == "AAPL"


def test_metrics_empty_history():
    m = metrics.metrics_from_history("NEVER_TRADED")
    assert m["samples"] == 0


def test_portfolio_metrics_empty():
    m = metrics.portfolio_metrics(["AAPL", "BTC-USD"])
    assert m.get("symbols") == 2
