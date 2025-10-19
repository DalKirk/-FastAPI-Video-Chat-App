# FastAPI Video Chat - Project Structure

## ?? Project Organization

```
My_FastAPI_Python/
??? backend/                      # Backend modules
?   ??? dynamic_cors_middleware.py
??? database/                     # Database layer
?   ??? interface.py
??? docs/                         # Documentation
?   ??? API_DOCUMENTATION.md
?   ??? BEFORE_AFTER_COMPARISON.md
?   ??? IMPROVEMENTS_SUMMARY.md
?   ??? QUICK_START_GUIDE.md
??? middleware/                   # Middleware components
?   ??? rate_limit.py
??? tests/                        # Test suite
?   ??? conftest.py
?   ??? smoke_ws.py
?   ??? test_api.py
?   ??? test_comprehensive.py
??? tools/                        # Development tools
?   ??? run_smoke.py
?   ??? test_api_manual.py
?   ??? ws_network_smoke.py
??? utils/                        # Utility modules
?   ??? cache.py
?   ??? logging_config.py
?   ??? metrics.py
?   ??? validation.py
??? .env.example                  # Environment variables template
??? .gitignore                    # Git ignore patterns
??? config.py                     # Configuration management
??? deploy.ps1                    # Windows deployment script
??? deploy.sh                     # Unix deployment script
??? DEPLOYMENT_GUIDE.md           # Deployment instructions
??? Dockerfile                    # Docker configuration
??? exceptions.py                 # Custom exceptions
??? LICENSE                       # Project license
??? main.py                       # Main application entry point
??? Procfile                      # Railway deployment config
??? PROJECT_STATUS.md             # Current project status
??? README.md                     # Main documentation
??? redeploy.ps1                  # Quick redeploy script
??? requirements.txt              # Python dependencies
??? runtime.txt                   # Python version for deployment
??? setup_vercel_env.ps1          # Vercel environment setup
??? start.sh                      # Start script for deployment
??? vercel.json                   # Vercel configuration
```

## ??? Directory Descriptions

### `/backend/`
Custom middleware and backend-specific utilities.
- **dynamic_cors_middleware.py**: CORS middleware with whitelist validation

### `/database/`
Database abstraction layer and interfaces.
- **interface.py**: Database interface for room and user management

### `/docs/`
Project documentation and guides.
- **API_DOCUMENTATION.md**: Complete API reference
- **BEFORE_AFTER_COMPARISON.md**: Code improvements comparison
- **IMPROVEMENTS_SUMMARY.md**: Summary of optimizations
- **QUICK_START_GUIDE.md**: Getting started guide

### `/middleware/`
HTTP middleware components.
- **rate_limit.py**: Rate limiting middleware for API protection

### `/tests/`
Testing suite with comprehensive test coverage.
- **conftest.py**: pytest configuration and fixtures
- **smoke_ws.py**: WebSocket smoke tests
- **test_api.py**: API endpoint tests
- **test_comprehensive.py**: Comprehensive integration tests

### `/tools/`
Development and testing tools.
- **run_smoke.py**: Smoke test runner
- **test_api_manual.py**: Manual API testing tool
- **ws_network_smoke.py**: WebSocket network testing

### `/utils/`
Utility modules for common functionality.
- **cache.py**: Caching utilities
- **logging_config.py**: Logging configuration
- **metrics.py**: Performance metrics
- **validation.py**: Input validation utilities

## ?? Core Files

### Application Files
- **main.py**: Main FastAPI application with WebSocket and REST endpoints
- **config.py**: Environment configuration and settings
- **exceptions.py**: Custom exception classes

### Deployment Files
- **Dockerfile**: Container configuration
- **Procfile**: Railway/Heroku deployment
- **vercel.json**: Vercel deployment configuration
- **runtime.txt**: Python runtime version
- **start.sh**: Application startup script
- **requirements.txt**: Python package dependencies

### Deployment Scripts
- **deploy.ps1** / **deploy.sh**: Initial deployment scripts
- **redeploy.ps1**: Quick redeploy script for Railway and Vercel
- **setup_vercel_env.ps1**: Vercel environment variable setup

## ?? Documentation Files

- **README.md**: Main project documentation
- **PROJECT_STATUS.md**: Current implementation status
- **DEPLOYMENT_GUIDE.md**: Deployment instructions
- **LICENSE**: Project license information

## ?? Clean Project

This project has been cleaned of:
- ? Redundant documentation files
- ? Obsolete test files in root
- ? Unused deployment status files
- ? Duplicate main files
- ? Temporary scripts
- ? Binary executables
- ? Python cache files (`__pycache__`)

## ?? Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload

# Run tests
pytest

# Deploy to Railway
railway up

# Deploy to Vercel (frontend)
vercel --prod
```

## ?? Environment Variables

See `.env.example` for required environment variables.

## ?? Contributing

1. Keep the project structure organized
2. Place tests in `/tests/` directory
3. Document new features in `/docs/`
4. Update `requirements.txt` for new dependencies
5. Follow the existing code style
