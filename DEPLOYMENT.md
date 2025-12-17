# Proof of Consideration - Production Deployment Guide

This guide covers deploying the PoC platform to production using Railway (API) and Vercel (Frontend).

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **Domain** (optional but recommended)
4. **Production API Keys**:
   - Clerk (live mode)
   - Stripe (live mode)
   - Resend

## Part 1: Backend Deployment (Railway)

### 1.1 Create PostgreSQL Database

```bash
# In Railway dashboard:
1. Click "New Project"
2. Select "Provision PostgreSQL"
3. Copy the DATABASE_URL from environment variables

postgresql://postgres:VJgQMrtHapWZqqJmisUqdqYBuZTgLeFU@postgres.railway.internal:5432/railway
```

### 1.2 Create Redis Instance

```bash
# In Railway dashboard:
1. Click "+ New" in your project
2. Select "Provision Redis"
3. Copy the REDIS_URL from environment variables
redis://default:rprFDbqMJQALfcXLeennJTMGhgyMKBWV@redis.railway.internal:6379
```

### 1.3 Deploy FastAPI Backend

```bash
# From your local repo:
railway login
railway init
railway link

# Set environment variables:
railway variables set DATABASE_URL="your_database_url_from_railway"
railway variables set REDIS_URL="your_redis_url_from_railway"
railway variables set CLERK_SECRET_KEY="your_clerk_secret_key"
railway variables set STRIPE_SECRET_KEY="your_stripe_secret_key"
railway variables set STRIPE_WEBHOOK_SECRET="your_stripe_webhook_secret"
railway variables set RESEND_API_KEY="your_resend_api_key"
railway variables set FRONTEND_URL="https://yourdomain.com"
railway variables set PROTOCOL_FEE_PERCENT="7"

# Deploy:
railway up
```

### 1.4 Run Database Migrations

```bash
# SSH into Railway container or run locally:
cd packages/database
npx prisma generate
npx prisma db push
```

### 1.5 Configure Custom Domain (Optional)

```bash
# In Railway dashboard:
1. Go to your FastAPI service
2. Click "Settings" → "Domains"
3. Add "api.yourdomain.com"
4. Update DNS records as instructed
```

## Part 2: Frontend Deployment (Vercel)

### 2.1 Deploy to Vercel

```bash
# From your local repo:
cd apps/web
vercel login
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? proof-of-consideration
# - Directory? apps/web
```

### 2.2 Set Environment Variables

```bash
# In Vercel dashboard:
1. Go to project Settings → Environment Variables
2. Add:
   - NEXT_PUBLIC_API_URL = https://api.yourdomain.com
   - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = pk_live_...
   - CLERK_SECRET_KEY = sk_live_...
3. Redeploy
```

### 2.3 Configure Custom Domain

```bash
# In Vercel dashboard:
1. Go to Settings → Domains
2. Add "yourdomain.com"
3. Update DNS records as instructed
```

## Part 3: Configure External Services

### 3.1 Clerk Setup

```bash
# In Clerk dashboard (https://dashboard.clerk.com):

1. Create production instance

2. Configure JWT Template:
   - Go to JWT Templates
   - Add user ID to claims

3. Set up webhooks:
   - Webhook URL: https://api.yourdomain.com/api/webhooks/clerk
   - Events: user.created, user.updated
   - Copy webhook secret

4. Update application URLs:
   - Home URL: https://yourdomain.com
   - Sign in URL: https://yourdomain.com/sign-in
   - Sign up URL: https://yourdomain.com/sign-up
```

### 3.2 Stripe Setup

```bash
# In Stripe dashboard (https://dashboard.stripe.com):

1. Switch to live mode

2. Get API keys:
   - Go to Developers → API keys
   - Copy Secret key (sk_live_...)

3. Set up Connect:
   - Go to Connect → Settings
   - Get Connect client ID (ca_...)

4. Configure webhooks:
   - Webhook URL: https://api.yourdomain.com/api/webhooks/stripe
   - Events to listen for:
     * payment_intent.succeeded
     * payment_intent.payment_failed
     * account.updated
     * transfer.created
     * transfer.failed
   - Copy webhook secret (whsec_...)

5. Connect settings:
   - Set branding (logo, colors)
   - Configure payout schedule
   - Set statement descriptor
```

### 3.3 Resend Setup

```bash
# In Resend dashboard (https://resend.com):

1. Add domain:
   - Go to Domains
   - Add "yourdomain.com"
   - Update DNS records (SPF, DKIM)
   - Verify domain

2. Get API key:
   - Go to API Keys
   - Create key
   - Copy re_...

3. Update email service:
   - Change from_email in apps/api/services/email.py
   - From: "PoC <noreply@poc.io>"
   - To: "PoC <noreply@yourdomain.com>"
```

## Part 4: Database Setup

### 4.1 Run Migrations

```bash
# Connect to production database:
cd packages/database

# Generate Prisma client:
npx prisma generate

# Push schema to database:
npx prisma db push

# Verify tables created:
npx prisma studio
# Open http://localhost:5555
```

### 4.2 Create Admin User (Optional)

```sql
-- Connect to PostgreSQL:
psql $DATABASE_URL

-- Create admin user:
INSERT INTO "User" (id, clerk_id, email, role, created_at, updated_at)
VALUES (
  gen_random_uuid()::text,
  'admin_clerk_id',
  'admin@yourdomain.com',
  'ADMIN',
  NOW(),
  NOW()
);
```

## Part 5: Post-Deployment Checks

### 5.1 Smoke Tests

```bash
# Test API health:
curl https://api.yourdomain.com/health

# Test API root:
curl https://api.yourdomain.com/

# Test frontend:
curl https://yourdomain.com/

# Test authentication:
# 1. Sign up on frontend
# 2. Check user created in database
# 3. Check Clerk webhook received
```

### 5.2 Test Critical Flows

**Test 1: User Registration**
1. Go to https://yourdomain.com
2. Sign up with real email
3. Verify user created in database
4. Check Clerk webhook logs in Railway

**Test 2: Stripe Connect**
1. Sign in as considerer
2. Go to /earnings
3. Click "Connect with Stripe"
4. Complete onboarding
5. Verify account created in Stripe dashboard

**Test 3: Create Campaign (Small Budget)**
1. Sign in as buyer
2. Create campaign with $1 bounty, 1 response
3. Activate campaign
4. Verify campaign in database

**Test 4: Submit Proof**
1. Sign in as considerer
2. Accept task
3. Submit thoughtful response
4. Wait for verification
5. Check email received
6. Verify payment in Stripe

**Test 5: Email Notifications**
1. Submit proof (as considerer)
2. Check inbox for verification email
3. Complete campaign (as buyer)
4. Check inbox for completion email

### 5.3 Monitoring Setup

**Option 1: Railway Logs**
```bash
# View real-time logs:
railway logs

# Filter for errors:
railway logs | grep ERROR
```

**Option 2: Sentry (Recommended)**
```bash
# 1. Sign up at sentry.io
# 2. Create project for Python
# 3. Install Sentry:
pip install sentry-sdk[fastapi]

# 4. Add to apps/api/main.py:
import sentry_sdk

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    traces_sample_rate=0.1,
    environment="production"
)

# 5. Deploy
```

## Part 6: Production Configuration

### 6.1 Rate Limiting

Rate limits are configured in `apps/api/middleware/rate_limit.py`:

- Proof submission: 10/minute per user
- Campaign creation: 5/hour per user
- Verification: 20/minute
- Task acceptance: 30/minute
- Stripe Connect: 5/hour
- General API: 100/minute

Adjust in production based on usage patterns.

### 6.2 Verification Thresholds

Default thresholds in database schema:
- Min Relevance: 0.65
- Min Novelty: 0.70
- Min Coherence: 0.60
- Min Combined: 0.60

Buyers can customize per campaign.

### 6.3 Payment Settings

- Protocol Fee: 7%
- Stripe Connect Fee: 0.25%
- Net to Considerer: ~92.75%

Example: $10 bounty
- Considerer receives: $9.275
- Protocol keeps: $0.70
- Stripe takes: $0.025

## Part 7: Maintenance

### 7.1 Database Backups

```bash
# Railway automatic backups:
# - Enabled by default for PostgreSQL
# - Retention: 7 days
# - Can restore from dashboard

# Manual backup:
pg_dump $DATABASE_URL > backup.sql

# Restore:
psql $DATABASE_URL < backup.sql
```

### 7.2 Updating the Application

```bash
# Backend (Railway):
git push origin main
# Railway auto-deploys on push

# Frontend (Vercel):
git push origin main
# Vercel auto-deploys on push

# Or manual deploy:
vercel --prod
```

### 7.3 Scaling

**Railway Auto-Scaling:**
- Configured in railway.toml
- Scales based on CPU/memory
- Max 4 workers (gunicorn)

**Vercel Auto-Scaling:**
- Automatic
- Serverless functions scale to demand

**Database Scaling:**
- Upgrade plan in Railway dashboard
- Monitor with `railway logs`

## Part 8: Security Checklist

Before going live:

- [ ] All API keys are live mode (not test mode)
- [ ] Clerk webhook secret configured
- [ ] Stripe webhook secret configured
- [ ] CORS origins set to production domain only
- [ ] Rate limiting enabled
- [ ] SSL/TLS certificates active (automatic with Vercel/Railway)
- [ ] Database connection uses SSL
- [ ] Environment variables not committed to git
- [ ] Admin endpoints protected (if any)
- [ ] Error messages don't leak sensitive data
- [ ] Logs don't contain secrets
- [ ] Stripe Connect restricted to your account

## Part 9: Cost Estimates

### Monthly Costs (Starting Small)

**Railway (Backend + Database + Redis):**
- Hobby Plan: $5/month
- Pro Plan (recommended): $20/month
- Includes PostgreSQL + Redis + API hosting

**Vercel (Frontend):**
- Free tier: $0/month (enough for MVP)
- Pro: $20/month (if you need more)

**Clerk (Auth):**
- Free: 10,000 MAU
- Pro: $25/month + $0.02/MAU

**Stripe:**
- No monthly fee
- 2.9% + $0.30 per transaction

**Resend (Email):**
- Free: 100 emails/day
- Pro: $20/month for 50k emails

**Total MVP Cost: ~$45-65/month**

## Part 10: Go-Live Checklist

Final checks before announcing:

- [ ] All environment variables set correctly
- [ ] Database migrations run
- [ ] Admin user created
- [ ] All smoke tests passing
- [ ] Rate limiting tested
- [ ] Email notifications working
- [ ] Stripe Connect tested with real payout
- [ ] Test campaign end-to-end with real money ($1)
- [ ] Error monitoring active (Sentry)
- [ ] Backup strategy in place
- [ ] Support email configured
- [ ] Terms of Service live
- [ ] Privacy Policy live
- [ ] About/FAQ pages complete
- [ ] Analytics tracking (optional)

## Support

If you encounter issues:
1. Check Railway logs: `railway logs`
2. Check Vercel logs: Vercel dashboard → Deployments
3. Check Stripe webhooks: Stripe dashboard → Developers → Webhooks
4. Check Clerk webhooks: Clerk dashboard → Webhooks
5. Review this deployment guide

---

**Congratulations!** Your Proof of Consideration platform is now live in production! 🎉
