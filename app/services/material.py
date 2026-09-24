"""Reads material the user supplies (articles, report summaries, notes) and turns it into a lean.

This is deliberately separate from the trained model: it reads wording, not facts, and has no
back-tested track record. It is shown next to the automatic signal and can nudge it when combined.
"""
from __future__ import annotations

import re

from ..core import config
from . import sentiment

MAX_SENTENCES = 300
MIN_SENTENCE_CHARS = 15
# Pulls the score toward zero when only a few sentences carry a signal.
SHRINK = 2.0

_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text: str) -> list[str]:
    parts = [p.strip(" \t-\u2022*#>") for p in _SPLIT.split(text)]
    return [p for p in parts if len(p) >= MIN_SENTENCE_CHARS][:MAX_SENTENCES]


def _label(score: float) -> str:
    if score >= config.MATERIAL_LEAN:
        return "bullish"
    if score <= -config.MATERIAL_LEAN:
        return "bearish"
    return "neutral"


def analyze(text: str, asset_class: str | None = None) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Paste some material to read: news, a report summary, or your own notes.")
    sentences = split_sentences(text)
    if not sentences:
        raise ValueError("Couldn't find full sentences in that. Paste a few sentences of news, a report, or notes.")

    scores = sentiment.score_texts(sentences, asset_class)
    signal = [(s, sc) for s, sc in zip(sentences, scores) if abs(sc) >= 0.05]
    n = len(signal)
    score = sum(sc for _, sc in signal) / (n + SHRINK)

    def pick(rows, reverse):
        rows = sorted(rows, key=lambda r: r[1], reverse=reverse)[:3]
        return [{"text": s[:240], "score": round(sc, 2)} for s, sc in rows]

    return {
        "score": round(score, 3),
        "strength": round(abs(score), 3),
        "label": _label(score),
        "sentences": len(sentences),
        "signals": n,
        "pushing_up": pick([r for r in signal if r[1] > 0], True),
        "pushing_down": pick([r for r in signal if r[1] < 0], False),
    }
