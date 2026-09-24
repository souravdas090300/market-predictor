# Repository Structure

This repository has a flattened structure for simplified deployment:

```
market-predictor/                    # Repository root
├── .github/                         # GitHub workflows
│   └── workflows/
│       ├── deploy.yml              # CI/CD deployment workflow
│       └── test.yml                # Testing workflow
├── app/                            # Backend application
│   ├── api/                        # FastAPI endpoints
│   ├── core/                       # Core configuration
│   ├── services/                   # Business logic
│   ├── security/                   # Security utilities
│   └── auth/                       # Authentication
├── frontend/                       # Next.js frontend
│   ├── src/                        # React components
│   ├── public/                     # Static assets
│   ├── package.json                # Frontend dependencies
│   └── vercel.json                 # Vercel configuration
├── data/                           # Database files
├── logs/                           # Application logs
├── models/                         # ML models
├── static/                         # Static files
├── tests/                          # Test files
├── scripts/                        # Utility scripts
├── docs/                           # Documentation
├── Dockerfile                      # Container configuration
├── .dockerignore                   # Docker ignore patterns
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Python project configuration
├── setup.py                        # Python package setup
├── railway.json                    # Railway configuration
├── railway.toml                    # Railway TOML configuration
├── nixpacks.toml                  # Railway build config
├── Procfile                        # Process definition
├── start.sh                        # Startup script
├── .env.example                    # Environment template
├── .env.production.template        # Production env template
├── frontend.env.production.template # Frontend env template
├── DEPLOYMENT.md                   # Deployment guide
├── QUICK_START.md                  # Quick deployment guide
├── CI_CD_SETUP.md                  # CI/CD setup guide
└── README.md                       # Main documentation
```

## Deployment Considerations

### Railway (Backend)
- Dockerfile at root for container-based deployment
- `requirements.txt` and `pyproject.toml` for Python dependency management
- `railway.json` and `railway.toml` for Railway-specific configuration
- Build runs from repository root using Docker
- Environment variables are set at the service level

### Vercel (Frontend)
- Must be configured to use `frontend` as root directory
- The `vercel.json` file is inside the frontend directory
- Environment variables are set at the project level
- Next.js 16 with App Router and TypeScript

### GitHub Actions
- Workflow runs from repository root
- Tests run in repository root
- Frontend build runs in `frontend/` directory
- Backend deployment uses Docker configuration

## Why This Structure?

This flattened structure was adopted because:
1. Simplifies deployment configuration across platforms
2. Eliminates subdirectory navigation issues
3. Better alignment with modern deployment platforms
4. Reduces configuration complexity
5. Easier to maintain and debug deployment issues