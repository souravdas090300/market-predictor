"""FastAPI server. Run with:  uvicorn app.api:app --reload"""
from __future__ import annotations

import time

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, material, predict

app = FastAPI(title="Market lean")
_cache: dict[str, tuple[float, dict]] = {}


class MaterialIn(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)
    text: str = Field(max_length=20000)
    combine: bool = True


def _auto_signal(symbol: str, news: bool = True, refresh: bool = False) -> dict:
    key = f"{symbol}|{news}"
    hit = _cache.get(key)
    if hit and not refresh and time.time() - hit[0] < config.API_CACHE_SECONDS:
        return hit[1]
    try:
        result = predict.get_signal(symbol, use_news=news, retrain=refresh)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:  # network errors, yfinance hiccups, etc.
        raise HTTPException(status_code=502, detail=f"Could not analyse {symbol}: {e}")
    _cache[key] = (time.time(), result)
    return result


@app.get("/api/watchlist")
def watchlist():
    return config.WATCHLIST


@app.get("/api/classes")
def classes():
    return [{"key": k, "label": v, "hints": config.MATERIAL_HINTS.get(k, [])}
            for k, v in config.CLASS_LABELS.items()]


@app.get("/api/signal/{symbol:path}")
def signal(symbol: str, news: bool = True, refresh: bool = False):
    """Automatic mode: prices, candlesticks, ML model and recent news."""
    return _auto_signal(symbol, news, refresh)


@app.post("/api/material")
def read_material(body: MaterialIn):
    """Material mode: read the user's own text, alone or combined with the automatic signal."""
    asset_class = config.asset_info(body.symbol)["class"]
    try:
        analysis = material.analyze(body.text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if body.combine:
        auto = _auto_signal(body.symbol)
        combined = predict.combine(auto, analysis)
    return {
        "symbol": body.symbol,
        "asset_class": asset_class,
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


app.mount("/", StaticFiles(directory=str(config.ROOT / "static"), html=True), name="static")


class MaterialWithSource(MaterialIn):
    source: str = "text"  # text, url, pdf, csv


@app.post("/api/material-from-url")
def material_from_url(body: MaterialIn):
    """Fetch a URL and read it as material."""
    symbol = body.symbol
    url = body.text
    asset_class = config.asset_info(symbol)["class"]
    try:
        from . import fetcher
        result = fetcher.fetch_url(url)
        text = result["text"]
        analysis = material.analyze(text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if body.combine:
        auto = _auto_signal(symbol)
        combined = predict.combine(auto, analysis)
    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "source": "url",
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


@app.post("/api/material-from-file")
def material_from_file(symbol: str, file_bytes: bytes, file_type: str, combine: bool = True):
    """Upload PDF or CSV as material."""
    asset_class = config.asset_info(symbol)["class"]
    try:
        from . import fetcher
        if file_type == "pdf":
            result = fetcher.extract_pdf(file_bytes)
        elif file_type == "csv":
            result = fetcher.extract_csv(file_bytes)
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        text = result["text"]
        analysis = material.analyze(text, asset_class)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    auto = combined = None
    if combine:
        auto = _auto_signal(symbol)
        combined = predict.combine(auto, analysis)
    return {
        "symbol": symbol,
        "asset_class": asset_class,
        "source": file_type,
        "material": analysis,
        "auto": {"signal": auto["signal"], "probability_up": auto["probability_up"]} if auto else None,
        "combined": combined,
    }


@app.get("/api/signal/{symbol}/history")
def signal_history(symbol: str, days: int = 90):
    """Signal history and metrics for a symbol."""
    from . import history as hist
    entries = hist.get_history(symbol, days)
    metrics = hist.metrics_from_history(symbol, days)
    return {"symbol": symbol, "entries": entries, "metrics": metrics}


@app.post("/api/bulk")
def bulk_signals(symbols: list[str]):
    """Analyse up to 50 symbols in one request."""
    if len(symbols) > config.BULK_LIMIT:
        raise HTTPException(status_code=422, detail=f"Max {config.BULK_LIMIT} symbols at once")
    results = []
    for s in symbols:
        try:
            results.append(_auto_signal(s, news=True))
        except HTTPException:
            results.append({"symbol": s, "error": "Could not fetch"})
    return results


@app.get("/api/export/{symbol}")
def export_signals(symbol: str, format: str = "csv"):
    """Export signal history as CSV or JSON."""
    from . import history as hist
    entries = hist.get_history(symbol, days=config.HISTORY_KEEP_DAYS)
    if format == "csv":
        import csv
        from io import StringIO
        out = StringIO()
        if entries:
            w = csv.DictWriter(out, fieldnames=entries[0].keys())
            w.writeheader()
            w.writerows(entries)
        return {"data": out.getvalue(), "filename": f"{symbol}_signals.csv"}
    return {"data": entries, "filename": f"{symbol}_signals.json"}


@app.get("/api/portfolio")
def portfolio_metrics(symbols: list[str]):
    """Aggregate metrics across a portfolio."""
    from . import metrics
    return metrics.portfolio_metrics(symbols)
