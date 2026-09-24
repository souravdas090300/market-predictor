# Quick Start Guide - Vercel + Railway Deployment

This is a condensed version of the full deployment guide. For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## 5-Minute Deployment Overview

### Prerequisites
- GitHub account with code pushed
- Railway account (free)
- Vercel account (free)

### Step 1: Deploy Backend to Railway (2 minutes)

1. Go to [railway.app](https://railway.app) → "New Project" → "Deploy from GitHub"
2. Select your repository
3. Add Redis service ("New Service" → "Database" → "Add Redis")
4. Set environment variables (see below)
5. Click "Deploy" and copy the backend URL

### Step 2: Deploy Frontend to Vercel (2 minutes)

1. Go to [vercel.com](https://vercel.com) → "Add New Project" → "Import Git Repository"
2. Select your repository
3. Set root directory: `market-predictor/frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-backend.railway.app`
5. Click "Deploy"

### Step 3: Update CORS (1 minute)

1. Go to Railway → Backend → Variables
2. Update `CORS_ORIGINS` to include your Vercel domain
3. Redeploy backend

## Essential Environment Variables

### Railway (Backend)
```bash
ENV=production
SECRET_KEY=your-generated-secret-key
REDIS_URL=${{REDIS.URL}}
CORS_ORIGINS=https://*.vercel.app,https://*.railway.app
ENABLE_RATE_LIMITING=true
ENABLE_AUTHENTICATION=true
```

### Vercel (Frontend)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## Generate Secret Key

Run this command to generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Verification

After deployment, test these endpoints:
- Backend health: `https://your-backend.railway.app/api/health`
- Frontend: `https://your-frontend.vercel.app`
- API test: `https://your-backend.railway.app/api/watchlist`

## Cost Estimate

- **Railway**: Free tier ($5 credits/month), then ~$5-10/month
- **Vercel**: Free for hobby projects, then ~$20/month for Pro
- **Total**: $0-15/month depending on usage

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend fails to start | Check Railway logs, verify requirements.txt |
| CORS errors | Update CORS_ORIGINS with actual Vercel domain |
| API calls fail | Verify NEXT_PUBLIC_API_URL is correct |
| Build fails | Check Vercel build logs, verify package.json |

## Next Steps

1. Read the full [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions
2. Run `python scripts/deploy.py` for deployment checklist
3. Configure custom domains for professional appearance
4. Set up monitoring and error tracking

## Support

- Railway Docs: [railway.app/docs](https://railway.app/docs)
- Vercel Docs: [vercel.com/docs](https://vercel.com/docs)
- Full Guide: [DEPLOYMENT.md](./DEPLOYMENT.md)