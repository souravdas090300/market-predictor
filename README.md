#
 Market lean: auto + material signals across all markets

Estimates the chance that a share, crypto, forex pair or commodity closes higher in 5 trading days, and
labels it bullish, bearish or neutral. It has two modes that you can use together or separately.

## Quick start

```bash
pip install -r requirements.txt
pytest -q
python -m scripts.cli AAPL BTC-USD GC=F EURUSD=X    # quick check
```

## Running the application

### Development Mode
```bash
python scripts/run_dev.py
```
This starts the application with:
- Debug mode enabled
- Relaxed security settings
- Verbose logging
- Auto-reload on code changes
- Access at http://localhost:8000

### Production Mode
```bash
python scripts/run_prod.py
```
This starts the application with:
- Strict security settings
- Multiple workers for performance
- Standard logging
- No auto-reload
- Access at http://localhost:8000

See [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md) for detailed environment configuration.

## Two modes

**Automatic mode** needs nothing from you. It combines:
1. Technical indicators: RSI, MACD, moving averages, Bollinger, ATR, volatility, yearly range
2. Candlestick patterns: hammer, shooting star, engulfing, morning/evening star, harami, three soldiers/crows,
   marubozu, doji, piercing line, dark cloud (context-aware)
3. ML model: gradient boosting on those features, calibrated on out-of-sample predictions so it doesn't lie
4. News tone: recent headlines (Google News RSS) scored for sentiment

**Material mode** lets you paste your own news, report summaries or notes about an asset. Each asset's panel
suggests what is worth pasting:
- **Shares**: earnings release, analyst upgrades, market-wide news on rates or jobs
- **Crypto**: ETF flows, regulation, staking or halving events, macro news on rates or the dollar
- **Forex**: central bank statements, CPI/jobs/GDP data. Write from the first currency's view.
- **Commodities**: OPEC decisions, inventory reports, China data, supply disruptions, dollar and rate moves

You can read the material on its own, or combine it with the automatic signal: your text can move the
probability by at most +/-0.15 (`MATERIAL_WEIGHT` in `config.py`). Wording is understood per market.

## Markets

Out of the box: shares (AAPL, MSFT, NVDA, S&P 500), crypto (BTC, ETH), forex (EUR/USD, GBP/USD)
and commodities (gold, silver, WTI oil, natural gas, copper). Any Yahoo Finance symbol works:
- `symbol` or `SYMBOL` = share (e.g. TSLA, NVDA, ^GSPC)
- `symbol-USD` = crypto (e.g. SOL-USD, ETH-USD)
- `symbol=X` = forex pair (e.g. EURUSD=X, GBPUSD=X)
- `symbol=F` = commodity futures (e.g. GC=F for gold, CL=F for oil)

## Advanced features

### Dashboard
- **Filter by market**: All, Shares, Crypto, Forex, Commodities
- **Material panel**: paste text, URL (fetch & read), or upload a PDF or CSV
- **Candlestick chart**: 60-day price action with pattern markers
- **Indicators**: RSI, MACD, moving average distance, volatility
- **Track record**: out-of-sample accuracy compared to a naive baseline

### API endpoints
- `GET /api/watchlist` — list of tracked symbols
- `GET /api/signal/{symbol}` — automatic analysis (prices, candles, ML, news)
- `POST /api/material` — read text material on its own or combined with auto signal
- `POST /api/material-from-url` — fetch and read a web page as material
- `POST /api/material-from-file` — upload and read a PDF or CSV as material
- `GET /api/signal/{symbol}/history` — logged signals and metrics for a symbol
- `POST /api/bulk` — analyse up to 50 symbols in one request
- `GET /api/portfolio` — aggregate metrics across multiple symbols
- `GET /api/export/{symbol}` — download signal history as CSV or JSON
- `GET /api/classes` — market types and material hints per class

### CLI
```
python -m scripts.cli AAPL BTC-USD EURUSD=X    # auto signals
python -m scripts.cli history --symbol AAPL    # signal history
python -m scripts.cli portfolio AAPL,BTC-USD   # portfolio metrics
```

### Signal history & logging
Every signal is logged to `signals.db` (JSON lines file). See recent history with the dashboard or API.
Entries are kept for 90 days; `history.purge_old()` removes older entries.

### Risk metrics
`metrics.py` computes aggregate statistics across signals:
- Average probability across all signals
- Count of bullish, bearish, neutral leans
- How many high-confidence calls have been made
- Portfolio-level aggregates

## How honest is it?

- **No lookahead**: Features only use data up to each day (there's a test for this).
- **No training leakage**: Evaluation is walk-forward with a gap, so no training row overlaps a test row.
- **Calibrated**: The model uses Platt scaling to map out-of-sample predictions to actual frequencies, so a model with no edge shows about 50%, not 85%.
- **Track record shown**: The dashboard shows out-of-sample accuracy next to the "always guess the common outcome" baseline. If those are close, treat the signal as noise.
- **Expected accuracy**: 51–58% is normal for daily direction prediction. This can still be useful if you combine it with other signals.

## What material does and doesn't do

Material is scored on its **wording**, not checked for truth, and it has no back-tested track record like the model.
- **Few clear sentences**: if only a few carry a signal, the result is pulled toward zero and has little effect.
- **Market-aware**: "output cut" and "inventory draw" read as bullish for oil; "inflation" is not counted against
  commodities.
- **One person's take**: material wording is weighted at 15 points max, so it nudges but never dominates the auto signal.

## Wording understood per market

### Shares
Positive: surge, beat, record high, upgrade, growth, profit, strong, boost
Negative: fall, miss, downgrade, weakness, loss, fear, crash, recession, lawsuit, tariff

### Crypto
Shares + adoption, accumulation, staking (positive); delisting, liquidation, exploit, rug (negative)

### Forex & commodities
Commodity-specific: supply cut, inventory draw, OPEC cut (positive); supply glut, inventory build, weak demand (negative)

Forex: write from the first currency's view, e.g. "euro weakens after weak German data"

### All
Multi-word phrases are matched first: "rate cut" (positive), "rate hike" (negative), "raises guidance" (positive)

## Notes

- **Continuous vs contract futures**: gold and oil come from continuous futures, so contract rolls can show up as
  small gaps in the candles.
- **News**: free news sources don't provide history, so headlines only adjust today's probability. To train on
  historical sentiment, log daily scores for a few months and add them to `features.py`.
- **No FinBERT by default**: the app uses a small lexicon (no downloads, works offline). Install `transformers`
  and `torch`, then run with `USE_FINBERT=1` for better headline scoring.

## Deployment

### Production Deployment (Vercel + Railway)

The recommended production setup uses **Vercel** for the Next.js frontend and **Railway** for the Python FastAPI backend.

**Quick Start:**
- See [QUICK_START.md](QUICK_START.md) for a 5-minute deployment guide
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions
- See [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) for repository structure information
- Run `python market-predictor/scripts/deploy.py` for deployment preparation checklist

**Architecture:**
- Frontend: Next.js 16 on Vercel (free tier)
- Backend: Python FastAPI on Railway (free tier with credits)
- Database: SQLite (persistent storage on Railway)
- Caching: Redis on Railway for rate limiting and sessions

**Manual Deployment:**
```bash
# Generate production secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Follow the deployment guide for platform-specific setup
```

### Local Development
```bash
# Development mode
python scripts/run_dev.py

# Production mode locally
python scripts/run_prod.py
```

### Docker
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development
1. Edit `app/core/config.py` to change the watchlist, weights or date range
2. Run `pytest -q` after changes
3. Use `python -m scripts.cli` for quick testing
4. The API caches responses for 5 minutes; use `?refresh=true` to bust the cache

## What's next?

- Log outcomes and measure live accuracy against historical signals
- Add macro indicators (VIX, DXY, long-term rates) as market-wide context
- Train FinBERT on your own market data for better sentiment
- Port to Next.js for auth, user watchlists and alerts on Vercel with API on Railway
- Add correlation analysis to compare how assets move together
