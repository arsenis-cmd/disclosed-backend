from auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import get_db
from config import get_settings
import stripe

router = APIRouter()
settings = get_settings()
stripe.api_key = settings.stripe_secret_key


@router.post("/connect/onboard")
async def create_stripe_connect_account(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Create Stripe Connect Express account for considerer"""
    # Get user
    user_query = "SELECT id, email, display_name FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if account already exists
    if user.get('stripe_account_id'):
        # Return existing account
        account = stripe.Account.retrieve(user['stripe_account_id'])

        # Generate new onboarding link if needed
        if not account.charges_enabled or not account.payouts_enabled:
            account_link = stripe.AccountLink.create(
                account=user['stripe_account_id'],
                refresh_url=f"{settings.frontend_url}/earnings/setup?refresh=true",
                return_url=f"{settings.frontend_url}/earnings/setup?success=true",
                type="account_onboarding"
            )
            return {"url": account_link.url, "account_id": user['stripe_account_id']}

        return {"account_id": user['stripe_account_id'], "status": "active"}

    # Create new Connect Express account
    try:
        account = stripe.Account.create(
            type="express",
            email=user['email'],
            capabilities={
                "transfers": {"requested": True},
            },
            business_type="individual",
            metadata={
                "user_id": user['id'],
                "clerk_id": clerk_id
            }
        )

        # Save account ID to user
        update_query = """
            UPDATE "User"
            SET stripe_account_id = $1, updated_at = NOW()
            WHERE id = $2
        """
        await db.execute(update_query, account.id, user['id'])

        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f"{settings.frontend_url}/earnings/setup?refresh=true",
            return_url=f"{settings.frontend_url}/earnings/setup?success=true",
            type="account_onboarding"
        )

        return {
            "url": account_link.url,
            "account_id": account.id
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/connect/status")
async def get_stripe_connect_status(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Check if considerer's Stripe account is ready for payouts"""
    # Get user
    user_query = "SELECT stripe_account_id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user['stripe_account_id']:
        return {
            "connected": False,
            "charges_enabled": False,
            "payouts_enabled": False
        }

    try:
        account = stripe.Account.retrieve(user['stripe_account_id'])

        return {
            "connected": True,
            "account_id": account.id,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "details_submitted": account.details_submitted,
            "requirements": {
                "currently_due": account.requirements.currently_due if account.requirements else [],
                "eventually_due": account.requirements.eventually_due if account.requirements else []
            }
        }

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/connect/dashboard")
async def get_stripe_dashboard_link(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get Stripe Express dashboard URL for considerer"""
    # Get user
    user_query = "SELECT stripe_account_id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user['stripe_account_id']:
        raise HTTPException(
            status_code=400,
            detail="Please connect your Stripe account first"
        )

    try:
        login_link = stripe.Account.create_login_link(user['stripe_account_id'])
        return {"url": login_link.url}

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my")
async def get_my_payments(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get payment history for current user"""
    # Get user
    user_query = "SELECT id, role FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user['role'] == 'CONSIDERER':
        # Get payments received
        query = """
            SELECT p.*, pr.response_text, c.title as campaign_title
            FROM "Payment" p
            JOIN "Proof" pr ON p.proof_id = pr.id
            JOIN "Task" t ON pr.task_id = t.id
            JOIN "Campaign" c ON t.campaign_id = c.id
            WHERE p.receiver_id = $1
            ORDER BY p.created_at DESC
        """
    else:
        # Get payments sent (buyer)
        query = """
            SELECT p.*, pr.response_text, c.title as campaign_title
            FROM "Payment" p
            JOIN "Proof" pr ON p.proof_id = pr.id
            JOIN "Task" t ON pr.task_id = t.id
            JOIN "Campaign" c ON t.campaign_id = c.id
            WHERE p.sender_id = $1
            ORDER BY p.created_at DESC
        """

    payments = await db.fetch(query, user['id'])

    return [dict(p) for p in payments]


@router.get("/balance")
async def get_balance(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get pending balance for considerer"""
    # Get user
    user_query = "SELECT id, role FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user['role'] != 'CONSIDERER':
        raise HTTPException(status_code=403, detail="Only considerers have a balance")

    # Get pending and completed payments
    query = """
        SELECT
            COALESCE(SUM(net_amount) FILTER (WHERE status = 'PENDING'), 0) as pending,
            COALESCE(SUM(net_amount) FILTER (WHERE status = 'COMPLETED'), 0) as available
        FROM "Payment"
        WHERE receiver_id = $1
    """
    balance = await db.fetchrow(query, user['id'])

    return {
        "pending": balance['pending'],
        "available": balance['available'],
        "total": balance['pending'] + balance['available']
    }


async def create_stripe_transfer(
    amount: float,
    stripe_account_id: str,
    proof_id: str,
    description: str
) -> str:
    """Create a Stripe transfer to a Connect account"""
    try:
        # Convert to cents
        amount_cents = int(amount * 100)

        transfer = stripe.Transfer.create(
            amount=amount_cents,
            currency="usd",
            destination=stripe_account_id,
            description=description,
            metadata={"proof_id": proof_id}
        )

        return transfer.id

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe transfer failed: {str(e)}")
