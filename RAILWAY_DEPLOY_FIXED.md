# Railway Deployment Instructions

## Quick Deploy Steps

### Option 1: Railway CLI (Recommended)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize and Deploy**:
   ```bash
   railway init
   railway up
   ```

### Option 2: Connect via GitHub

1. **Create a GitHub repository** (if you haven't already):
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   git push -u origin main
   ```

2. **Go to Railway.app** and:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will automatically detect it's a Python project

### Option 3: Direct Railway Connection

1. **Go to** https://railway.app/new
2. **Select "Empty Project"**
3. **Connect GitHub** and select your repository
4. **Railway will auto-deploy**

## Environment Variables (Optional)

If you want to enable video features, add these Bunny.net variables to Railway:

```
BUNNY_API_KEY=your-bunny-api-key
BUNNY_LIBRARY_ID=your-library-id
BUNNY_PULL_ZONE=your-pull-zone-domain
BUNNY_COLLECTION_ID=your-collection-id  # Optional
FRONTEND_URL=https://next-js-14-front-end-for-chat-plast.vercel.app
```

## Deployment Files

✅ **Procfile** - Tells Railway how to run the app
✅ **requirements.txt** - Python dependencies  
✅ **main.py** - Application code (Bunny.net Stream integration)
✅ **Health Check** - `/health` endpoint for monitoring

## Post-Deployment

1. **Check Health**: Visit `https://YOUR-APP.up.railway.app/health`
2. **Test API**: Visit `https://YOUR-APP.up.railway.app/docs`
3. **Update Frontend**: Update the API URL in your Vercel frontend

## Your Frontend URL
https://next-js-14-front-end-for-chat-plast.vercel.app

## Current Status
- ✅ Code is ready for deployment
- ✅ Dependencies are minimal and stable
- ✅ CORS is configured for your frontend
- ✅ Health check endpoint added
- 🟡 Need to connect to Railway (follow steps above)

## Troubleshooting

If deployment fails:
1. Check Railway logs
2. Verify Python version (should use 3.9+)
3. Check that `main.py` is in root directory
4. Ensure `Procfile` points to correct module

Railway will assign you a URL like: `https://web-production-XXXXX.up.railway.app`