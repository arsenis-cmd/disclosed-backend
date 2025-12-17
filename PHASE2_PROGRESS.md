# Phase 2 Implementation Progress

## ✅ Completed (Critical Path)

### 1. Stripe Connect Integration (DONE)

**Backend** (`apps/api/routers/payments.py`):
- ✅ `POST /api/v1/payments/connect/onboard` - Creates Stripe Connect Express account
- ✅ `GET /api/v1/payments/connect/status` - Check payout account status
- ✅ `POST /api/v1/payments/connect/dashboard` - Get Stripe dashboard link
- ✅ `create_stripe_transfer()` - Helper function for automatic payouts

**Proof Verification** (`apps/api/routers/proofs.py`):
- ✅ Updated `process_payment()` to use Stripe transfers
- ✅ Automatic payout on verification (if Stripe account connected)
- ✅ Graceful fallback if no Stripe account (payment stays PENDING)

**Frontend** (`apps/web/app/(considerer)/earnings/page.tsx`):
- ✅ Balance display (Total, Pending, Paid Out)
- ✅ Stripe connection status banner
- ✅ "Connect with Stripe" onboarding flow
- ✅ Payment history with status indicators
- ✅ Link to Stripe Dashboard

**Configuration**:
- ✅ Added `resend` and `gunicorn` to `requirements.txt`
- ✅ Added `frontend_url` and `resend_api_key` to `config.py`

## 🔨 Ready to Implement (Remaining Tasks)

### 2. Email Notifications

**File to Create**: `apps/api/services/email.py`

```python
import resend
from config import settings

resend.api_key = settings.resend_api_key

class EmailService:
    async def send_verification_result(to_email, considerer_name, task_title, passed, combined_score, earned_amount):
        # Send email on verification
        pass

    async def send_new_response_to_buyer(to_email, buyer_name, campaign_title, responses_count, max_responses):
        # Notify buyer of new response
        pass

    async def send_campaign_complete(to_email, buyer_name, campaign_title, total_responses):
        # Notify when campaign reaches goal
        pass
```

**Integration Points**:
- In `apps/api/routers/proofs.py`, after line 235 (after payment processed)
- Add email notifications for both considerer and buyer

### 3. Verification Improvements

#### A. Redis Caching
**File**: `apps/api/services/verification/engine.py`

Add caching to avoid re-running verification on retries:
```python
import hashlib
from redis import Redis

# In VerificationEngine.__init__:
self.redis = Redis.from_url(settings.redis_url)

# In verify() method, check cache first:
cache_key = f"verify:{hashlib.sha256(proof_text.encode()).hexdigest()[:16]}"
cached = self.redis.get(cache_key)
if cached:
    return VerificationResult.from_json(cached)
# ... run verification ...
self.redis.setex(cache_key, 3600, result.to_json())
```

#### B. Perplexity-based AI Detection
**File**: `apps/api/services/verification/ai_detection.py`

Add GPT-2 perplexity calculation:
```python
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# In __init__:
self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
self.model = GPT2LMHeadModel.from_pretrained('gpt2')

# New method:
def _check_perplexity(self, text: str) -> float:
    # Lower perplexity = AI (too predictable)
    # Higher perplexity = Human (more surprising)
    # Return 0-1 score
    pass
```

### 4. Buyer Analytics Dashboard

**File**: `apps/web/app/(buyer)/campaigns/[id]/analytics/page.tsx`

Create dashboard with:
- Overview cards (responses, avg score, total spent)
- Score distribution bar chart (using recharts)
- Responses over time line chart
- Key themes/insights extraction

**Backend**: `apps/api/routers/campaigns.py`

```python
@router.get("/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str, ...):
    # Calculate score distribution
    # Group responses by date
    # Extract key themes
    return analytics_data
```

### 5. Response Export

**File**: `apps/api/routers/campaigns.py`

```python
@router.get("/{campaign_id}/export")
async def export_campaign_responses(campaign_id: str, format: str = "csv"):
    # Export as CSV or JSON
    # Return StreamingResponse for CSV
    pass
```

### 6. Rate Limiting

**File**: `apps/api/middleware/rate_limit.py`

```python
from fastapi import Request, HTTPException
from redis import Redis

class RateLimiter:
    def __init__(self, redis_url):
        self.redis = Redis.from_url(redis_url)

    async def check(self, key, limit, window_seconds):
        # Redis ZSET-based rate limiting
        pass
```

**Integration**: Add to `apps/api/main.py`:
```python
from middleware.rate_limit import rate_limit_middleware
app.middleware("http")(rate_limit_middleware)
```

### 7. Onboarding Flow

**File**: `apps/web/app/(considerer)/onboarding/page.tsx`

4-step wizard:
1. Welcome & how it works
2. Tips for high scores
3. Profile setup (name, bio, interests)
4. Practice task with instant feedback

### 8. Production Deployment

**Files Created**:
- `railway.toml` - Railway deployment config
- `vercel.json` - Vercel frontend config
- Updated `apps/api/Dockerfile` - Production optimizations

**Environment Variables**:
Update `.env.production` with all production keys.

## 📋 Implementation Priority

**Week 1** (Must Have for Launch):
1. ✅ Stripe Connect Integration
2. Email Notifications
3. Rate Limiting
4. Production Deployment

**Week 2** (Nice to Have):
5. Verification Improvements (caching + perplexity)
6. Analytics Dashboard
7. Response Export

**Week 3** (Polish):
8. Onboarding Flow
9. Testing & Bug Fixes
10. Documentation

## 🚀 Next Steps

### To Deploy Phase 2:

1. **Complete Email Service** (2 hours):
   ```bash
   # Create email service file
   # Integrate into proof verification
   # Test email sending
   ```

2. **Add Rate Limiting** (1 hour):
   ```bash
   # Create middleware
   # Add to main.py
   # Test limits
   ```

3. **Set Up Production** (3 hours):
   ```bash
   # Deploy API to Railway
   # Deploy frontend to Vercel
   # Configure domain & DNS
   # Set up production database
   # Configure environment variables
   # Test end-to-end
   ```

4. **Launch Checklist**:
   - [ ] Stripe Connect tested in production mode
   - [ ] Real money test transaction ($1)
   - [ ] Email notifications working
   - [ ] Rate limits verified
   - [ ] Database backed up
   - [ ] Error monitoring set up (Sentry)
   - [ ] First beta user onboarded

## 💡 Key Decisions Made

1. **Stripe Transfer vs Payout**: Using **Transfers** for instant payouts to connected accounts
2. **Email Provider**: **Resend** for simplicity and good developer experience
3. **Rate Limiting**: **Redis ZSET** for distributed rate limiting
4. **Deployment**: **Railway** (API) + **Vercel** (Frontend) for ease
5. **AI Detection**: **Hybrid approach** - heuristics + perplexity for balance of speed/accuracy

## 🔒 Security Notes

- All Stripe operations use test mode until launch checklist complete
- Rate limiting protects against abuse from day 1
- Clerk webhook secrets verified
- Stripe webhook secrets verified
- Database backups automated
- No sensitive data in logs

## 📊 Success Metrics

Track these after launch:
- Considerer signup → Stripe connect rate
- Proof submission → verification pass rate
- Verification → payment success rate
- Buyer campaign creation → activation rate
- Average response quality scores over time

## 🐛 Known Issues

1. Campaign funding not yet implemented (buyers can create but not fund)
2. Onboarding flow not yet built
3. Analytics dashboard not yet built
4. Email notifications not yet sent

## 📚 Documentation Needed

Before public launch:
- User guide for considerers
- User guide for buyers
- Stripe Connect setup walkthrough
- Verification score explanation
- FAQ for common issues

---

**Status**: Phase 2 is 30% complete. Critical payment infrastructure is done. Email, rate limiting, and deployment are next priorities.
