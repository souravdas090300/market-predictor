# CI/CD Pipeline Setup Guide

This guide explains how to set up and use the GitHub Actions CI/CD pipeline for automatic deployment to Railway and Vercel.

## Pipeline Overview

Your project has two GitHub Actions workflows:

### 1. Test Workflow (`.github/workflows/test.yml`)
- **Triggers**: Push to any branch, pull requests
- **Purpose**: Run tests and build frontend
- **No deployment**: Only tests code quality

### 2. Deploy Workflow (`.github/workflows/deploy.yml`)
- **Triggers**: Push to main/master branch, manual trigger
- **Purpose**: Deploy to Railway (backend) and Vercel (frontend)
- **Requirements**: Tests must pass first

## Prerequisites

1. **GitHub Repository**: Your code must be on GitHub
2. **Railway Account**: Backend deployment platform
3. **Vercel Account**: Frontend deployment platform
4. **GitHub Secrets**: Required API tokens

## Setting Up GitHub Secrets

### Railway Token

1. Go to [railway.app](https://railway.app) → Account Settings
2. Generate an API token
3. Go to your GitHub repository → Settings → Secrets and variables → Actions
4. Add new secret:
   - **Name**: `RAILWAY_TOKEN`
   - **Value**: Your Railway API token

### Vercel Token

1. Go to [vercel.com](https://vercel.com) → Account Settings → Tokens
2. Create a new token
3. Go to your GitHub repository → Settings → Secrets and variables → Actions
4. Add new secret:
   - **Name**: `VERCEL_TOKEN`
   - **Value**: Your Vercel API token

## Workflow Triggers

### Automatic Deployment
- **When**: Push to `main` or `master` branch
- **Process**: Tests → Railway deploy → Vercel deploy
- **Duration**: ~5-10 minutes

### Manual Deployment
- **When**: Use GitHub Actions "Run workflow" button
- **Process**: Same as automatic
- **Use case**: Deploy without pushing new code

### Pull Request Testing
- **When**: Open PR to main/master
- **Process**: Only tests, no deployment
- **Use case**: Test before merging

## Pipeline Stages

### Stage 1: Test
```yaml
- Setup Python 3.12
- Install backend dependencies
- Run pytest tests
- Setup Node.js 20
- Install frontend dependencies
- Build Next.js frontend
```

### Stage 2: Deploy Railway (Backend)
```yaml
- Install Railway CLI
- Login with token
- Deploy using Nixpacks (Docker-less)
- Railway auto-detects Python from requirements.txt
```

### Stage 3: Deploy Vercel (Frontend)
```yaml
- Install Vercel CLI
- Pull environment configuration
- Build project artifacts
- Deploy to production
```

## Deployment Order

The pipeline deploys in this order:
1. **Backend first** (Railway) - API must be available
2. **Frontend second** (Vercel) - Can connect to new backend
3. **CORS update** - Manual step after both deployments

## Manual Deployment

### Via GitHub UI
1. Go to repository → Actions tab
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Select branch and run

### Via CLI
```bash
# Trigger workflow manually
gh workflow run deploy.yml
```

## Monitoring Deployments

### View Deployment Status
1. Go to repository → Actions tab
2. Click on the latest workflow run
3. View real-time logs for each job

### Railway Deployment
- Check Railway dashboard for build logs
- Monitor service health after deployment
- Test API endpoints

### Vercel Deployment
- Check Vercel dashboard for deployment logs
- Preview deployment before production
- Monitor build times and errors

## Troubleshooting

### Common Issues

**Secrets Not Found**
```
Error: RAILWAY_TOKEN not found
```
**Solution**: Add the missing secret in GitHub repository settings

**Tests Failing**
```
Error: pytest failed
```
**Solution**: Fix failing tests locally before pushing

**Railway Build Fails**
```
Error: railway up failed
```
**Solution**: Check Railway logs, verify requirements.txt at root

**Vercel Build Fails**
```
Error: vercel build failed
```
**Solution**: Check Vercel logs, verify frontend builds locally

### Debug Mode

To debug deployment issues:
1. Enable debug logging in workflow
2. Add `--debug` flags to CLI commands
3. Check individual service logs

## Environment Variables

The pipeline uses these environment variables:

### Backend (Railway)
- `ENV=production`
- `SECRET_KEY` (set in Railway)
- `REDIS_URL` (provided by Railway)
- `CORS_ORIGINS` (set in Railway)

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` (set in Vercel)
- Points to Railway backend URL

## Security Best Practices

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for sensitive data
3. **Rotate tokens** regularly
4. **Limit token permissions** to minimum required
5. **Monitor access logs** for unusual activity

## Customization

### Change Branch Names
```yaml
on:
  push:
    branches:
      - main
      - production  # Add your branch
```

### Add More Tests
```yaml
- name: Run linting
  run: |
    cd market-predictor
    pip install flake8
    flake8 app/
```

### Add Deployment Notifications
```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Performance Optimization

### Parallel Jobs
```yaml
jobs:
  test-backend:
    # Backend tests
  test-frontend:
    # Frontend tests
  deploy:
    needs: [test-backend, test-frontend]
    # Deploy after both tests pass
```

### Caching Dependencies
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Rollback Procedures

### Manual Rollback
1. Go to Railway dashboard → Service → Deployments
2. Select previous deployment → Redeploy
3. Go to Vercel dashboard → Deployments
4. Select previous deployment → Promote to production

### Git Rollback
```bash
# Revert to previous commit
git revert HEAD
git push origin main
# This will trigger automatic rollback deployment
```

## Cost Monitoring

### Railway Costs
- Monitor usage in Railway dashboard
- Set spending limits
- Review free tier usage

### Vercel Costs
- Monitor bandwidth usage
- Check build minutes
- Review Pro plan requirements

## Next Steps

1. **Set up secrets** in GitHub repository
2. **Test locally** before pushing
3. **Monitor first deployment** carefully
4. **Set up alerts** for deployment failures
5. **Document custom procedures** for your team

## Support

- **GitHub Actions Docs**: [docs.github.com/actions](https://docs.github.com/actions)
- **Railway CLI Docs**: [railway.app/docs/cli](https://railway.app/docs/cli)
- **Vercel CLI Docs**: [vercel.com/docs/cli](https://vercel.com/docs/cli)

## Emergency Contacts

If CI/CD pipeline fails:
1. Check workflow logs in GitHub Actions
2. Check service logs in Railway/Vercel dashboards
3. Deploy manually using platform dashboards
4. Contact platform support if needed