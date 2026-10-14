# Local Testing Guide - Market Predictor

## ✅ Current Status

Your app is now running locally at: **http://localhost:8000**

### What's Working:
- ✅ Application server is running
- ✅ Database is connected (SQLite)
- ✅ All dependencies are installed
- ✅ Redis graceful degradation (works without Redis)
- ✅ All API endpoints are accessible

### What's Not Working (Expected):
- ⚠️ Redis: Not connected (running in WSL, app on Windows - different environments)
- ⚠️ Polygon API: Missing API key (prices will be slow/unavailable)
- ⚠️ CoinGecko API: Works but may have rate limits

---

## 🚀 How to Test Locally

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "Database connected",
  "cache": "Redis disabled",
  "timestamp": "2026-10-10T17:20:13.734695+00:00"
}
```

### 2. Test Live Prices (Will be slow without API keys)
```bash
curl "http://localhost:8000/api/assets/live-prices?limit=5"
```

**Note**: This will be slow (30-60 seconds) because:
- No Polygon API key (prices fetched from Yahoo Finance instead)
- No Redis caching (running without Redis)
- First request always slower than subsequent requests

### 3. Test Signal Analysis
```bash
curl http://localhost:8000/api/signal/AAPL
```

### 4. Test Material Analysis
```bash
curl -X POST http://localhost:8000/api/material \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","text":"Apple reported strong earnings beat","combine":true}'
```

### 5. Test Chart Data
```bash
curl http://localhost:8000/api/chart/AAPL
```

---

## 🔧 Redis Testing (Optional)

### Current Issue
Redis is installed in WSL (Linux) but your Python app runs on Windows. They can't connect to each other.

### Solution 1: Use Railway for Redis Testing (Recommended)
1. Deploy to Railway (where Redis is automatically configured)
2. Test on Railway's preview URL
3. No local Redis needed

### Solution 2: Install Redis on Windows (Advanced)
Download Redis for Windows from:
- https://github.com/microsoftarchive/redis/releases
- Or use Docker Desktop to run Redis container

### Solution 3: Accept No Redis (Simplest)
- App works without Redis (just slower)
- Production on Railway will have Redis
- Accept slower local performance

---

## 🔑 API Keys (Optional)

To get faster prices, add API keys to your `.env` file:

### Polygon API Key (Stocks)
1. Go to https://polygon.io/
2. Sign up for free account
3. Get API key
4. Add to `.env`:
   ```
   POLYGON_API_KEY=your_polygon_api_key_here
   ```

### CoinGecko API Key (Crypto)
1. Go to https://www.coingecko.com/en/api
2. Sign up for free account
3. Get API key
4. Add to `.env`:
   ```
   COINGECKO_API_KEY=your_coingecko_api_key_here
   ```

---

## 📊 Testing All Features

### Test Categories:
```bash
# Get asset categories
curl http://localhost:8000/api/assets/categories
```

### Test Search:
```bash
# Search for assets
curl "http://localhost:8000/api/assets/search?q=AAPL"
```

### Test Predictions:
```bash
# Get AI predictions
curl "http://localhost:8000/api/predictions/AAPL?timeframe=1d"
```

### Test Backtesting:
```bash
# Run backtest
curl -X POST http://localhost:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","strategy_name":"momentum","initial_capital":100000}'
```

### Test News:
```bash
# Get news with sentiment
curl "http://localhost:8000/api/news/AAPL?max_articles=5"
```

---

## 🌐 Open in Browser

Open these URLs in your browser:

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **ReDoc**: http://localhost:8000/redoc

The API docs page (http://localhost:8000/docs) provides an interactive UI to test all endpoints!

---

## 🎯 Recommended Testing Workflow

### 1. Start with API Docs
1. Open http://localhost:8000/docs in your browser
2. This is the FastAPI automatic documentation
3. Try each endpoint from the UI
4. See real-time responses

### 2. Test Core Features
1. Health check - verify app is running
2. Get assets - test data retrieval
3. Get signal - test ML predictions
4. Get chart - test chart data

### 3. Test Advanced Features
1. Backtesting - test strategy analysis
2. News sentiment - test NLP analysis
3. Risk calculation - test risk metrics
4. Portfolio - test portfolio metrics

---

## 📝 Important Notes

### Performance Expectations
- **Local without Redis**: 30-60 seconds per request (slow)
- **Local with Redis**: 100-200ms per request (fast)
- **Production on Railway**: 50-100ms per request (fastest)

### Why Local is Slow
1. No Redis caching (Redis in WSL, app on Windows)
2. No API keys (using free tier APIs with rate limits)
3. SQLite database (slower than PostgreSQL)
4. Network latency to external APIs

### Production on Railway
1. ✅ Redis automatically configured
2. ✅ PostgreSQL database
3. ✅ Can add API keys
4. ✅ Much faster performance

---

## 🚀 Next Steps

### Option 1: Test on Railway (Recommended)
1. Push code to GitHub
2. Connect to Railway
3. Deploy automatically
4. Test on Railway URL (much faster)

### Option 2: Improve Local Testing
1. Add API keys to `.env`
2. Install Redis on Windows (optional)
3. Use Docker for Redis (optional)
4. Accept slower local performance

### Option 3: Use Interactive API Docs
1. Open http://localhost:8000/docs
2. Try all endpoints from the UI
3. See responses in real-time
4. No curl commands needed

---

## ✅ Summary

**Your app is running locally!** 🎉

- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

**Performance**: Local is slow (expected), Railway will be fast.

**Testing**: Use the interactive API docs at http://localhost:8000/docs for easiest testing.

**Production**: Deploy to Railway for full performance with Redis and PostgreSQL.
