from auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from database import get_db
from schemas.task import TaskResponse, TaskAccept

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def list_available_tasks(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """List available tasks for considerer"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get available tasks (not assigned or expired)
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t."campaignId" = c.id
        WHERE c.status = 'ACTIVE'
        AND (t."assignedTo" IS NULL OR t."expiresAt" < NOW())
        AND c."currentResponses" < c."maxResponses"
        ORDER BY c."bountyAmount" DESC, c."createdAt" DESC
        LIMIT 50
    """
    tasks = await db.fetch(query)

    result = []
    for task in tasks:
        task_dict = dict(task)
        # Separate campaign data
        campaign_data = {
            'id': task_dict['id'],
            'title': task_dict['title'],
            'description': task_dict['description'],
            'content_type': task_dict['contentType'],
            'content_text': task_dict.get('contentText'),
            'content_url': task_dict.get('contentUrl'),
            'proof_prompt': task_dict['proofPrompt'],
            'proof_min_length': task_dict['proofMinLength'],
            'proof_max_length': task_dict['proofMaxLength'],
            'proof_guidelines': task_dict.get('proofGuidelines'),
            'bounty_amount': task_dict['bountyAmount']
        }

        task_response = {
            'id': task_dict['id'],
            'campaign_id': task_dict['campaignId'],
            'assigned_to': task_dict.get('assignedTo'),
            'assigned_at': task_dict.get('assignedAt'),
            'expires_at': task_dict.get('expiresAt'),
            'created_at': task_dict['createdAt'],
            'updated_at': task_dict['updatedAt'],
            'campaign': campaign_data
        }
        result.append(task_response)

    return result


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get task details"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get task with campaign details
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t."campaignId" = c.id
        WHERE t.id = $1
    """
    task = await db.fetchrow(query, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_dict = dict(task)

    # Build campaign data
    campaign_data = {
        'id': task_dict['campaignId'],
        'title': task_dict['title'],
        'description': task_dict['description'],
        'content_type': task_dict['contentType'],
        'content_text': task_dict.get('content_text'),
        'content_url': task_dict.get('content_url'),
        'proof_prompt': task_dict['proofPrompt'],
        'proof_min_length': task_dict['proofMinLength'],
        'proof_max_length': task_dict['proofMaxLength'],
        'proof_guidelines': task_dict.get('proof_guidelines'),
        'bounty_amount': task_dict['bountyAmount']
    }

    return {
        'id': task_id,
        'campaign_id': task_dict['campaignId'],
        'assigned_to': task_dict.get('assigned_to'),
        'assigned_at': task_dict.get('assigned_at'),
        'expires_at': task_dict.get('expires_at'),
        'created_at': task_dict['createdAt'],
        'updated_at': task_dict['updatedAt'],
        'campaign': campaign_data
    }


@router.post("/{task_id}/accept")
async def accept_task(task_id: str, clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Accept/start a task"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get task
    task_query = "SELECT * FROM \"Task\" WHERE id = $1"
    task = await db.fetchrow(task_query, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task is available
    if task['assignedTo'] and task['expiresAt'] and task['expiresAt'] > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Task is already assigned")

    # Check if user already has a proof for this task
    proof_query = "SELECT * FROM \"Proof\" WHERE \"taskId\" = $1"
    existing_proof = await db.fetchrow(proof_query, task_id)

    if existing_proof:
        raise HTTPException(status_code=400, detail="Task already has a submission")

    # Assign task to user (expires in 24 hours)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    update_query = """
        UPDATE "Task"
        SET "assignedTo" = $1, "assignedAt" = NOW(), "expiresAt" = $2, "updatedAt" = NOW()
        WHERE id = $3
        RETURNING *
    """
    updated_task = await db.fetchrow(update_query, user['id'], expires_at, task_id)

    return {"message": "Task accepted", "task": dict(updated_task)}


@router.get("/my/tasks")
async def get_my_tasks(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get tasks assigned to current user"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE \"clerkId\" = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get assigned tasks
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t."campaignId" = c.id
        WHERE t."assignedTo" = $1
        AND t."expiresAt" > NOW()
        AND NOT EXISTS (
            SELECT 1 FROM "Proof" p WHERE p.task_id = t.id
        )
        ORDER BY t."assignedAt" DESC
    """
    tasks = await db.fetch(query, user['id'])

    result = []
    for task in tasks:
        task_dict = dict(task)
        campaign_data = {
            'id': task_dict['campaignId'],
            'title': task_dict['title'],
            'description': task_dict['description'],
            'content_type': task_dict['contentType'],
            'content_text': task_dict.get('content_text'),
            'content_url': task_dict.get('content_url'),
            'proof_prompt': task_dict['proofPrompt'],
            'proof_min_length': task_dict['proofMinLength'],
            'proof_max_length': task_dict['proofMaxLength'],
            'proof_guidelines': task_dict.get('proof_guidelines'),
            'bounty_amount': task_dict['bountyAmount']
        }

        task_response = {
            'id': task_dict['id'],
            'campaign_id': task_dict['campaignId'],
            'assigned_to': task_dict.get('assigned_to'),
            'assigned_at': task_dict.get('assigned_at'),
            'expires_at': task_dict.get('expires_at'),
            'created_at': task_dict['createdAt'],
            'updated_at': task_dict['updatedAt'],
            'campaign': campaign_data
        }
        result.append(task_response)

    return result
