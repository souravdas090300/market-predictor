"""Text sentiment in [-1, 1] for headlines and longer material.

Default is a finance lexicon with market-specific wording (no downloads, works offline). For
better accuracy install `transformers` + `torch` and set USE_FINBERT=1 to use FinBERT instead.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from functools import lru_cache

POSITIVE = {
    "surge", "surges", "soar", "soars", "rally", "rallies", "gain", "gains", "jump", "jumps",
    "rise", "rises", "climb", "climbs", "beat", "beats", "record", "high", "upgrade", "upgraded",
    "bullish", "growth", "profit", "profits", "strong", "boost", "optimism", "recovery",
    "rebound", "breakout", "outperform", "buy", "approval", "approved", "inflows", "expands",
    "wins", "surpass", "surpasses", "upbeat", "accelerates", "improves", "improved",
}
NEGATIVE = {
    "fall", "falls", "drop", "drops", "plunge", "plunges", "slump", "slumps", "sink", "sinks",
    "tumble", "tumbles", "miss", "misses", "low", "downgrade", "downgraded", "bearish", "loss",
    "losses", "weak", "fear", "fears", "crash", "selloff", "sell-off", "recession", "lawsuit",
    "probe", "investigation", "fraud", "ban", "bans", "layoffs", "warning", "warns", "default",
    "outflows", "decline", "declines", "inflation", "tariff", "tariffs", "hack", "hacked",
    "bankruptcy", "underperform", "sell", "slows", "worsens", "pessimism",
}

# Extra words that only mean something in one market.
CLASS_POSITIVE = {
    "commodity": {"shortage", "shortages", "deficit", "disruption", "disruptions"},
    "crypto": {"adoption", "accumulation", "staking"},
}
CLASS_NEGATIVE = {
    "commodity": {"glut", "oversupply", "surplus", "stockpile", "stockpiles"},
    "crypto": {"delisting", "liquidation", "liquidations", "exploit", "rug"},
}
# Words that are bad for shares but neutral or good for these markets.
CLASS_NEUTRAL = {"commodity": {"inflation", "tariff", "tariffs"}}

# Multi-word phrases; matched first so their words are not counted twice. Value is +1 or -1.
PHRASES = {
    "rate cut": 1, "rate cuts": 1, "rate hike": -1, "rate hikes": -1,
    "raises guidance": 1, "raises forecast": 1, "raised guidance": 1,
    "cuts guidance": -1, "cuts forecast": -1, "lowers guidance": -1, "lowered guidance": -1,
}
CLASS_PHRASES = {
    "commodity": {
        "supply cut": 1, "supply cuts": 1, "output cut": 1, "output cuts": 1,
        "production cut": 1, "production cuts": 1, "opec cut": 1, "opec cuts": 1,
        "inventory draw": 1, "inventory draws": 1, "stock draw": 1,
        "safe haven": 1, "safe-haven": 1, "haven demand": 1, "strong demand": 1,
        "inventory build": -1, "inventory builds": -1, "stock build": -1, "demand fears": -1,
        "demand concerns": -1, "weak demand": -1, "strong dollar": -1, "dollar strength": -1,
        "output hike": -1, "output increase": -1, "raises output": -1, "boosts output": -1,
    },
}
NEGATORS = {"not", "no", "never", "without", "fails", "fail"}

_WORD = re.compile(r"[a-z][a-z\-']+")


@lru_cache(maxsize=8)
def _lexicon(asset_class: str | None):
    pos, neg = set(POSITIVE), set(NEGATIVE)
    pos |= CLASS_POSITIVE.get(asset_class, set())
    neg |= CLASS_NEGATIVE.get(asset_class, set())
    neg -= CLASS_NEUTRAL.get(asset_class, set())
    phrases = {**PHRASES, **CLASS_PHRASES.get(asset_class, {})}
    ordered = sorted(phrases.items(), key=lambda kv: -len(kv[0]))
    return pos, neg, ordered


def lexicon_score(text: str, asset_class: str | None = None) -> float:
    pos, neg, phrases = _lexicon(asset_class)
    t = text.lower()
    score, hits = 0.0, 0
    for phrase, val in phrases:
        n = t.count(phrase)
        if n:
            score += val * n
            hits += n
            t = t.replace(phrase, " ")
    words = _WORD.findall(t)
    for i, w in enumerate(words):
        val = 1.0 if w in pos else -1.0 if w in neg else 0.0
        if val:
            if i > 0 and words[i - 1] in NEGATORS:
                val = -val
            score += val
            hits += 1
    return 0.0 if hits == 0 else max(-1.0, min(1.0, score / hits))


@lru_cache(maxsize=1)
def _finbert():
    from transformers import pipeline

    return pipeline("text-classification", model="ProsusAI/finbert", top_k=None)


def _finbert_scores(texts: list[str]) -> list[float]:
    out = _finbert()(texts, truncation=True)
    scores = []
    for res in out:
        d = {r["label"].lower(): r["score"] for r in res}
        scores.append(d.get("positive", 0.0) - d.get("negative", 0.0))
    return scores


def score_texts(texts: list[str], asset_class: str | None = None) -> list[float]:
    if not texts:
        return []
    if os.getenv("USE_FINBERT") == "1":
        try:
            return _finbert_scores(texts)
        except Exception:
            pass  # fall back to the lexicon if the model can't load
    return [lexicon_score(t, asset_class) for t in texts]


# Kept for older callers.
score_headlines = score_texts


def aggregate(news: list[dict], half_life_hours: float = 48.0, asset_class: str | None = None) -> dict:
    """Recency-weighted average sentiment across headlines.

    Returns {"score": float in [-1, 1], "count": int, "headlines": [...]}.
    """
    if not news:
        return {"score": 0.0, "count": 0, "headlines": []}

    scores = score_texts([n["title"] for n in news], asset_class)
    now = datetime.now(timezone.utc)
    num = den = 0.0
    rows = []
    for n, s in zip(news, scores):
        age_h = (now - n["published"]).total_seconds() / 3600 if n.get("published") else 72.0
        w = 0.5 ** (max(age_h, 0) / half_life_hours)
        num += w * s
        den += w
        rows.append({"title": n["title"], "source": n.get("source", ""), "link": n.get("link", ""),
                     "score": round(s, 2)})
    agg = num / den if den else 0.0
    rows.sort(key=lambda r: abs(r["score"]), reverse=True)
    return {"score": round(agg, 3), "count": len(news), "headlines": rows[:8]}
