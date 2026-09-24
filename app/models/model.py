"""Training, walk-forward evaluation, probability calibration and persistence."""
from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import TimeSeriesSplit

from ..core import config
from .features import build_features, build_target


def _make_model() -> HistGradientBoostingClassifier:
    # Shallow trees + strong regularisation: financial data is noisy and overfits easily.
    return HistGradientBoostingClassifier(
        max_depth=3, learning_rate=0.05, max_iter=150,
        l2_regularization=1.0, min_samples_leaf=40, random_state=42,
    )


def _dataset(df: pd.DataFrame, horizon: int):
    X = build_features(df)
    y, fwd = build_target(df["close"], horizon)
    keep = X.notna().all(axis=1) & y.notna()
    return X[keep], y[keep].astype(int), fwd[keep]


def _logit(p) -> np.ndarray:
    p = np.clip(np.asarray(p, dtype=float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p)).reshape(-1, 1)


def apply_calibration(calibrator: LogisticRegression, raw_p) -> np.ndarray:
    return calibrator.predict_proba(_logit(raw_p))[:, 1]


def _out_of_sample(X, y, horizon: int, n_splits: int) -> pd.Series:
    """Each fold trains only on the past and predicts the next block.

    `gap=horizon` removes the overlap between the last training labels and the first
    test rows (the classic leak with multi-day forward returns).
    """
    tscv = TimeSeriesSplit(n_splits=n_splits, gap=horizon)
    probs = pd.Series(np.nan, index=X.index)
    for train_idx, test_idx in tscv.split(X):
        m = _make_model().fit(X.iloc[train_idx], y.iloc[train_idx])
        probs.iloc[test_idx] = m.predict_proba(X.iloc[test_idx])[:, 1]
    return probs


def _fit_calibrator(raw_oos: pd.Series, y: pd.Series) -> LogisticRegression:
    """Platt scaling fitted on out-of-sample predictions."""
    mask = raw_oos.notna()
    return LogisticRegression(C=1.0).fit(_logit(raw_oos[mask]), y[mask])


def _metrics(p: pd.Series, y: pd.Series, fwd: pd.Series, horizon: int) -> dict:
    mask = p.notna()
    p, yt, ft = p[mask], y[mask], fwd[mask]
    pred = (p > 0.5).astype(int)
    lean = config.BULLISH_ABOVE, config.BEARISH_BELOW
    high_conf = (p >= lean[0]) | (p <= lean[1])
    position = np.where(p > 0.5, 1.0, -1.0)
    return {
        "samples": int(mask.sum()),
        "accuracy": round(float((pred == yt).mean()), 4),
        "baseline_accuracy": round(float(max(yt.mean(), 1 - yt.mean())), 4),
        "auc": round(float(roc_auc_score(yt, p)), 4) if yt.nunique() == 2 else None,
        "high_conviction_accuracy": (
            round(float((pred[high_conf] == yt[high_conf]).mean()), 4) if high_conf.sum() >= 20 else None
        ),
        "high_conviction_signals": int(high_conf.sum()),
        "avg_return_per_signal": round(float((position * ft).mean()), 5),
        "avg_return_always_long": round(float(ft.mean()), 5),
        "horizon_days": horizon,
    }


def walk_forward(df: pd.DataFrame, horizon: int = config.HORIZON_DAYS, n_splits: int = 5) -> dict:
    X, y, fwd = _dataset(df, horizon)
    raw = _out_of_sample(X, y, horizon, n_splits)
    cal = _fit_calibrator(raw, y)
    p = pd.Series(np.nan, index=raw.index)
    ok = raw.notna()
    p[ok] = apply_calibration(cal, raw[ok])
    return _metrics(p, y, fwd, horizon)


def _path(symbol: str):
    safe = re.sub(r"[^A-Za-z0-9]+", "_", symbol).strip("_")
    return config.MODEL_DIR / f"{safe}.joblib"


def train(symbol: str, df: pd.DataFrame, horizon: int = config.HORIZON_DAYS) -> dict:
    X, y, fwd = _dataset(df, horizon)
    raw = _out_of_sample(X, y, horizon, n_splits=5)
    cal = _fit_calibrator(raw, y)
    p = pd.Series(np.nan, index=raw.index)
    ok = raw.notna()
    p[ok] = apply_calibration(cal, raw[ok])

    bundle = {
        "model": _make_model().fit(X, y),
        "calibrator": cal,
        "columns": list(X.columns),
        "metrics": _metrics(p, y, fwd, horizon),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "trained_ts": time.time(),
        "horizon": horizon,
    }
    joblib.dump(bundle, _path(symbol))
    return bundle


def predict_up(bundle: dict, latest_row: pd.DataFrame) -> tuple[float, float]:
    """Returns (calibrated P(up), raw model P(up))."""
    raw = float(bundle["model"].predict_proba(latest_row[bundle["columns"]])[0, 1])
    return float(apply_calibration(bundle["calibrator"], [raw])[0]), raw


def load_or_train(symbol: str, df: pd.DataFrame, retrain: bool = False) -> dict:
    p = _path(symbol)
    if not retrain and p.exists():
        bundle = joblib.load(p)
        age_days = (time.time() - bundle["trained_ts"]) / 86400
        if age_days <= config.MODEL_MAX_AGE_DAYS and bundle["horizon"] == config.HORIZON_DAYS \
                and "calibrator" in bundle:
            return bundle
    return train(symbol, df)
