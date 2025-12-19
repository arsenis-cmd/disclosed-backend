from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from database import get_db
from schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignAnalytics
from auth import get_current_user

router = APIRouter()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new campaign"""
    # Get user ID from clerk_id
    user_query = "SELECT id, role FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user['role'] != 'BUYER':
        raise HTTPException(status_code=403, detail="Only buyers can create campaigns")

    # Calculate budget total
    budget_total = campaign_data.bounty_amount * campaign_data.max_responses

    # Insert campaign
    insert_query = """
        INSERT INTO "Campaign" (
            id, buyer_id, title, description, status,
            content_type, content_text, content_url,
            proof_prompt, proof_min_length, proof_max_length, proof_guidelines,
            min_relevance, min_novelty, min_coherence, min_combined_score,
            bounty_amount, max_responses, budget_total, budget_spent,
            target_audience, start_date, end_date,
            created_at, updated_at
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


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    clerk_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """List campaigns for current user (buyer)"""
    # Get user ID from clerk_id
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaigns
    query = """
        SELECT * FROM "Campaign"
        WHERE buyer_id = $1
        ORDER BY created_at DESC
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Check ownership
    if campaign['buyer_id'] != user['id']:
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check campaign ownership
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyer_id'] != user['id']:
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyer_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    if campaign['status'] != 'DRAFT':
        raise HTTPException(status_code=400, detail="Campaign is not in DRAFT status")

    # TODO: Process payment for budget_total via Stripe

    # Update campaign status
    update_query = """
        UPDATE "Campaign"
        SET status = 'ACTIVE', start_date = NOW(), updated_at = NOW()
        WHERE id = $1
        RETURNING *
    """
    updated_campaign = await db.fetchrow(update_query, campaign_id)

    # Create tasks
    for i in range(campaign['max_responses']):
        insert_task_query = """
            INSERT INTO "Task" (id, campaign_id, created_at, updated_at)
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyer_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update status
    update_query = """
        UPDATE "Campaign"
        SET status = 'PAUSED', updated_at = NOW()
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyer_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get verified proofs
    query = """
        SELECT p.*, u.display_name, u.email
        FROM "Proof" p
        JOIN "Task" t ON p.task_id = t.id
        JOIN "User" u ON p.considerer_id = u.id
        WHERE t.campaign_id = $1 AND p.status = 'VERIFIED'
        ORDER BY p.verified_at DESC
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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get campaign
    campaign_query = "SELECT * FROM \"Campaign\" WHERE id = $1"
    campaign = await db.fetchrow(campaign_query, campaign_id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign['buyer_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get analytics
    analytics_query = """
        SELECT
            COUNT(*) as total_responses,
            COUNT(*) FILTER (WHERE p.status = 'VERIFIED') as verified_responses,
            COUNT(*) FILTER (WHERE p.status = 'REJECTED') as rejected_responses,
            AVG(p.relevance_score) FILTER (WHERE p.status = 'VERIFIED') as avg_relevance,
            AVG(p.novelty_score) FILTER (WHERE p.status = 'VERIFIED') as avg_novelty,
            AVG(p.coherence_score) FILTER (WHERE p.status = 'VERIFIED') as avg_coherence,
            AVG(p.combined_score) FILTER (WHERE p.status = 'VERIFIED') as avg_combined
        FROM "Proof" p
        JOIN "Task" t ON p.task_id = t.id
        WHERE t.campaign_id = $1
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
        "budget_spent": campaign['budget_spent'],
        "budget_remaining": campaign['budget_total'] - campaign['budget_spent']
    }
