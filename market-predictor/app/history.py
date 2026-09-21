"""Log and retrieve signal history for backtesting and measurement."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import config


def log_signal(symbol: str, signal: dict, material_result: dict | None = None):
    """Record a signal attempt. Path is a simple append-only JSON lines file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "probability_up": signal.get("probability_up"),
        "signal": signal.get("signal"),
        "material": material_result,
    }
    try:
        with open(config.DB_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # silent fail, history is not load-bearing


def get_history(symbol: str | None = None, days: int = 90) -> list[dict]:
    """Read signal entries from the last N days, optionally filtered by symbol."""
    if not config.DB_PATH.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out = []
    try:
        with open(config.DB_PATH) as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("timestamp", ""))
                if ts >= cutoff and (symbol is None or entry.get("symbol") == symbol):
                    out.append(entry)
    except Exception:
        pass
    return out


def purge_old():
    """Remove entries older than HISTORY_KEEP_DAYS. Run periodically."""
    if not config.DB_PATH.exists():
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=config.HISTORY_KEEP_DAYS)
    try:
        with open(config.DB_PATH) as f:
            lines = [ln for ln in f if ln.strip()]
        fresh = []
        for ln in lines:
            entry = json.loads(ln)
            ts = datetime.fromisoformat(entry.get("timestamp", ""))
            if ts >= cutoff:
                fresh.append(ln)
        with open(config.DB_PATH, "w") as f:
            f.writelines(fresh)
    except Exception:
        pass
