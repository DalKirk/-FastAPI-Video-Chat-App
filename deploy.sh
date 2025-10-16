#!/bin/bash
# Railway Deployment Script

echo "🚀 Starting Railway Deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway login..."
railway whoami || railway login

# Initialize project (if not already initialized)
echo "📝 Initializing Railway project..."
railway init

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "📊 Check your deployment status at: https://railway.app/dashboard"