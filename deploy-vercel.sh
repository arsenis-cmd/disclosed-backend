#!/bin/bash

# Vercel Deployment Script for Proof of Consideration Frontend
# Run this AFTER deploying backend to Railway

echo "▲ Vercel Deployment Script for PoC Platform"
echo "==========================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found!"
    echo "Install it with: npm install -g vercel"
    exit 1
fi

echo "✅ Vercel CLI found"
echo ""

# Check if we're in the right directory
if [ ! -d "apps/web" ]; then
    echo "❌ Error: apps/web directory not found!"
    echo "Make sure you're running this from the project root."
    exit 1
fi

# Step 1: Install dependencies
echo "Step 1: Installing frontend dependencies..."
cd apps/web
npm install --legacy-peer-deps

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Step 2: Login to Vercel
echo "Step 2: Logging in to Vercel..."
vercel login
echo ""

# Step 3: Collect environment variables
echo "Step 3: Collecting environment variables..."
echo ""
echo "⚠️  You'll need:"
echo "   - NEXT_PUBLIC_API_URL (your Railway API URL)"
echo "   - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY (from Clerk dashboard)"
echo "   - CLERK_SECRET_KEY (from Clerk dashboard)"
echo ""

read -p "Enter NEXT_PUBLIC_API_URL (Railway API URL): " API_URL
read -p "Enter NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: " CLERK_PUB_KEY
read -p "Enter CLERK_SECRET_KEY: " CLERK_SECRET

echo ""
echo "Step 4: Deploying to Vercel (preview)..."
vercel

echo ""
echo "✅ Preview deployment complete!"
echo ""

# Step 5: Set environment variables
echo "Step 5: Setting production environment variables..."
vercel env add NEXT_PUBLIC_API_URL production <<EOF
$API_URL
EOF

vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production <<EOF
$CLERK_PUB_KEY
EOF

vercel env add CLERK_SECRET_KEY production <<EOF
$CLERK_SECRET
EOF

echo ""
echo "✅ Environment variables set!"
echo ""

# Step 6: Production deployment
echo "Step 6: Deploying to production..."
read -p "Ready to deploy to production? (y/n): " confirm

if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
    vercel --prod
    echo ""
    echo "🎉 Production deployment complete!"
else
    echo "⏸️  Production deployment skipped."
    echo "Run 'vercel --prod' when ready."
fi

echo ""
echo "Next steps:"
echo "1. Get your Vercel URL from the deployment output"
echo "2. Update FRONTEND_URL in Railway: railway variables set FRONTEND_URL=\"https://your-url.vercel.app\""
echo "3. Update CORS_ORIGINS in Railway: railway variables set CORS_ORIGINS='[\"https://your-url.vercel.app\"]'"
echo "4. Update Clerk dashboard URLs to point to Vercel"
echo "5. Test the application end-to-end"
echo ""
