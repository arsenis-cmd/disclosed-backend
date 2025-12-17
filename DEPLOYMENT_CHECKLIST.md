# 📋 Deployment Checklist

Use this checklist to track your deployment progress. Mark items as you complete them.

---

## Pre-Deployment Setup

- [ ] Railway account created
- [ ] PostgreSQL database provisioned in Railway
- [ ] Redis instance provisioned in Railway
- [ ] Vercel account created
- [ ] Clerk account created (production instance)
- [ ] Stripe account created (switched to live mode)
- [ ] Resend account created
- [ ] All API keys collected and saved securely

---

## Backend Deployment (Railway)

### Environment Variables
- [ ] DATABASE_URL set in Railway
- [ ] REDIS_URL set in Railway
- [ ] CLERK_SECRET_KEY set in Railway
- [ ] STRIPE_SECRET_KEY set in Railway
- [ ] STRIPE_WEBHOOK_SECRET set in Railway
- [ ] RESEND_API_KEY set in Railway
- [ ] FRONTEND_URL set in Railway (temporary placeholder)
- [ ] PROTOCOL_FEE_PERCENT set to "7"

### Deployment
- [ ] Ran `./deploy-railway.sh` (or `railway up`)
- [ ] Backend deployment successful
- [ ] Copied Railway API URL: ___________________________________
- [ ] Health check passing: `curl https://[railway-url]/health`
- [ ] API root responding: `curl https://[railway-url]/`

---

## Database Setup

- [ ] Ran `./run-migrations.sh`
- [ ] Prisma client generated successfully
- [ ] Schema pushed to production database
- [ ] Verified tables in Prisma Studio:
  - [ ] User table exists
  - [ ] Campaign table exists
  - [ ] Task table exists
  - [ ] Proof table exists
  - [ ] Payment table exists
  - [ ] VerificationLog table exists

---

## Clerk Configuration

### Webhooks
- [ ] Created webhook endpoint
- [ ] Webhook URL: `https://[railway-url]/api/webhooks/clerk`
- [ ] Subscribed to `user.created` event
- [ ] Subscribed to `user.updated` event
- [ ] Copied webhook signing secret
- [ ] Set CLERK_WEBHOOK_SECRET in Railway

### Application Settings
- [ ] JWT Template created with custom claims
- [ ] Home URL set to production domain
- [ ] Sign in URL configured
- [ ] Sign up URL configured
- [ ] After sign in URL configured
- [ ] After sign up URL configured

---

## Stripe Configuration

### API Keys
- [ ] Switched to live mode
- [ ] Copied Secret key (sk_live_...)
- [ ] Already set STRIPE_SECRET_KEY ✓

### Connect Settings
- [ ] Added branding (logo, colors)
- [ ] Set business name
- [ ] Set support email
- [ ] Set statement descriptor
- [ ] Configured payout schedule (Daily recommended)

### Webhooks
- [ ] Created webhook endpoint
- [ ] Webhook URL: `https://[railway-url]/api/webhooks/stripe`
- [ ] Subscribed to events:
  - [ ] payment_intent.succeeded
  - [ ] payment_intent.payment_failed
  - [ ] account.updated
  - [ ] transfer.created
  - [ ] transfer.failed
- [ ] Copied webhook signing secret
- [ ] Updated STRIPE_WEBHOOK_SECRET in Railway

---

## Resend Configuration

- [ ] Created API key
- [ ] Already set RESEND_API_KEY ✓
- [ ] (Optional) Added custom domain
- [ ] (Optional) Added DNS records (SPF, DKIM)
- [ ] (Optional) Verified domain
- [ ] (Optional) Updated sender email in code

---

## Frontend Deployment (Vercel)

### Preparation
- [ ] Ran `npm install` in `apps/web`
- [ ] All dependencies installed successfully

### Environment Variables
- [ ] NEXT_PUBLIC_API_URL set (Railway API URL)
- [ ] NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY set
- [ ] CLERK_SECRET_KEY set

### Deployment
- [ ] Ran `./deploy-vercel.sh` (or `vercel --prod`)
- [ ] Frontend deployment successful
- [ ] Copied Vercel URL: ___________________________________
- [ ] Can access frontend at Vercel URL

---

## Post-Deployment Configuration

### Update Railway Variables
- [ ] Updated FRONTEND_URL with Vercel URL
- [ ] Updated CORS_ORIGINS with Vercel URL
- [ ] Redeployed backend (if needed)

### Update Clerk URLs
- [ ] Updated all URLs in Clerk dashboard to Vercel URL
- [ ] Tested sign in redirect works
- [ ] Tested sign up redirect works

### Update Stripe Redirects
- [ ] Verified Connect redirect URLs point to Vercel
- [ ] Refresh URL: `https://[vercel-url]/earnings/setup?refresh=true`
- [ ] Return URL: `https://[vercel-url]/earnings/setup?success=true`

---

## Testing & Verification

### Smoke Tests
- [ ] Backend health check passes
- [ ] Frontend loads successfully
- [ ] Can access sign in page
- [ ] No console errors in browser

### Critical Flow: User Registration
- [ ] Created new test account
- [ ] Successfully signed up
- [ ] Redirected to dashboard
- [ ] User created in database (verified in Prisma Studio)
- [ ] Clerk webhook received (checked Railway logs)

### Critical Flow: Stripe Connect
- [ ] Signed in as considerer
- [ ] Navigated to `/earnings`
- [ ] Clicked "Connect with Stripe"
- [ ] Completed Stripe onboarding
- [ ] Redirected back to app
- [ ] Stripe account created in dashboard
- [ ] Account ID saved in database

### Critical Flow: Campaign Creation
- [ ] Signed in as buyer (different account)
- [ ] Navigated to `/campaigns/new`
- [ ] Created test campaign:
  - Title: "Test Campaign"
  - Bounty: $1.00 (REAL MONEY - BE CAREFUL!)
  - Target responses: 1
- [ ] Campaign saved in database
- [ ] Campaign appears on dashboard

### Critical Flow: Proof Submission
- [ ] Signed in as considerer (with Stripe connected)
- [ ] Found test campaign
- [ ] Accepted task
- [ ] Submitted thoughtful response
- [ ] Verification completed (checked logs)
- [ ] Received verification email
- [ ] Payment transferred to Stripe (if passed)
- [ ] Payment record in database

### Email Notifications
- [ ] Received verification result email (pass or fail)
- [ ] Email formatting looks good
- [ ] Links in email work (if any)
- [ ] Buyer received "new response" email
- [ ] If campaign complete, buyer received completion email

### Rate Limiting
- [ ] Tried submitting multiple proofs rapidly
- [ ] Rate limit kicked in (429 status)
- [ ] Error message displayed to user

### Mobile Testing
- [ ] Tested on mobile browser (iOS or Android)
- [ ] Layout responsive
- [ ] Touch targets adequate (44x44px minimum)
- [ ] No horizontal scrolling
- [ ] Forms work on mobile

---

## Production Readiness

### Security Checklist
- [ ] All API keys are **live mode** (not test)
- [ ] CORS origins restricted to production domain only
- [ ] Environment variables not committed to git
- [ ] .gitignore includes .env files
- [ ] SSL/TLS active (automatic with Railway/Vercel)
- [ ] Rate limiting enabled and tested
- [ ] Webhook secrets configured
- [ ] Database connections use SSL

### Content & Legal
- [ ] Terms of Service page created
- [ ] Privacy Policy page created
- [ ] About page complete
- [ ] FAQ page complete
- [ ] Support email configured
- [ ] Contact information visible

### Monitoring Setup
- [ ] Can access Railway logs
- [ ] Can access Vercel logs
- [ ] Can check Clerk webhook logs
- [ ] Can check Stripe webhook logs
- [ ] Can check Resend sending logs
- [ ] (Optional) Sentry configured for error tracking

### Performance
- [ ] Ran Lighthouse audit (score >80 recommended)
- [ ] Fixed any critical accessibility issues
- [ ] Tested page load times
- [ ] Checked mobile performance

---

## Launch Preparation

### Pre-Launch Checklist
- [ ] All critical flows tested and working
- [ ] No errors in production logs
- [ ] Webhooks all functioning
- [ ] Email notifications working
- [ ] Payments processing correctly
- [ ] Mobile experience satisfactory

### Custom Domain (Optional)
- [ ] Domain purchased
- [ ] DNS configured for Vercel
- [ ] DNS configured for Railway (if using custom API domain)
- [ ] DNS configured for Resend (if using custom domain)
- [ ] SSL certificates issued
- [ ] All URLs updated to use custom domain

### Soft Launch (Recommended)
- [ ] Invited 5-10 beta testers
- [ ] Sent beta testing instructions
- [ ] Set up feedback collection method
- [ ] Monitoring for issues
- [ ] Ready to respond to questions

---

## Post-Launch Monitoring

### First 24 Hours
- [ ] Check logs hourly
- [ ] Monitor error rates
- [ ] Track user signups
- [ ] Watch for payment issues
- [ ] Respond to user feedback

### First Week
- [ ] Daily log review
- [ ] Track key metrics:
  - [ ] User signups
  - [ ] Campaigns created
  - [ ] Proofs submitted
  - [ ] Verification pass rate
  - [ ] Payments processed
- [ ] Address critical bugs
- [ ] Collect user feedback

### First Month Success Metrics
- [ ] 20+ signups (minimum viable success)
- [ ] 5+ campaigns created
- [ ] 25+ proofs submitted
- [ ] 15+ proofs verified and paid
- [ ] <5% critical error rate
- [ ] >70% verification pass rate

---

## 🎉 Deployment Complete!

Once all items are checked:

✅ Your Proof of Consideration platform is **LIVE**!
✅ All critical systems operational
✅ Monitoring in place
✅ Ready for real users

---

## 📊 Deployment Summary

**Date Started:** ___________________________________

**Date Completed:** ___________________________________

**Railway URL:** ___________________________________

**Vercel URL:** ___________________________________

**Custom Domain (if any):** ___________________________________

**First Campaign Created:** ___________________________________

**First Payment Processed:** ___________________________________

---

## Notes & Issues

Use this space to track any issues encountered during deployment:

```
Issue 1:
Description:
Resolution:

Issue 2:
Description:
Resolution:

Issue 3:
Description:
Resolution:
```

---

**Congratulations on launching your marketplace! 🚀**
