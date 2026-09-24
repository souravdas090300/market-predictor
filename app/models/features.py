"""Technical-indicator features. Every feature at row t uses only data up to and including t."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import candles


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    f = pd.DataFrame(index=df.index)

    for n in (1, 5, 10, 20):
        f[f"ret_{n}"] = c.pct_change(n)
    f["rsi_14"] = rsi(c)

    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    f["macd_pct"] = macd / c
    f["macd_hist_pct"] = (macd - signal) / c

    for n in (10, 20, 50, 200):
        f[f"sma_{n}_dist"] = c / c.rolling(n).mean() - 1
    f["sma_10_50"] = c.rolling(10).mean() / c.rolling(50).mean() - 1

    mid, std = c.rolling(20).mean(), c.rolling(20).std()
    f["bb_pctb"] = (c - (mid - 2 * std)) / (4 * std)

    prev = c.shift()
    tr = pd.concat([h - l, (h - prev).abs(), (l - prev).abs()], axis=1).max(axis=1)
    f["atr_pct"] = tr.rolling(14).mean() / c
    f["vol_20"] = c.pct_change().rolling(20).std()

    f["dist_high_252"] = c / c.rolling(252, min_periods=60).max() - 1
    f["dist_low_252"] = c / c.rolling(252, min_periods=60).min() - 1

    if v.fillna(0).sum() > 0:
        f["vol_z"] = (v - v.rolling(20).mean()) / v.rolling(20).std().replace(0, np.nan)
    else:
        f["vol_z"] = 0.0

    f = f.join(candles.shape_features(df))

    return f.replace([np.inf, -np.inf], np.nan)


def build_target(close: pd.Series, horizon: int) -> tuple[pd.Series, pd.Series]:
    """Forward return over `horizon` days, and 1/0 label for 'closes higher'.

    The last `horizon` rows have no outcome yet; they stay NaN and are dropped in training.
    """
    fwd = close.shift(-horizon) / close - 1
    y = (fwd > 0).astype(float).where(fwd.notna())
    return y, fwd
