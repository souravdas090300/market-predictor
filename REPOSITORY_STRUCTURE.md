# Repository Structure

This repository has a specific structure that requires special handling for deployment:

```
market-predictor/                    # Repository root
├── .github/                         # GitHub workflows
│   └── workflows/
│       └── deploy.yml              # CI/CD deployment workflow
├── market-predictor/               # Application code directory
│   ├── app/                        # Backend application
│   │   ├── api/                    # FastAPI endpoints
│   │   ├── core/                   # Core configuration
│   │   ├── services/               # Business logic
│   │   ├── security/               # Security utilities
│   │   └── auth/                   # Authentication
│   ├── frontend/                   # Next.js frontend
│   │   ├── src/                    # React components
│   │   ├── public/                 # Static assets
│   │   ├── package.json            # Frontend dependencies
│   │   └── vercel.json             # Vercel configuration
│   ├── data/                       # Database files
│   ├── logs/                       # Application logs
│   ├── models/                     # ML models
│   ├── static/                     # Static files
│   ├── tests/                      # Test files
│   ├── scripts/                    # Utility scripts
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment template
├── Dockerfile                      # Container configuration (moved to root)
├── .dockerignore                   # Docker ignore patterns (moved to root)
├── railway.json                    # Railway configuration (moved to root)
├── nixpacks.toml                  # Railway build config (moved to root)
├── .env.production.template        # Production env template (moved to root)
├── frontend.env.production.template # Frontend env template (moved to root)
├── DEPLOYMENT.md                   # Deployment guide (moved to root)
├── QUICK_START.md                  # Quick deployment guide (moved to root)
└── README.md                       # Main documentation
```

## Deployment Considerations

### Railway (Backend)
- Configuration files are at the repository root
- Build/start commands navigate into `market-predictor/` directory
- Environment variables are set at the service level
- The Railway build system automatically handles the subdirectory structure

### Vercel (Frontend)
- Must be configured to use `market-predictor/frontend` as root directory
- The `vercel.json` file is inside the frontend directory
- Environment variables are set at the project level

### GitHub Actions
- Workflow runs from repository root
- All commands navigate into appropriate subdirectories
- Tests run in `market-predictor/` directory
- Frontend build runs in `market-predictor/frontend/` directory

## Why This Structure?

This structure was adopted because:
1. The original codebase was developed in a subdirectory
2. Moving everything to the root would require significant refactoring
3. Deployment platforms support subdirectory configurations
4. This allows separation of deployment configs from application code

## Migration Notes

If you want to flatten this structure in the future:
1. Move all content from `market-predictor/` to repository root
2. Update all import paths in Python code
3. Update all file references in configuration files
4. Update deployment configurations to remove directory navigation
5. Update GitHub Actions workflow paths