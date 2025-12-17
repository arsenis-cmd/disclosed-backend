# Quick Deployment Guide - Ready to Deploy! 🚀

You have the API keys ready! Let's deploy from section 1.3 onwards.

---

## ✅ Prerequisites Complete

- [x] Railway account with PostgreSQL database created
- [x] Railway account with Redis instance created
- [x] API keys collected (Clerk, Stripe, Resend)
- [x] Design system foundation set up
- [x] Dependencies added to package.json

---

## 📦 Step 0: Install Frontend Dependencies

Before deploying, install the new design system dependencies:

```bash
cd apps/web
npm install
# This will install the newly added @tailwindcss/forms
```

---

## 🚂 Part 1: Deploy FastAPI Backend to Railway

### 1.3 Deploy FastAPI Backend

#### Option A: Using Railway CLI (Recommended)

```bash
# 1. Login to Railway
railway login

# 2. Link to your existing Railway project
railway link
# Select your project from the list

# 3. Set environment variables (replace with your actual values)
railway variables set DATABASE_URL="postgresql://..."
railway variables set REDIS_URL="redis://..."
railway variables set CLERK_SECRET_KEY="sk_live_..."
railway variables set STRIPE_SECRET_KEY="sk_live_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set RESEND_API_KEY="re_..."
railway variables set FRONTEND_URL="https://yourdomain.com"
railway variables set PROTOCOL_FEE_PERCENT="7"

# 4. Deploy the backend
railway up
```

#### Option B: Using Railway Dashboard (Alternative)

1. Go to your Railway project dashboard
2. Click on your FastAPI service (or create a new service)
3. Go to **Settings** → **Environment Variables**
4. Add each variable:

```
DATABASE_URL = postgresql://user:password@host:5432/db_name
REDIS_URL = redis://host:6379
CLERK_SECRET_KEY = sk_live_xxxxx
STRIPE_SECRET_KEY = sk_live_xxxxx
STRIPE_WEBHOOK_SECRET = whsec_xxxxx
RESEND_API_KEY = re_xxxxx
FRONTEND_URL = https://yourdomain.com
PROTOCOL_FEE_PERCENT = 7
```

5. Go to **Settings** → **Deploy**
6. Connect your GitHub repo (or push code)
7. Railway will automatically detect the `railway.toml` and deploy

#### Option C: Using Git Push

If your Railway project is set up with GitHub integration:

```bash
# Commit all changes
git add .
git commit -m "Deploy production-ready platform with new design system"

# Push to main branch
git push origin main

# Railway will auto-deploy
```

---

## 🗄️ Part 2: Run Database Migrations (Section 1.4)

Once the backend is deployed, you need to push the Prisma schema to your production database.

### Method 1: Local Connection to Production DB

```bash
# From project root
cd packages/database

# Set the production DATABASE_URL temporarily
export DATABASE_URL="postgresql://user:password@host:5432/db_name"

# Generate Prisma client
npx prisma generate

# Push schema to production database
npx prisma db push

# Verify tables were created
npx prisma studio
# This opens http://localhost:5555 to browse the database
```

### Method 2: Using Railway Shell

```bash
# Open a shell in your Railway container
railway run bash

# Inside the container
cd packages/database
npx prisma generate
npx prisma db push
exit
```

---

## 🔧 Part 3: Configure External Services

### 3.1 Clerk Setup (Section 3.1)

**Get your Railway API URL first:**
```bash
railway status
# Copy the service URL (e.g., https://your-app.up.railway.app)
```

**In Clerk Dashboard** (https://dashboard.clerk.com):

1. **Create production instance** (if not already)

2. **Configure JWT Template:**
   - Go to **JWT Templates**
   - Click "New Template"
   - Name: "proof-of-consideration"
   - Add custom claims:
     ```json
     {
       "userId": "{{user.id}}"
     }
     ```

3. **Set up webhooks:**
   - Go to **Webhooks**
   - Click "Add Endpoint"
   - Endpoint URL: `https://your-railway-url.up.railway.app/api/webhooks/clerk`
   - Subscribe to events:
     - `user.created`
     - `user.updated`
   - Copy the **Signing Secret** (starts with `whsec_`)
   - Add to Railway: `railway variables set CLERK_WEBHOOK_SECRET="whsec_..."`

4. **Update application URLs:**
   - Go to **Paths**
   - Home URL: `https://yourdomain.com`
   - Sign in URL: `https://yourdomain.com/sign-in`
   - Sign up URL: `https://yourdomain.com/sign-up`
   - After sign in URL: `https://yourdomain.com/dashboard`
   - After sign up URL: `https://yourdomain.com/dashboard`

---

### 3.2 Stripe Setup (Section 3.2)

**In Stripe Dashboard** (https://dashboard.stripe.com):

1. **Switch to live mode** (toggle in top right)

2. **Get API keys:**
   - Go to **Developers** → **API keys**
   - Copy **Secret key** (sk_live_...)
   - Already added to Railway ✓

3. **Set up Connect:**
   - Go to **Connect** → **Settings**
   - **Branding**: Add your logo and brand colors
   - **Public details**:
     - Business name: "Proof of Consideration"
     - Support email: your email
     - Statement descriptor: "POC_TASK"

4. **Configure webhooks:**
   - Go to **Developers** → **Webhooks**
   - Click "Add endpoint"
   - Endpoint URL: `https://your-railway-url.up.railway.app/api/webhooks/stripe`
   - Select events to listen to:
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `account.updated`
     - `transfer.created`
     - `transfer.failed`
   - Copy the **Signing secret** (whsec_...)
   - Add to Railway: `railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."`

5. **Enable payouts:**
   - Go to **Settings** → **Connect settings**
   - Enable "Standard account application"
   - Set payout schedule: "Daily" (recommended)

---

### 3.3 Resend Setup (Section 3.3)

**In Resend Dashboard** (https://resend.com):

1. **Add domain (if you have one):**
   - Go to **Domains**
   - Click "Add Domain"
   - Enter your domain (e.g., `yourdomain.com`)
   - Add the DNS records shown (SPF, DKIM)
   - Wait for verification (can take up to 48 hours)

2. **Get API key:**
   - Go to **API Keys**
   - Create new key (if not already)
   - Copy the key (re_...)
   - Already added to Railway ✓

3. **Update email sender:**
   - Once domain is verified, update the sender email in your code
   - For now, you can use the default Resend sandbox: `onboarding@resend.dev`

---

## 🧪 Part 4: Post-Deployment Checks (Section 5)

### 5.1 Smoke Tests

```bash
# Get your Railway API URL
railway status

# Test API health
curl https://your-railway-url.up.railway.app/health
# Expected: {"status": "healthy"}

# Test API root
curl https://your-railway-url.up.railway.app/
# Expected: {"message": "Proof of Consideration API"}

# Check Railway logs
railway logs
# Look for any errors
```

---

## 🌐 Part 5: Deploy Frontend to Vercel (Section 2)

### 2.1 Deploy to Vercel

```bash
# From project root
cd apps/web

# Install Vercel CLI (if not installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (follow prompts)
vercel

# When prompted:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? proof-of-consideration
# - Directory? ./
# - Override settings? No
```

### 2.2 Set Environment Variables in Vercel

**In Vercel Dashboard** (https://vercel.com):

1. Go to your project
2. Go to **Settings** → **Environment Variables**
3. Add the following:

```
NEXT_PUBLIC_API_URL = https://your-railway-url.up.railway.app
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = pk_live_xxxxx
CLERK_SECRET_KEY = sk_live_xxxxx
```

4. **Redeploy** to apply environment variables:

```bash
vercel --prod
```

### 2.3 Configure Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS records as instructed by Vercel
4. Wait for SSL certificate to be issued

---

## ✅ Part 6: Final Configuration Updates

### Update CORS Origins

Now that you have your Vercel URL, update CORS in Railway:

```bash
railway variables set CORS_ORIGINS='["https://your-vercel-url.vercel.app"]'
# Or if you have a custom domain:
railway variables set CORS_ORIGINS='["https://yourdomain.com"]'
```

### Update Clerk Frontend URL

In Railway:
```bash
railway variables set FRONTEND_URL="https://your-vercel-url.vercel.app"
```

In Clerk Dashboard:
- Update all URLs to point to your Vercel deployment

### Update Stripe Redirect URLs

In your Stripe Connect settings, ensure redirect URLs point to:
- `https://your-vercel-url.vercel.app/earnings/setup?refresh=true`
- `https://your-vercel-url.vercel.app/earnings/setup?success=true`

---

## 🧪 Part 7: Test Critical Flows (Section 5.2)

### Test 1: User Registration

1. Go to `https://your-vercel-url.vercel.app`
2. Click "Sign Up"
3. Create a new account
4. Check Railway logs for Clerk webhook:
   ```bash
   railway logs | grep "clerk webhook"
   ```
5. Verify user was created in database:
   ```bash
   cd packages/database
   npx prisma studio
   # Check the User table
   ```

### Test 2: Stripe Connect (Small Test)

1. Sign in as a considerer
2. Go to `/earnings`
3. Click "Connect with Stripe"
4. Complete the onboarding (use test mode if available)
5. Verify account created in Stripe Dashboard

### Test 3: Create $1 Campaign (Real Money - CAREFUL!)

1. Sign in as a buyer (different account)
2. Go to `/campaigns/new`
3. Create campaign:
   - Title: "Test Campaign"
   - Bounty: $1.00
   - Target responses: 1
4. Activate campaign
5. Check database to verify campaign saved

### Test 4: Submit Proof

1. Sign in as considerer (with Stripe connected)
2. Accept the test task
3. Submit a thoughtful response
4. Wait for verification (check Railway logs)
5. Check email for verification result
6. Check Stripe for transfer

### Test 5: Email Notifications

1. Submit a proof (as considerer)
2. Check your inbox for verification email
3. If no email, check Railway logs:
   ```bash
   railway logs | grep "email"
   ```

---

## 📊 Monitoring & Logs

### View Real-time Logs

```bash
# All logs
railway logs

# Filter for errors
railway logs | grep ERROR

# Filter for specific component
railway logs | grep "email"
railway logs | grep "stripe"
railway logs | grep "verification"
```

### Check Service Status

```bash
railway status
```

### Access Railway Database

```bash
# Get DATABASE_URL
railway variables

# Connect with psql
psql "postgresql://..."

# Or use Prisma Studio
cd packages/database
npx prisma studio
```

---

## 🔒 Security Checklist (Section 8)

Before going live:

- [ ] All API keys are in **live mode** (not test mode)
- [ ] Clerk webhook secret configured in Railway
- [ ] Stripe webhook secret configured in Railway
- [ ] CORS origins set to production domain only
- [ ] Rate limiting enabled (already configured ✓)
- [ ] SSL/TLS active (automatic with Railway/Vercel ✓)
- [ ] Environment variables not in git (check .gitignore ✓)
- [ ] Database connection uses SSL (Railway default ✓)

---

## 💰 Expected Monthly Costs (Section 9)

**Starting small:**
- Railway (Backend + DB + Redis): **$20/month** (Pro plan recommended)
- Vercel (Frontend): **$0/month** (Free tier sufficient for MVP)
- Clerk (Auth): **$0/month** (Free for <10,000 users)
- Stripe: **No monthly fee** (2.9% + $0.30 per transaction)
- Resend (Email): **$0/month** (Free for 100 emails/day)

**Total: ~$20-25/month to start**

---

## 🎉 Go-Live Checklist (Section 10)

Before announcing publicly:

- [ ] Backend deployed to Railway ✓
- [ ] Frontend deployed to Vercel
- [ ] Database migrations complete
- [ ] All environment variables set
- [ ] Clerk webhooks tested
- [ ] Stripe Connect tested (with real $1 payout)
- [ ] Email notifications working
- [ ] Rate limits tested (try rapid submissions)
- [ ] Test on mobile devices
- [ ] Run Lighthouse audit (score >80)
- [ ] Terms of Service page live
- [ ] Privacy Policy page live
- [ ] Support email configured

---

## 🆘 Troubleshooting

### Backend Issues

**Can't access API:**
```bash
railway logs
# Look for startup errors
```

**Database connection failed:**
- Verify DATABASE_URL is correct
- Check if PostgreSQL service is running in Railway
- Try running migrations again

**Redis errors:**
- Verify REDIS_URL is correct
- If Redis is failing, services should continue (graceful degradation)

### Frontend Issues

**Can't sign in:**
- Check Clerk publishable key is correct
- Verify Clerk webhook is receiving events

**API calls failing:**
- Check NEXT_PUBLIC_API_URL is correct
- Check CORS is configured correctly
- Look at browser console for errors

---

## 📞 Support

If you encounter issues:

1. **Check logs first:**
   ```bash
   railway logs
   ```

2. **Check Railway dashboard:**
   - Service status
   - Environment variables
   - Recent deployments

3. **Check external service dashboards:**
   - Clerk webhooks page
   - Stripe webhooks page
   - Resend logs

4. **Review deployment guide:**
   - `DEPLOYMENT.md` for full reference
   - `PHASE2_COMPLETE.md` for what was built

---

## 🚀 You're Ready to Deploy!

**Start here:**
1. Run `npm install` in `apps/web` directory
2. Set Railway environment variables (section 1.3)
3. Deploy backend: `railway up`
4. Run database migrations
5. Configure Clerk, Stripe, Resend
6. Deploy frontend to Vercel
7. Test critical flows
8. Go live! 🎉

**Estimated deployment time:** 30-45 minutes

Good luck! 🚀
