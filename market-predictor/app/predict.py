"""Turns a symbol into a bullish / bearish / neutral signal."""
from __future__ import annotations

from . import candles, config, data, model, sentiment
from .features import build_features


def label_for(p: float) -> str:
    if p >= config.BULLISH_ABOVE:
        return "bullish"
    if p <= config.BEARISH_BELOW:
        return "bearish"
    return "neutral"


def get_signal(symbol: str, use_news: bool = True, retrain: bool = False) -> dict:
    info = config.asset_info(symbol)
    df = data.get_prices(symbol)
    bundle = model.load_or_train(symbol, df, retrain=retrain)

    feats = build_features(df)
    latest = feats.dropna().iloc[[-1]]
    p_model, p_raw = model.predict_up(bundle, latest)

    news = data.get_news(info["query"]) if use_news else []
    sent = sentiment.aggregate(news, asset_class=info["class"])

    # News nudges the model's probability; it never overrides it.
    p_final = min(0.99, max(0.01, p_model + config.SENTIMENT_WEIGHT * sent["score"]))

    row = latest.iloc[0]
    return {
        "symbol": symbol,
        "name": info["name"],
        "class": info["class"],
        "as_of": latest.index[0].strftime("%Y-%m-%d"),
        "last_close": round(float(df["close"].iloc[-1]), 4),
        "horizon_days": config.HORIZON_DAYS,
        "signal": label_for(p_final),
        "probability_up": round(p_final, 4),
        "model_probability_up": round(p_model, 4),
        "model_raw_probability_up": round(p_raw, 4),
        # 0 = coin flip, 1 = maximum lean. This is NOT a win-rate.
        "conviction": round(abs(p_final - 0.5) * 2, 3),
        "sentiment": {"score": sent["score"], "headline_count": sent["count"],
                      "headlines": sent["headlines"]},
        "indicators": {
            "rsi_14": round(float(row["rsi_14"]), 1),
            "macd_hist_pct": round(float(row["macd_hist_pct"]) * 100, 3),
            "vs_sma_50_pct": round(float(row["sma_50_dist"]) * 100, 2),
            "vs_sma_200_pct": round(float(row["sma_200_dist"]) * 100, 2),
            "volatility_20d_pct": round(float(row["vol_20"]) * 100, 2),
        },
        "candle_patterns": candles.recent_patterns(df, bars=5),
        "candles": candles.ohlc_tail(df, bars=60),
        "backtest": bundle["metrics"],
        "model_trained_at": bundle["trained_at"],
    }


def combine(auto: dict, material_result: dict) -> dict:
    """Nudge the automatic probability with the user's material. Never overrides it."""
    p = min(0.99, max(0.01, auto["probability_up"] + config.MATERIAL_WEIGHT * material_result["score"]))
    return {
        "probability_up": round(p, 4),
        "signal": label_for(p),
        "conviction": round(abs(p - 0.5) * 2, 3),
        "material_shift": round(p - auto["probability_up"], 4),
    }
