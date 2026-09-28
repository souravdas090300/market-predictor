# 📈 Market Predictor Pro

AI-powered market prediction platform with advanced authentication, role-based access control, and comprehensive market analysis tools.

## 🚀 Features

### Market Prediction
- **Automatic Mode**: Combines technical indicators, candlestick patterns, ML models, and news sentiment
- **Material Mode**: Analyze your own news, reports, or notes about assets
- **Multi-Market Support**: Stocks, crypto, forex, and commodities
- **Real-time Analysis**: Live quotes, charts, and predictions
- **Advanced Analytics**: Backtesting, risk management, strategy optimization

### Authentication & User Management
- **User Registration & Login**: Secure authentication with JWT tokens
- **Role-Based Access Control**: Admin, user, and superuser roles
- **Admin Dashboard**: User management, system stats, configuration
- **API Key Management**: Generate and manage API keys
- **OAuth Integration**: Google OAuth support

### Advanced Features
- **Batch Predictions**: Run predictions for multiple assets
- **Sentiment Analysis**: News and social media sentiment
- **Risk Management**: Position sizing, VaR, stress testing
- **Portfolio Analysis**: Efficient frontier, rebalancing, tax-loss harvesting
- **Social Features**: Strategy sharing, leaderboards, following

## 🏗️ Architecture

### Frontend (Next.js 16)
- **Landing Page**: Professional marketing page with features and pricing
- **Authentication**: Login and signup pages with role-based routing
- **User Dashboard**: Personalized dashboard for regular users
- **Admin Dashboard**: Administrative interface with full system control
- **Deployment**: Vercel (free tier)

### Backend (FastAPI)
- **API Endpoints**: 50+ RESTful endpoints for market data and user management
- **Authentication**: JWT-based auth with role verification
- **Rate Limiting**: Configurable rate limits per endpoint
- **Security**: CORS, security headers, input sanitization
- **Deployment**: Railway (Nixpacks, no Docker required)

### Data Storage
- **User Data**: SQLite with JSON file storage
- **Signal History**: JSON lines database for 90-day retention
- **Cache**: Redis for rate limiting and session management

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/souravdas090300/market-predictor.git
cd market-predictor

# Install Python dependencies
pip install -r requirements.txt

# Run development server
python scripts/run_dev.py
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🔐 Authentication

### Default Credentials

**Admin User:**
- Username: `admin`
- Password: `admin12345`
- Role: `superuser`

**Demo User:**
- Username: `demo`
- Password: `demo12345`
- Role: `user`

### User Roles

| Role | Dashboard Access | Admin Access | API Access |
|------|------------------|--------------|------------|
| `user` | ✅ | ❌ | Public APIs |
| `admin` | ✅ | ✅ | Admin APIs |
| `superuser` | ✅ | ✅ | All APIs |

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns role)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/api-key` - Create API key
- `GET /api/auth/api-keys` - List API keys
- `DELETE /api/auth/api-key/{key_id}` - Revoke API key

### Market Data
- `GET /api/watchlist` - Get watchlist
- `GET /api/signal/{symbol}` - Get signal for symbol
- `GET /api/quote/{symbol}` - Get live quote
- `GET /api/quotes` - Get multiple quotes
- `GET /api/assets/all` - Get all assets
- `GET /api/predictions/assets` - Get assets list
- `GET /api/predictions/assets/{symbol}/predictions` - Get predictions

### Material Analysis
- `POST /api/material` - Analyze text material
- `POST /api/material-from-url` - Fetch and analyze URL
- `POST /api/material-from-file` - Upload and analyze file

### Admin (Superuser Required)
- `POST /api/admin/auth/login` - Admin login
- `GET /api/admin/users` - List all users
- `POST /api/admin/add-admin/{username}` - Add admin user
- `DELETE /api/admin/remove-admin/{username}` - Remove admin
- `PUT /api/admin/user/{username}/enable` - Enable user
- `PUT /api/admin/user/{username}/disable` - Disable user
- `GET /api/admin/stats` - System statistics

### Advanced Features
- `POST /api/backtest/run` - Run backtest
- `POST /api/sentiment/advanced` - Advanced sentiment analysis
- `POST /api/risk/calculate` - Calculate risk metrics
- `POST /api/strategy/optimize` - Optimize strategy
- `POST /api/portfolio/analyze` - Analyze portfolio

## 🎯 Frontend Routes

### Public Routes
- `/` - Landing page
- `/auth/login` - Login page
- `/auth/signup` - Registration page

### Protected Routes
- `/dashboard` - User dashboard (requires login)
- `/admin` - Admin dashboard (requires admin role)

## 🚀 Deployment

### Production Deployment (Vercel + Railway)

**Frontend (Vercel):**
```bash
cd frontend
npm run build
vercel deploy
```

**Backend (Railway):**
```bash
# Railway auto-deploys from GitHub
# Ensure railway.json is configured
railway up
```

### Environment Variables

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
NEXT_PUBLIC_APP_URL=https://your-vercel-app.vercel.app
```

**Backend (.env):**
```env
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
```

### Docker Deployment (Alternative)
```bash
docker build -t market-predictor .
docker run -p 8000:8000 market-predictor
```

## 🧪 Testing

### Backend Tests
```bash
pytest -q
```

### Manual Testing
```bash
# Test market prediction
python -m scripts.cli AAPL BTC-USD EURUSD=X

# Test signal history
python -m scripts.cli history --symbol AAPL

# Test portfolio metrics
python -m scripts.cli portfolio AAPL,BTC-USD
```

### API Testing
```bash
# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'

# Test market signal
curl http://localhost:8000/api/signal/AAPL
```

## 📊 Markets Supported

Out of the box: shares (AAPL, MSFT, NVDA, S&P 500), crypto (BTC, ETH), forex (EUR/USD, GBP/USD) and commodities (gold, silver, WTI oil, natural gas, copper).

Any Yahoo Finance symbol works:
- `symbol` or `SYMBOL` = share (e.g. TSLA, NVDA, ^GSPC)
- `symbol-USD` = crypto (e.g. SOL-USD, ETH-USD)
- `symbol=X` = forex pair (e.g. EURUSD=X, GBPUSD=X)
- `symbol=F` = commodity futures (e.g. GC=F for gold, CL=F for oil)

## 🔧 Configuration

Edit `app/core/config.py` to customize:
- Watchlist symbols
- Feature weights
- Date ranges
- API cache duration
- Rate limits
- CORS origins

## 📈 How It Works

### Automatic Mode
Combines:
1. **Technical Indicators**: RSI, MACD, moving averages, Bollinger, ATR, volatility
2. **Candlestick Patterns**: Hammer, shooting star, engulfing, morning/evening star, etc.
3. **ML Model**: Gradient boosting with Platt scaling for calibrated predictions
4. **News Sentiment**: Recent headlines scored for market sentiment

### Material Mode
Lets you analyze your own text material:
- **Shares**: Earnings releases, analyst upgrades, market news
- **Crypto**: ETF flows, regulation, staking events, macro news
- **Forex**: Central bank statements, economic data
- **Commodities**: OPEC decisions, inventory reports, supply disruptions

## 🛡️ Security

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Admin/user role separation
- **Rate Limiting**: Configurable per-endpoint limits
- **Input Sanitization**: All inputs validated and sanitized
- **CORS Protection**: Configurable CORS origins
- **Security Headers**: Standard security headers on all responses

## 📝 Development

### Backend Development
```bash
# Development mode with auto-reload
python scripts/run_dev.py

# Production mode locally
python scripts/run_prod.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Code Quality
```bash
# Run tests
pytest -q

# Linting (if configured)
flake8 app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review API endpoints
- Test with demo credentials
- Check logs for errors

## 🎯 What's Next

- [ ] Add more ML models for ensemble predictions
- [ ] Implement real-time WebSocket data streams
- [ ] Add mobile app support
- [ ] Enhance social features and community
- [ ] Add more brokers for trading integration
- [ ] Implement advanced order types
- [ ] Add paper trading mode

---

**Built with ❤️ using Next.js, FastAPI, and modern ML techniques**
