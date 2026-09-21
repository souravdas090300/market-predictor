"""Risk and performance metrics for portfolios and historical signals."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import history


def metrics_from_history(symbol: str, days: int = 90) -> dict:
    """Compute basic metrics from logged signals (out-of-sample performance)."""
    entries = history.get_history(symbol, days)
    if not entries:
        return {"samples": 0}

    df = pd.DataFrame(entries)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df["signal_int"] = df["signal"].map({"bullish": 1, "neutral": 0, "bearish": -1})

    signals = df["signal_int"].dropna().astype(int)
    probs = df["probability_up"].dropna()

    if signals.empty:
        return {"samples": len(df)}

    # How often was the higher-confidence signal right?
    # Since we don't have outcomes, this is speculative.
    confident = df[df["probability_up"].between(0.65, 0.99) | df["probability_up"].between(0.01, 0.35)]
    return {
        "samples": len(entries),
        "avg_probability": round(float(probs.mean()), 3),
        "bull_lean": int((signals > 0).sum()),
        "bear_lean": int((signals < 0).sum()),
        "confidence_avg": round(float(df["probability_up"].abs() - 0.5).mean() * 2, 3),
        "high_confidence_calls": int(confident.shape[0]),
    }


def portfolio_metrics(symbols: list[str]) -> dict:
    """Aggregate metrics across a group of symbols."""
    all_entries = []
    for s in symbols:
        all_entries.extend(history.get_history(s, days=90))
    if not all_entries:
        return {"symbols": len(symbols), "total_signals": 0}
    df = pd.DataFrame(all_entries)
    signals = df["signal"].value_counts()
    return {
        "symbols": len(symbols),
        "total_signals": len(df),
        "bullish_count": int(signals.get("bullish", 0)),
        "bearish_count": int(signals.get("bearish", 0)),
        "neutral_count": int(signals.get("neutral", 0)),
        "avg_probability": round(float(df["probability_up"].mean()), 3),
    }
