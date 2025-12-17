from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from database import get_db
from schemas.user import UserCreate, UserUpdate, UserResponse, UserStats

router = APIRouter()


@router.post("/sync", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sync_user(user_data: UserCreate, db=Depends(get_db)):
    """Sync user from Clerk webhook"""
    # Check if user exists
    query = "SELECT * FROM \"User\" WHERE clerk_id = $1"
    existing_user = await db.fetchrow(query, user_data.clerk_id)

    if existing_user:
        # Update existing user
        update_query = """
            UPDATE "User"
            SET email = $1, display_name = $2, updated_at = NOW()
            WHERE clerk_id = $3
            RETURNING *
        """
        user = await db.fetchrow(
            update_query,
            user_data.email,
            user_data.display_name,
            user_data.clerk_id
        )
    else:
        # Create new user
        insert_query = """
            INSERT INTO "User" (id, clerk_id, email, role, display_name, created_at, updated_at)
            VALUES (gen_random_uuid()::text, $1, $2, $3, $4, NOW(), NOW())
            RETURNING *
        """
        user = await db.fetchrow(
            insert_query,
            user_data.clerk_id,
            user_data.email,
            user_data.role,
            user_data.display_name
        )

    return dict(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user(clerk_id: str, db=Depends(get_db)):
    """Get current user profile"""
    query = "SELECT * FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    clerk_id: str,
    user_update: UserUpdate,
    db=Depends(get_db)
):
    """Update current user profile"""
    # Build dynamic update query
    updates = []
    values = []
    param_count = 1

    for field, value in user_update.model_dump(exclude_unset=True).items():
        updates.append(f"{field} = ${param_count}")
        values.append(value)
        param_count += 1

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    values.append(clerk_id)
    query = f"""
        UPDATE "User"
        SET {", ".join(updates)}, updated_at = NOW()
        WHERE clerk_id = ${param_count}
        RETURNING *
    """

    user = await db.fetchrow(query, *values)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)


@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(clerk_id: str, db=Depends(get_db)):
    """Get user statistics"""
    # Get user
    user_query = "SELECT * FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get average score
    avg_query = """
        SELECT AVG(combined_score) as avg_score
        FROM "Proof"
        WHERE considerer_id = $1 AND status = 'VERIFIED'
    """
    avg_result = await db.fetchrow(avg_query, user['id'])

    return {
        "total_proofs": user['total_proofs'],
        "successful_proofs": user['successful_proofs'],
        "success_rate": user['successful_proofs'] / user['total_proofs'] if user['total_proofs'] > 0 else 0,
        "total_earned": user['total_earned'],
        "reputation_score": user['reputation_score'],
        "average_score": avg_result['avg_score'] if avg_result['avg_score'] else None
    }


@router.post("/me/stripe-account")
async def create_stripe_account(clerk_id: str, db=Depends(get_db)):
    """Create Stripe Connect account for considerer to receive payouts"""
    # TODO: Implement Stripe Connect account creation
    # This will be implemented in the payments integration
    raise HTTPException(status_code=501, detail="Not implemented yet")
