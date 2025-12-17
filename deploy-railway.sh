#!/bin/bash

# Railway Deployment Script for Proof of Consideration
# This script helps you deploy the FastAPI backend to Railway

echo "🚂 Railway Deployment Script for PoC Platform"
echo "=============================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "Install it with: npm install -g @railway/cli"
    echo "Or: brew install railway"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Step 1: Login
echo "Step 1: Logging in to Railway..."
railway login
echo ""

# Step 2: Link project
echo "Step 2: Linking to Railway project..."
railway link
echo ""

# Step 3: Set environment variables
echo "Step 3: Setting environment variables..."
echo ""
echo "⚠️  You'll need to provide these values:"
echo "   - DATABASE_URL (from Railway PostgreSQL service)"
echo "   - REDIS_URL (from Railway Redis service)"
echo "   - CLERK_SECRET_KEY (from Clerk dashboard)"
echo "   - STRIPE_SECRET_KEY (from Stripe dashboard)"
echo "   - STRIPE_WEBHOOK_SECRET (from Stripe webhooks)"
echo "   - RESEND_API_KEY (from Resend dashboard)"
echo "   - FRONTEND_URL (your Vercel URL or custom domain)"
echo ""

read -p "Enter DATABASE_URL: " DATABASE_URL
railway variables set DATABASE_URL="$DATABASE_URL"

read -p "Enter REDIS_URL: " REDIS_URL
railway variables set REDIS_URL="$REDIS_URL"

read -p "Enter CLERK_SECRET_KEY: " CLERK_SECRET_KEY
railway variables set CLERK_SECRET_KEY="$CLERK_SECRET_KEY"

read -p "Enter STRIPE_SECRET_KEY: " STRIPE_SECRET_KEY
railway variables set STRIPE_SECRET_KEY="$STRIPE_SECRET_KEY"

read -p "Enter STRIPE_WEBHOOK_SECRET: " STRIPE_WEBHOOK_SECRET
railway variables set STRIPE_WEBHOOK_SECRET="$STRIPE_WEBHOOK_SECRET"

read -p "Enter RESEND_API_KEY: " RESEND_API_KEY
railway variables set RESEND_API_KEY="$RESEND_API_KEY"

read -p "Enter FRONTEND_URL: " FRONTEND_URL
railway variables set FRONTEND_URL="$FRONTEND_URL"

railway variables set PROTOCOL_FEE_PERCENT="7"

echo ""
echo "✅ Environment variables set!"
echo ""

# Step 4: Deploy
echo "Step 4: Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Check deployment status: railway status"
echo "2. View logs: railway logs"
echo "3. Get your API URL from Railway dashboard"
echo "4. Run database migrations (see DEPLOY_NOW.md)"
echo "5. Configure Clerk, Stripe, Resend webhooks"
echo ""
