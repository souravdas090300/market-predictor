# Deployment Guide - Vercel + Railway (Docker-less)

This guide explains how to deploy your Market Predictor application to production using **Vercel** (frontend) and **Railway** (backend) without Docker, using Railway's native Nixpacks build system.

## Architecture

- **Frontend**: Next.js 16 deployed on Vercel
- **Backend**: Python FastAPI deployed on Railway (using Nixpacks, no Docker)
- **Database**: SQLite (local file storage) + Redis (Railway for rate limiting)
- **Storage**: Railway provides persistent storage for the backend

## Prerequisites

1. GitHub account with your code pushed to a repository
2. Vercel account (free)
3. Railway account (free tier with $5 credits)

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your market-predictor repository
4. Railway will detect the Python project (requirements.txt at root) and suggest settings

### 1.2 Configure Backend Service

1. In your Railway project, the service will be created automatically
2. Click on the service to configure it
3. Railway's Nixpacks will automatically detect Python from `requirements.txt` at the root
4. Configure the service settings:
   - **Build Command**: `cd market-predictor && pip install -r requirements.txt`
   - **Start Command**: `cd market-predictor && uvicorn app.api:app --host 0.0.0.0 --port $PORT`
   - **Health Check**: `/api/health`

**Note**: Your repository structure has the application code in a `market-predictor/` subdirectory. The `requirements.txt` and `setup.py` at the root help Railway detect the Python project, while commands navigate into the subdirectory.

### 1.3 Add Redis Service

1. In your Railway project, click "New Service"
2. Select "Database" → "Add Redis"
3. Railway will provide a Redis connection URL

### 1.4 Set Environment Variables

Go to your backend service → "Variables" tab and add these variables:

```bash
# Environment
ENV=production

# Security
SECRET_KEY=your-generated-secret-key-here
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"

# Redis (Railway provides this automatically)
REDIS_URL=${{REDIS.URL}}

# Security Settings
ALLOW_PRIVATE_URLS=false
ENABLE_RATE_LIMITING=true
ENABLE_AUTHENTICATION=true

# API Settings
API_CACHE_SECONDS=300
BULK_LIMIT=50

# File Upload Limits
MAX_UPLOAD_BYTES=5000000

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_LEVEL=INFO

# CORS Settings (will be updated after Vercel deployment)
CORS_ORIGINS=https://*.vercel.app,https://*.railway.app
ADMIN_CORS_ORIGINS=https://*.vercel.app,https://*.railway.app

# Feature Flags
ENABLE_DEBUG_MODE=false
ENABLE_PROFILING=false
ENABLE_TESTING_MODE=false
```

**Note**: Railway automatically provides `REDIS_URL` when you add a Redis service to your project.

### 1.5 Deploy Backend

1. Click "Deploy" in Railway
2. Wait for the build to complete
3. Railway will provide a URL like: `https://your-backend.railway.app`
4. Copy this URL for the next step

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project" → "Import your Git repository"
3. Select your market-predictor repository
4. Configure the project settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `market-predictor/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

**Note**: Vercel needs to point to the `market-predictor/frontend` subdirectory since that's where the Next.js app is located.

### 2.2 Set Environment Variables

In your Vercel project → "Settings" → "Environment Variables", add:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

Replace `your-backend.railway.app` with your actual Railway backend URL.

### 2.3 Deploy Frontend

1. Click "Deploy" in Vercel
2. Wait for the build to complete
3. Vercel will provide a URL like: `https://your-frontend.vercel.app`

## Step 3: Update CORS Configuration

Now that you have both URLs, update the Railway backend CORS settings:

1. Go to Railway → Backend service → "Variables"
2. Update `CORS_ORIGINS` to include your specific Vercel domain:
   ```bash
   CORS_ORIGINS=https://your-frontend.vercel.app,https://*.vercel.app,https://*.railway.app
   ```
3. Redeploy the backend service

## Step 4: Configure Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Vercel project → "Settings" → "Domains"
2. Add your custom domain (e.g., `market-predictor.com`)
3. Follow Vercel's DNS configuration instructions

### Railway Custom Domain

1. Go to Railway project → Backend service → "Settings" → "Networking"
2. Add your custom domain for the API (e.g., `api.market-predictor.com`)
3. Update Vercel environment variable: `NEXT_PUBLIC_API_URL=https://api.market-predictor.com`

## Step 5: Production Database Setup

### SQLite Persistence

Railway provides a persistent filesystem. Your SQLite database (`data/signals.db`) will be preserved between deployments.

### Redis for Sessions & Rate Limiting

The Railway Redis service handles:
- Session storage
- Rate limiting
- Caching

## Step 6: Create Admin User

After deployment, create your first admin user:

1. Access your Railway backend logs
2. Run the admin creation script locally or add a script endpoint
3. Or use the admin API endpoint once authenticated

## Step 7: Monitor & Maintain

### Railway Monitoring

- **Metrics**: Railway provides CPU, memory, and network metrics
- **Logs**: View real-time logs in the Railway dashboard
- **Deployments**: Automatic deployments on git push

### Vercel Monitoring

- **Analytics**: View visitor analytics and performance
- **Logs**: Access build and runtime logs
- **Deployments**: Preview deployments and production history

## Step 8: Set Up CI/CD Pipeline (Optional but Recommended)

For automated deployment, set up the GitHub Actions CI/CD pipeline:

1. **Add GitHub Secrets**:
   - `RAILWAY_TOKEN`: Get from Railway account settings
   - `VERCEL_TOKEN`: Get from Vercel account settings

2. **Configure Workflows**:
   - `.github/workflows/test.yml` - Runs tests on every push
   - `.github/workflows/deploy.yml` - Deploys on main branch push

3. **Automatic Deployment**:
   - Push to main/master triggers deployment
   - Tests run first, then deployment
   - Manual trigger available via GitHub UI

See [CI_CD_SETUP.md](CI_CD_SETUP.md) for detailed CI/CD configuration.

## Troubleshooting

### Backend Issues

**Problem**: Backend fails to start
- **Solution**: Check Railway logs for build errors, ensure all dependencies are in requirements.txt

**Problem**: CORS errors
- **Solution**: Verify CORS_ORIGINS includes your Vercel domain, redeploy backend

**Problem**: Redis connection fails
- **Solution**: Ensure REDIS_URL is set correctly and Redis service is running

### Frontend Issues

**Problem**: API calls fail
- **Solution**: Verify NEXT_PUBLIC_API_URL is correct and backend is accessible

**Problem**: Build fails
- **Solution**: Check Vercel build logs, ensure all dependencies are in package.json

## Cost Estimate

### Free Tier Usage

**Railway**:
- $5 free credits/month
- After credits: ~$5-10/month for small applications
- Includes: Backend service, Redis, storage

**Vercel**:
- Free for hobby projects
- 100GB bandwidth/month
- Unlimited deployments
- After limits: ~$20/month for Pro plan

**Total Estimated Cost**: $0-15/month depending on usage

## Scaling Considerations

When your application grows:

1. **Backend**: Add more workers in Railway
2. **Database**: Migrate from SQLite to PostgreSQL (Railway offers this)
3. **CDN**: Vercel automatically provides CDN for frontend
4. **Monitoring**: Add Sentry for error tracking
5. **Analytics**: Add Google Analytics or similar

## Security Checklist

- [ ] Generate strong SECRET_KEY for production
- [ ] Enable rate limiting
- [ ] Use HTTPS (both platforms provide this)
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity
- [ ] Regularly backup database
- [ ] Use environment variables for secrets
- [ ] Enable authentication
- [ ] Review CORS settings regularly

## Support & Resources

- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Railway Docs**: [railway.app/docs](https://railway.app/docs)
- **Next.js Deployment**: [nextjs.org/docs/deployment](https://nextjs.org/docs/deployment)
- **FastAPI Deployment**: [fastapi.tiangolo.com/deployment](https://fastapi.tiangolo.com/deployment)

## Next Steps

1. Test your deployed application thoroughly
2. Set up monitoring and alerting
3. Configure backup strategy for database
4. Add custom domains for professional appearance
5. Set up CI/CD pipeline for automated testing
6. Consider adding analytics and error tracking