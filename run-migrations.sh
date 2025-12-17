#!/bin/bash

# Database Migration Script for Proof of Consideration
# Run this AFTER deploying to Railway

echo "🗄️  Database Migration Script"
echo "============================="
echo ""

# Check if we're in the right directory
if [ ! -d "packages/database" ]; then
    echo "❌ Error: packages/database directory not found!"
    echo "Make sure you're running this from the project root."
    exit 1
fi

echo "✅ Found packages/database directory"
echo ""

# Ask for DATABASE_URL
echo "⚠️  You need your production DATABASE_URL from Railway"
echo "Get it with: railway variables | grep DATABASE_URL"
echo "Or from Railway dashboard > PostgreSQL service > Variables"
echo ""

read -p "Enter production DATABASE_URL: " DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL cannot be empty!"
    exit 1
fi

echo ""
echo "Step 1: Generating Prisma client..."
cd packages/database
export DATABASE_URL="$DATABASE_URL"
npx prisma generate

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate Prisma client!"
    exit 1
fi

echo "✅ Prisma client generated"
echo ""

echo "Step 2: Pushing schema to production database..."
npx prisma db push

if [ $? -ne 0 ]; then
    echo "❌ Failed to push schema!"
    echo "Check your DATABASE_URL and network connection."
    exit 1
fi

echo "✅ Schema pushed successfully!"
echo ""

echo "Step 3: Verifying tables..."
echo "Opening Prisma Studio to view database..."
echo "Press Ctrl+C when done reviewing."
echo ""

npx prisma studio

echo ""
echo "🎉 Database migrations complete!"
echo ""
echo "Next steps:"
echo "1. Verify all tables exist in Prisma Studio"
echo "2. Configure external services (Clerk, Stripe, Resend)"
echo "3. Deploy frontend to Vercel"
echo ""
