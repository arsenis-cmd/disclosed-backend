# Proof of Consideration - MVP

A marketplace where buyers pay for verified human attention and considerers earn money by demonstrating genuine cognitive engagement with content.

## Overview

Proof of Consideration is a two-sided marketplace with:
- **Considerers**: Browse tasks, submit thoughtful responses, earn money
- **Buyers**: Create campaigns, receive verified human responses, pay bounties

The core innovation is the **AI-powered verification engine** that scores responses on:
- **Relevance**: How well the response engages with the content
- **Novelty**: Originality and unique personal insights
- **Coherence**: Logical structure and completeness
- **Effort**: Time and thought invested
- **AI Detection**: Verification that the response is genuinely human

## Tech Stack

- **Frontend**: Next.js 14 (App Router), Tailwind CSS, shadcn/ui
- **Backend**: Python FastAPI
- **Database**: PostgreSQL with Prisma ORM
- **Cache**: Redis
- **Auth**: Clerk
- **Payments**: Stripe Connect
- **ML/Verification**: sentence-transformers, transformers
- **Monorepo**: Turborepo

## Project Structure

```
poc/
├── apps/
│   ├── web/                 # Next.js frontend
│   └── api/                 # FastAPI backend
├── packages/
│   ├── database/           # Prisma schema
│   └── shared/             # Shared types and constants
├── docker-compose.yml
└── README.md
```

## Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional, for containerized setup)

## Quick Start (Docker)

The easiest way to get started is using Docker Compose:

### 1. Clone and Setup

```bash
git clone <your-repo>
cd disclosed
```

### 2. Configure Environment Variables

```bash
# Copy environment templates
cp .env.example .env
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env
```

Edit `.env` and add your API keys:
- **Clerk**: Sign up at https://clerk.com
- **Stripe**: Get test keys from https://stripe.com

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)

### 4. Initialize Database

```bash
# Run Prisma migrations
cd packages/database
npx prisma generate
npx prisma db push
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Prisma Studio**: `npx prisma studio` (in packages/database)

## Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
# Install root dependencies
npm install

# Install backend dependencies
cd apps/api
pip install -r requirements.txt

# Install frontend dependencies
cd ../web
npm install
```

### 2. Setup Database

```bash
# Start PostgreSQL and Redis locally
# Then run:
cd packages/database
npx prisma generate
npx prisma db push
```

### 3. Start Development Servers

```bash
# Terminal 1 - Backend
cd apps/api
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd apps/web
npm run dev
```

## Core Workflows

### Considerer Flow

1. **Browse Tasks**: `/tasks`
   - View available tasks with bounty amounts
   - See content type and requirements

2. **Accept Task**: Click "Accept Task"
   - Task is assigned to you for 24 hours

3. **Submit Response**: `/tasks/[id]/submit`
   - Read/watch the content
   - Write thoughtful response (tracked for time/effort)
   - Submit for verification

4. **Get Results**:
   - See verification scores instantly
   - If passed: get paid immediately
   - If failed: see feedback on what to improve

### Buyer Flow

1. **Create Campaign**: `/campaigns/new`
   - Set title, description
   - Add content (text, video, image, URL)
   - Define response requirements
   - Set verification thresholds
   - Configure budget (bounty × max responses)

2. **Activate Campaign**:
   - Review and activate
   - Budget is escrowed
   - Tasks become available to considerers

3. **View Responses**: `/campaigns/[id]/responses`
   - See all verified responses
   - View individual scores and analytics

## Verification Engine

The verification engine runs automatically when a proof is submitted:

```python
# apps/api/services/verification/engine.py

1. Relevance Scoring (all-MiniLM-L6-v2)
   - Semantic similarity to content
   - Keyword coverage
   - Prompt addressing

2. Novelty Scoring
   - Distance from original content
   - Uniqueness vs other responses
   - Personal elements detection
   - Template pattern detection

3. Coherence Scoring
   - Length appropriateness
   - Sentence structure variety
   - Logical flow (connectors)
   - Completeness

4. Effort Estimation
   - Time spent vs response length
   - Complexity relative to content
   - Revision count

5. AI Detection
   - AI-typical phrase detection
   - Perfection vs human quirks
   - Personality markers
   - Sentence variance (burstiness)

Combined Score = Geometric Mean of all 5 scores
```

## API Endpoints

### Users
- `POST /api/v1/users/sync` - Sync user from Clerk
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `GET /api/v1/users/me/stats` - Get statistics

### Campaigns (Buyer)
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns` - List my campaigns
- `GET /api/v1/campaigns/:id` - Get campaign details
- `POST /api/v1/campaigns/:id/activate` - Activate campaign
- `GET /api/v1/campaigns/:id/responses` - Get responses
- `GET /api/v1/campaigns/:id/analytics` - Get analytics

### Tasks (Considerer)
- `GET /api/v1/tasks` - List available tasks
- `GET /api/v1/tasks/:id` - Get task details
- `POST /api/v1/tasks/:id/accept` - Accept task
- `GET /api/v1/tasks/my` - Get my active tasks

### Proofs
- `POST /api/v1/proofs` - Submit proof (triggers verification)
- `GET /api/v1/proofs/:id` - Get proof details
- `GET /api/v1/proofs/my` - Get my proof history

### Verification
- `POST /api/v1/verify` - Standalone verification (testing)
- `GET /api/v1/verify/health` - Health check

### Payments
- `GET /api/v1/payments/my` - Payment history
- `GET /api/v1/payments/balance` - Current balance
- `POST /api/v1/payments/withdraw` - Request withdrawal

## Database Schema

See `packages/database/prisma/schema.prisma` for the complete schema.

Key models:
- **User**: Profiles for considerers and buyers
- **Campaign**: Buyer-created campaigns
- **Task**: Individual response slots
- **Proof**: Submitted responses with scores
- **Payment**: Payment records and escrow
- **VerificationLog**: Detailed verification data

## Environment Variables

### Required

```bash
# Clerk Authentication
CLERK_SECRET_KEY=sk_test_xxxxx
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_xxxxx

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Database
DATABASE_URL=postgresql://poc:poc_dev_password@localhost:5432/poc
```

### Optional

```bash
# Redis
REDIS_URL=redis://localhost:6379

# Business Settings
PROTOCOL_FEE_PERCENT=7

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Test the Verification Engine

```bash
curl -X POST http://localhost:8000/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "proof_text": "I really enjoyed this content. It made me think about...",
    "content_text": "Sample content here",
    "content_type": "text",
    "proof_prompt": "What did you think?",
    "existing_proofs": [],
    "metadata": {
      "timeSpentSeconds": 120,
      "revisionCount": 2
    }
  }'
```

### Test API Endpoints

Visit http://localhost:8000/docs for interactive API documentation.

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Frontend: Changes to `apps/web` reload automatically
- Backend: Changes to `apps/api` reload automatically (with `--reload` flag)

### Database Changes

When modifying the Prisma schema:

```bash
cd packages/database
npx prisma generate  # Regenerate Prisma Client
npx prisma db push   # Push schema to database
```

### View Database

```bash
cd packages/database
npx prisma studio
```

Opens at http://localhost:5555

## Deployment

### Backend (FastAPI)

Deploy to any platform supporting Python:
- Railway, Render, Fly.io, Heroku
- Configure production DATABASE_URL
- Set all environment variables
- Run: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend (Next.js)

Deploy to Vercel (recommended):
```bash
cd apps/web
vercel
```

Or any Node.js hosting platform.

### Database

Use managed PostgreSQL:
- Supabase (free tier)
- Railway (free tier)
- Neon (free tier)
- AWS RDS, Google Cloud SQL

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection
psql postgresql://poc:poc_dev_password@localhost:5432/poc
```

### ML Models Not Loading

First-time setup downloads ~100MB of ML models:
- sentence-transformers/all-MiniLM-L6-v2
- May take a few minutes on first API startup

## Security Notes

- Never commit `.env` files
- Use test Stripe keys in development
- Clerk secret keys should never be exposed to frontend
- In production, use environment-specific secrets
- Enable Stripe webhooks for production payments

## Roadmap

- [ ] Video content support
- [ ] Image content support
- [ ] Campaign analytics dashboard
- [ ] Reputation system enhancements
- [ ] Dispute resolution flow
- [ ] Email notifications
- [ ] Mobile responsive improvements
- [ ] Admin panel

## License

MIT

## Support

For issues, please open a GitHub issue or contact support.
