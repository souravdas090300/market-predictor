"""Candlestick pattern recognition.

`detect(df)` returns one boolean column per pattern (True on the bar where the pattern completes).
Reversal patterns only fire in the right context, e.g. a hammer needs a prior downtrend.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# name -> (bias, plain-language meaning)
PATTERNS: dict[str, tuple[int, str]] = {
    "hammer": (+1, "Long lower wick after a decline: sellers pushed price down but buyers took it back."),
    "shooting_star": (-1, "Long upper wick after a rise: buyers pushed price up but sellers took it back."),
    "bullish_engulfing": (+1, "A green candle fully covers the prior red one: buyers overpowered sellers."),
    "bearish_engulfing": (-1, "A red candle fully covers the prior green one: sellers overpowered buyers."),
    "morning_star": (+1, "Three-bar bottom: big red, small indecision, big green. Often marks a turn up."),
    "evening_star": (-1, "Three-bar top: big green, small indecision, big red. Often marks a turn down."),
    "piercing_line": (+1, "Green candle closes above the midpoint of the prior red one after a decline."),
    "dark_cloud_cover": (-1, "Red candle closes below the midpoint of the prior green one after a rise."),
    "bullish_harami": (+1, "Small green candle inside a big red one: selling momentum is fading."),
    "bearish_harami": (-1, "Small red candle inside a big green one: buying momentum is fading."),
    "three_white_soldiers": (+1, "Three strong green candles in a row, each closing higher: steady buying."),
    "three_black_crows": (-1, "Three strong red candles in a row, each closing lower: steady selling."),
    "bullish_marubozu": (+1, "Long green candle with almost no wicks: buyers controlled the whole session."),
    "bearish_marubozu": (-1, "Long red candle with almost no wicks: sellers controlled the whole session."),
    "doji": (0, "Open and close nearly equal: indecision. Matters most after a strong move."),
}

BULLISH = [k for k, (b, _) in PATTERNS.items() if b > 0]
BEARISH = [k for k, (b, _) in PATTERNS.items() if b < 0]


def _parts(df: pd.DataFrame) -> dict[str, pd.Series]:
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body = (c - o).abs()
    return {
        "o": o, "h": h, "l": l, "c": c,
        "body": body,
        "rng": (h - l),
        "upper": h - np.maximum(o, c),
        "lower": np.minimum(o, c) - l,
        "avg_body": body.rolling(10).mean(),
    }


def detect(df: pd.DataFrame) -> pd.DataFrame:
    p = _parts(df)
    o, h, l, c = p["o"], p["h"], p["l"], p["c"]
    body, rng, upper, lower, avg = p["body"], p["rng"], p["upper"], p["lower"], p["avg_body"]

    green, red = c > o, c < o
    long_body = body > avg
    small_body = body < 0.5 * avg

    sma10 = c.rolling(10).mean()
    was_down = c.shift(1) < sma10.shift(1)
    was_up = c.shift(1) > sma10.shift(1)

    o1, c1, h1, l1 = o.shift(1), c.shift(1), h.shift(1), l.shift(1)
    o2, c2 = o.shift(2), c.shift(2)
    body1, body2 = body.shift(1), body.shift(2)
    green1, red1 = green.shift(1, fill_value=False), red.shift(1, fill_value=False)
    green2, red2 = green.shift(2, fill_value=False), red.shift(2, fill_value=False)
    long1, long2 = long_body.shift(1, fill_value=False), long_body.shift(2, fill_value=False)

    out = pd.DataFrame(index=df.index)

    out["doji"] = (rng > 0) & (body <= 0.1 * rng)
    out["hammer"] = was_down & (body > 0) & (lower >= 2 * body) & (upper <= 0.15 * rng)
    out["shooting_star"] = was_up & (body > 0) & (upper >= 2 * body) & (lower <= 0.15 * rng)

    out["bullish_engulfing"] = was_down & red1 & green & (o <= c1) & (c >= o1) & (body > body1)
    out["bearish_engulfing"] = was_up & green1 & red & (o >= c1) & (c <= o1) & (body > body1)

    mid2 = (o2 + c2) / 2
    out["morning_star"] = (was_down.shift(1, fill_value=False) & red2 & long2
                           & (body1 <= 0.3 * body2) & green & (c > mid2))
    out["evening_star"] = (was_up.shift(1, fill_value=False) & green2 & long2
                           & (body1 <= 0.3 * body2) & red & (c < mid2))

    mid1 = (o1 + c1) / 2
    out["piercing_line"] = was_down & red1 & long1 & green & (o < c1) & (c > mid1) & (c < o1)
    out["dark_cloud_cover"] = was_up & green1 & long1 & red & (o > c1) & (c < mid1) & (c > o1)

    out["bullish_harami"] = (was_down & red1 & long1 & green & (o > c1) & (c < o1) & (body < 0.6 * body1))
    out["bearish_harami"] = (was_up & green1 & long1 & red & (o < c1) & (c > o1) & (body < 0.6 * body1))

    strong = body > 0.6 * avg
    out["three_white_soldiers"] = (green & green1 & green2 & strong & (c > c1) & (c1 > c2)
                                   & (o > o1) & (o < c1) & (o1 > o2) & (o1 < c2))
    out["three_black_crows"] = (red & red1 & red2 & strong & (c < c1) & (c1 < c2)
                                & (o < o1) & (o > c1) & (o1 < o2) & (o1 > c2))

    marubozu = (rng > 0) & (body >= 0.9 * rng) & (body > avg)
    out["bullish_marubozu"] = marubozu & green
    out["bearish_marubozu"] = marubozu & red

    return out.fillna(False).astype(bool)[list(PATTERNS)]


def shape_features(df: pd.DataFrame) -> pd.DataFrame:
    """Numeric candle-shape and pattern-count features for the ML model."""
    p = _parts(df)
    rng = p["rng"].replace(0, np.nan)
    pats = detect(df)
    f = pd.DataFrame(index=df.index)
    f["cndl_body"] = ((p["c"] - p["o"]) / rng).fillna(0.0)
    f["cndl_upper_wick"] = (p["upper"] / rng).fillna(0.0)
    f["cndl_lower_wick"] = (p["lower"] / rng).fillna(0.0)
    f["cndl_bull_3d"] = pats[BULLISH].sum(axis=1).rolling(3, min_periods=1).sum()
    f["cndl_bear_3d"] = pats[BEARISH].sum(axis=1).rolling(3, min_periods=1).sum()
    return f


def recent_patterns(df: pd.DataFrame, bars: int = 5) -> list[dict]:
    """Patterns completed in the last `bars` candles, newest first."""
    pats = detect(df).tail(bars)
    found = []
    for ts, row in pats[::-1].iterrows():
        for name in pats.columns[row.values]:
            bias, meaning = PATTERNS[name]
            found.append({
                "date": ts.strftime("%Y-%m-%d"),
                "pattern": name.replace("_", " "),
                "bias": "bullish" if bias > 0 else "bearish" if bias < 0 else "neutral",
                "meaning": meaning,
            })
    return found


def ohlc_tail(df: pd.DataFrame, bars: int = 60) -> list[dict]:
    t = df.tail(bars)
    rows = []
    for ts, r in t.iterrows():
        item = {
            "d": ts.strftime("%Y-%m-%d"),
            "o": round(float(r.open), 4),
            "h": round(float(r.high), 4),
            "l": round(float(r.low), 4),
            "c": round(float(r.close), 4),
        }
        if "volume" in t.columns:
            item["v"] = round(float(r.volume), 2)
        rows.append(item)
    return rows
