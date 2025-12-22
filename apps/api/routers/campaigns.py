from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from database import get_db
from schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignAnalytics
from auth import get_current_user
from config import settings
import stripe

stripe.api_key = settings.stripe_secret_key
router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new campaign"""
    try:
        # Get user ID from clerkId (camelCase in database)
        user_query = "SELECT id, role FROM \"User\" WHERE \"clerkId\" = $1"
        user = await db.fetchrow(user_query, clerk_id)

        if not user:
            # Auto-create user if they don't exist (authenticated via JWT but not yet synced)
            insert_user_query = """
                INSERT INTO "User" (id, \"clerkId\", email, role, \"displayName\", \"createdAt\", \"updatedAt\")
                VALUES (gen_random_uuid()::text, $1, $2, 'BUYER', $3, NOW(), NOW())
                RETURNING id, role
            """
            # Use clerkId as email placeholder if not available
            user = await db.fetchrow(
                insert_user_query,
                clerk_id,
                f"{clerk_id}@temp.email",  # Placeholder email
                "User"  # Default display name
            )

        if user['role'] != 'BUYER':
            raise HTTPException(status_code=403, detail="Only buyers can create campaigns")
    except Exception as e:
        import traceback
        print(f"Error in create_campaign (user check): {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Calculate budget total
    budget_total = campaign_data.bounty_amount * campaign_data.max_responses

    # Insert campaign (use camelCase column names to match database)
    insert_query = """
        INSERT INTO "Campaign" (
            id, \"buyerId\", title, description, status,
            \"contentType\", \"contentText\", \"contentUrl\",
            \"proofPrompt\", \"proofMinLength\", \"proofMaxLength\", \"proofGuidelines\",
            \"minRelevance\", \"minNovelty\", \"minCoherence\", \"minCombinedScore\",
            \"bountyAmount\", \"maxResponses\", \"budgetTotal\", \"budgetSpent\",
            \"targetAudience\", \"startDate\", \"endDate\",
            \"createdAt\", \"updatedAt\"
        )
        VALUES (
            gen_random_uuid()::text, $1, $2, $3, 'DRAFT',
            $4, $5, $6,
            $7, $8, $9, $10,
            $11, $12, $13, $14,
            $15, $16, $17, 0,
            $18, $19, $20,
            NOW(), NOW()
        )
        RETURNING *
    """

    campaign = await db.fetchrow(
        insert_query,
        user['id'],
        campaign_data.title,
        campaign_data.description,
        campaign_data.content_type,
        campaign_data.content_text,
        campaign_data.content_url,
        campaign_data.proof_prompt,
        campaign_data.proof_min_length,
        campaign_data.proof_max_length,
        campaign_data.proof_guidelines,
        campaign_data.min_relevance,
        campaign_data.min_novelty,
        campaign_data.min_coherence,
        campaign_data.min_combined_score,
        campaign_data.bounty_amount,
        campaign_data.max_responses,
        budget_total,
        campaign_data.target_audience,
        campaign_data.start_date,
        campaign_data.end_date
    )

    return dict(campaign)


@router.post("/{campaign_id}/checkout")
async def create_checkout_session(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create Stripe checkout session for campaign payment"""
    # Get user
    user_query = "SELECT id, email FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    if campaign['status'] != 'DRAFT':
        raise HTTPException(status_code=400, detail="Campaign is not in DRAFT status")

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Campaign: {campaign["title"]}',
                        'description': f'{campaign["maxResponses"]} responses at ${campaign["bountyAmount"]:.2f} each',
                    },
                    'unit_amount': int(campaign['budgetTotal'] * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{settings.frontend_url}/dashboard?payment=success&campaign_id={campaign_id}',
            cancel_url=f'{settings.frontend_url}/campaigns/new?payment=canceled',
            client_reference_id=campaign_id,
            customer_email=user['email'],
            metadata={
                'campaign_id': campaign_id,
                'buyer_id': user['id'],
            }
        )

        return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List campaigns for current user (buyer)"""
    # Get user ID from clerkId
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaigns
    query = """
        SELECT * FROM "Campaign"
        WHERE \"buyerId\" = $1
        ORDER BY \"createdAt\" DESC
    """
    campaigns = await db.fetch(query, user['id'])

    return [dict(c) for c in campaigns]


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get campaign details"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Check ownership
    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this campaign")

    return dict(campaign)


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    clerk_id: str,
    db=Depends(get_db)
):
    """Update campaign"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check campaign ownership
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this campaign")

    # Build dynamic update query
    updates = []
    values = []
    param_count = 1

    for field, value in campaign_update.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ${param_count}")
        values.append(value)
        param_count += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(campaign_id)
    query = f"""
        UPDATE "Campaign"
        SET {", ".join(updates)}, updated_at = NOW()
        WHERE id = ${param_count}
        RETURNING *
    """

    updated_campaign = await db.fetchrow(query, *values)

    return dict(updated_campaign)


@router.post("/{campaign_id}/activate")
async def activate_campaign(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Activate campaign and create tasks"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    if campaign['status'] != 'DRAFT':
        raise HTTPException(status_code=400, detail="Campaign is not in DRAFT status")

    # TODO: Process payment for budget_total via Stripe

    # Update campaign status
    update_query = """
        UPDATE "Campaign"
        SET status = 'ACTIVE', \"startDate\" = NOW(), \"updatedAt\" = NOW()
        WHERE id = $1
        RETURNING *
    """
    updated_campaign = await db.fetchrow(update_query, campaign_id)

    # Create tasks
    for i in range(campaign['maxResponses']):
        insert_task_query = """
            INSERT INTO "Task" (id, \"campaignId\", \"createdAt\", \"updatedAt\")
            VALUES (gen_random_uuid()::text, $1, NOW(), NOW())
        """
        await db.execute(insert_task_query, campaign_id)

    return {"message": "Campaign activated", "campaign": dict(updated_campaign)}


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Pause campaign"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update status
    update_query = """
        UPDATE "Campaign"
        SET status = 'PAUSED', \"updatedAt\" = NOW()
        WHERE id = $1
        RETURNING *
    """
    updated_campaign = await db.fetchrow(update_query, campaign_id)

    return {"message": "Campaign paused", "campaign": dict(updated_campaign)}


@router.get("/{campaign_id}/responses")
async def get_campaign_responses(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get all verified responses for a campaign"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get verified proofs
    query = """
        SELECT p.*, u.\"displayName\", u.email
        FROM "Proof" p
        JOIN "Task" t ON p.\"taskId\" = t.id
        JOIN "User" u ON p.\"considererId\" = u.id
        WHERE t.\"campaignId\" = $1 AND p.status = 'VERIFIED'
        ORDER BY p.\"verifiedAt\" DESC
    """
    proofs = await db.fetch(query, campaign_id)

    return [dict(p) for p in proofs]


@router.get("/{campaign_id}/analytics", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: str,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get campaign analytics"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyerId'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get analytics
    analytics_query = """
        SELECT
            COUNT(*) as total_responses,
            COUNT(*) FILTER (WHERE p.status = 'VERIFIED') as verified_responses,
            COUNT(*) FILTER (WHERE p.status = 'REJECTED') as rejected_responses,
            AVG(p.\"relevanceScore\") FILTER (WHERE p.status = 'VERIFIED') as avg_relevance,
            AVG(p.\"noveltyScore\") FILTER (WHERE p.status = 'VERIFIED') as avg_novelty,
            AVG(p.\"coherenceScore\") FILTER (WHERE p.status = 'VERIFIED') as avg_coherence,
            AVG(p.\"combinedScore\") FILTER (WHERE p.status = 'VERIFIED') as avg_combined
        FROM "Proof" p
        JOIN "Task" t ON p.\"taskId\" = t.id
        WHERE t.\"campaignId\" = $1
    """
    analytics = await db.fetchrow(analytics_query, campaign_id)

    return {
        "total_responses": analytics['total_responses'] or 0,
        "verified_responses": analytics['verified_responses'] or 0,
        "rejected_responses": analytics['rejected_responses'] or 0,
        "average_relevance_score": analytics['avg_relevance'] or 0,
        "average_novelty_score": analytics['avg_novelty'] or 0,
        "average_coherence_score": analytics['avg_coherence'] or 0,
        "average_combined_score": analytics['avg_combined'] or 0,
        "budget_spent": campaign['budgetSpent'],
        "budget_remaining": campaign['budgetTotal'] - campaign['budgetSpent']
    }
