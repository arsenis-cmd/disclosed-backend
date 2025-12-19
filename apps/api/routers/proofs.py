from auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List
from datetime import datetime
from database import get_db
from schemas.proof import ProofCreate, ProofResponse
from services.verification import VerificationEngine, VerificationThresholds
from services.email import email_service
from config import get_settings

router = APIRouter()
settings = get_settings()
verification_engine = VerificationEngine()


async def process_payment(proof_id: str, buyer_id: str, considerer_id: str, bounty_amount: float, db):
    """Process payment for verified proof"""
    from routers.payments import create_stripe_transfer

    # Get considerer's Stripe account ID
    considerer_query = "SELECT stripe_account_id, display_name FROM \"User\" WHERE id = $1"
    considerer = await db.fetchrow(considerer_query, considerer_id)

    # Calculate fees
    protocol_fee = bounty_amount * (settings.protocol_fee_percent / 100)
    stripe_fee = bounty_amount * 0.0025  # 0.25% Stripe Connect fee
    net_amount = bounty_amount - protocol_fee - stripe_fee

    # Create payment record
    payment_query = """
        INSERT INTO "Payment" (
            id, proof_id, sender_id, receiver_id,
            gross_amount, protocol_fee, net_amount,
            status, created_at, updated_at
        )
        VALUES (
            gen_random_uuid()::text, $1, $2, $3,
            $4, $5, $6,
            'PENDING', NOW(), NOW()
        )
        RETURNING *
    """
    payment = await db.fetchrow(
        payment_query,
        proof_id,
        buyer_id,
        considerer_id,
        bounty_amount,
        protocol_fee,
        net_amount
    )

    # Process Stripe transfer if considerer has connected account
    if considerer['stripe_account_id']:
        try:
            transfer_id = await create_stripe_transfer(
                amount=net_amount,
                stripe_account_id=considerer['stripe_account_id'],
                proof_id=proof_id,
                description=f"Payout for proof {proof_id}"
            )

            # Update payment record with transfer ID
            update_payment_query = """
                UPDATE "Payment"
                SET
                    status = 'COMPLETED',
                    stripe_transfer_id = $1,
                    paid_at = NOW(),
                    updated_at = NOW()
                WHERE id = $2
            """
            await db.execute(update_payment_query, transfer_id, payment['id'])

        except Exception as e:
            # Log error but don't fail the verification
            print(f"Stripe transfer failed for proof {proof_id}: {str(e)}")
            # Keep payment as PENDING for manual review
    else:
        # No Stripe account - mark as PENDING until they connect
        pass

    # Update user earnings
    update_user_query = """
        UPDATE "User"
        SET total_earned = total_earned + $1, updated_at = NOW()
        WHERE id = $2
    """
    await db.execute(update_user_query, net_amount, considerer_id)

    return payment


@router.post("", response_model=ProofResponse, status_code=status.HTTP_201_CREATED)
async def submit_proof(
    proof_data: ProofCreate,
    clerk_id: str,
    background_tasks: BackgroundTasks,
    db=Depends(get_db)
):
    """Submit a proof for verification"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get task with campaign details
    task_query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE t.id = $1
    """
    task = await db.fetchrow(task_query, proof_data.task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify task is assigned to this user
    if task['assigned_to'] != user['id']:
        raise HTTPException(status_code=403, detail="Task not assigned to you")

    # Check if already submitted
    existing_proof_query = "SELECT * FROM \"Proof\" WHERE task_id = $1"
    existing_proof = await db.fetchrow(existing_proof_query, proof_data.task_id)

    if existing_proof:
        raise HTTPException(status_code=400, detail="Proof already submitted for this task")

    # Validate response length
    if len(proof_data.response_text) < task['proof_min_length']:
        raise HTTPException(
            status_code=400,
            detail=f"Response must be at least {task['proof_min_length']} characters"
        )

    if len(proof_data.response_text) > task['proof_max_length']:
        raise HTTPException(
            status_code=400,
            detail=f"Response must not exceed {task['proof_max_length']} characters"
        )

    # Create proof record
    started_at = datetime.fromisoformat(proof_data.metadata['startedAt'].replace('Z', '+00:00'))
    submitted_at = datetime.utcnow()

    insert_proof_query = """
        INSERT INTO "Proof" (
            id, task_id, considerer_id, response_text,
            started_at, submitted_at, time_spent_seconds, revision_count,
            status, created_at, updated_at
        )
        VALUES (
            gen_random_uuid()::text, $1, $2, $3,
            $4, $5, $6, $7,
            'PROCESSING', NOW(), NOW()
        )
        RETURNING *
    """
    proof = await db.fetchrow(
        insert_proof_query,
        proof_data.task_id,
        user['id'],
        proof_data.response_text,
        started_at,
        submitted_at,
        proof_data.metadata['timeSpentSeconds'],
        proof_data.metadata['revisionCount']
    )

    # Get existing proofs for novelty check
    existing_proofs_query = """
        SELECT p.response_text
        FROM "Proof" p
        JOIN "Task" t ON p.task_id = t.id
        WHERE t.campaign_id = $1 AND p.status = 'VERIFIED'
    """
    existing_proofs = await db.fetch(existing_proofs_query, task['campaign_id'])
    existing_proof_texts = [p['response_text'] for p in existing_proofs]

    # Run verification
    content_text = task['content_text'] or ""
    thresholds = VerificationThresholds(
        min_relevance=task['min_relevance'],
        min_novelty=task['min_novelty'],
        min_coherence=task['min_coherence'],
        min_combined=task['min_combined_score']
    )

    verification_result = await verification_engine.verify(
        proof_text=proof_data.response_text,
        content_text=content_text,
        content_type=task['content_type'],
        proof_prompt=task['proof_prompt'],
        existing_proofs=existing_proof_texts,
        metadata=proof_data.metadata,
        thresholds=thresholds
    )

    # Update proof with verification results
    new_status = 'VERIFIED' if verification_result.passed else 'REJECTED'

    update_proof_query = """
        UPDATE "Proof"
        SET
            status = $1,
            relevance_score = $2,
            novelty_score = $3,
            coherence_score = $4,
            effort_score = $5,
            ai_detection_score = $6,
            combined_score = $7,
            verification_notes = $8,
            verified_at = NOW(),
            updated_at = NOW()
        WHERE id = $9
        RETURNING *
    """
    updated_proof = await db.fetchrow(
        update_proof_query,
        new_status,
        verification_result.relevance_score,
        verification_result.novelty_score,
        verification_result.coherence_score,
        verification_result.effort_score,
        verification_result.ai_detection_score,
        verification_result.combined_score,
        verification_result.feedback,
        proof['id']
    )

    # Update user stats
    if verification_result.passed:
        update_user_stats_query = """
            UPDATE "User"
            SET
                total_proofs = total_proofs + 1,
                successful_proofs = successful_proofs + 1,
                reputation_score = (reputation_score * total_proofs + $1) / (total_proofs + 1),
                updated_at = NOW()
            WHERE id = $2
        """
        await db.execute(update_user_stats_query, verification_result.combined_score, user['id'])

        # Update campaign stats
        update_campaign_query = """
            UPDATE "Campaign"
            SET
                current_responses = current_responses + 1,
                budget_spent = budget_spent + $1,
                updated_at = NOW()
            WHERE id = $2
        """
        await db.execute(update_campaign_query, task['bounty_amount'], task['campaign_id'])

        # Process payment
        payment = await process_payment(
            proof['id'],
            task['buyer_id'],
            user['id'],
            task['bounty_amount'],
            db
        )

        # Build response with payment info
        response = dict(updated_proof)
        response['passed'] = True
        response['net_amount'] = payment['net_amount']

        # Get user details for email
        considerer_query = "SELECT email, display_name FROM \"User\" WHERE id = $1"
        considerer = await db.fetchrow(considerer_query, user['id'])

        buyer_query = "SELECT email, display_name FROM \"User\" WHERE id = $1"
        buyer = await db.fetchrow(buyer_query, task['buyer_id'])

        # Send email notifications (async in background)
        background_tasks.add_task(
            email_service.send_verification_result,
            to_email=considerer['email'],
            considerer_name=considerer['display_name'] or 'there',
            task_title=task['title'],
            passed=True,
            combined_score=verification_result.combined_score,
            earned_amount=payment['net_amount']
        )

        background_tasks.add_task(
            email_service.send_new_response_to_buyer,
            to_email=buyer['email'],
            buyer_name=buyer['display_name'] or 'there',
            campaign_title=task['title'],
            campaign_id=task['campaign_id'],
            responses_count=task['current_responses'],
            max_responses=task['max_responses']
        )

        # Check if campaign is complete
        if task['current_responses'] >= task['max_responses']:
            background_tasks.add_task(
                email_service.send_campaign_complete,
                to_email=buyer['email'],
                buyer_name=buyer['display_name'] or 'there',
                campaign_title=task['title'],
                campaign_id=task['campaign_id'],
                total_responses=task['current_responses']
            )

    else:
        # Failed verification
        update_user_stats_query = """
            UPDATE "User"
            SET total_proofs = total_proofs + 1, updated_at = NOW()
            WHERE id = $1
        """
        await db.execute(update_user_stats_query, user['id'])

        response = dict(updated_proof)
        response['passed'] = False
        response['net_amount'] = 0

        # Get user details for email
        considerer_query = "SELECT email, display_name FROM \"User\" WHERE id = $1"
        considerer = await db.fetchrow(considerer_query, user['id'])

        # Send failure notification
        background_tasks.add_task(
            email_service.send_verification_result,
            to_email=considerer['email'],
            considerer_name=considerer['display_name'] or 'there',
            task_title=task['title'],
            passed=False,
            combined_score=verification_result.combined_score,
            earned_amount=None
        )

    # Log verification for debugging
    log_query = """
        INSERT INTO "VerificationLog" (
            id, proof_id, raw_scores, model_versions, processing_time_ms, created_at
        )
        VALUES (
            gen_random_uuid()::text, $1, $2, $3, $4, NOW()
        )
    """
    await db.execute(
        log_query,
        proof['id'],
        {
            'relevance': verification_result.relevance_score,
            'novelty': verification_result.novelty_score,
            'coherence': verification_result.coherence_score,
            'effort': verification_result.effort_score,
            'ai_detection': verification_result.ai_detection_score,
            'combined': verification_result.combined_score
        },
        {'embedding_model': 'all-MiniLM-L6-v2'},
        verification_result.processing_time_ms
    )

    return response


@router.get("/{proof_id}", response_model=ProofResponse)
async def get_proof(proof_id: str, clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get proof details and scores"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get proof
    proof_query = "SELECT * FROM \"Proof\" WHERE id = $1"
    proof = await db.fetchrow(proof_query, proof_id)

    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")

    # Check authorization (must be the considerer or the buyer)
    task_query = """
        SELECT t.*, c.buyer_id
        FROM "Task" t
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE t.id = $1
    """
    task = await db.fetchrow(task_query, proof['task_id'])

    if proof['considerer_id'] != user['id'] and task['buyer_id'] != user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this proof")

    response = dict(proof)

    # If verified, get payment info
    if proof['status'] == 'VERIFIED':
        payment_query = "SELECT * FROM \"Payment\" WHERE proof_id = $1"
        payment = await db.fetchrow(payment_query, proof_id)
        if payment:
            response['passed'] = True
            response['net_amount'] = payment['net_amount']

    return response


@router.get("/my/proofs")
async def get_my_proofs(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get proof history for current user"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get proofs
    query = """
        SELECT p.*, c.title as campaign_title
        FROM "Proof" p
        JOIN "Task" t ON p.task_id = t.id
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE p.considerer_id = $1
        ORDER BY p.created_at DESC
    """
    proofs = await db.fetch(query, user['id'])

    return [dict(p) for p in proofs]
