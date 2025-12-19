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
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get available tasks (not assigned or expired)
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE c.status = 'ACTIVE'
        AND (t.assigned_to IS NULL OR t.expires_at < NOW())
        AND c.current_responses < c.max_responses
        ORDER BY c.bounty_amount DESC, c.created_at DESC
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
            'content_type': task_dict['content_type'],
            'content_text': task_dict.get('content_text'),
            'content_url': task_dict.get('content_url'),
            'proof_prompt': task_dict['proof_prompt'],
            'proof_min_length': task_dict['proof_min_length'],
            'proof_max_length': task_dict['proof_max_length'],
            'proof_guidelines': task_dict.get('proof_guidelines'),
            'bounty_amount': task_dict['bounty_amount']
        }

        task_response = {
            'id': task_dict['id'],
            'campaign_id': task_dict['campaign_id'],
            'assigned_to': task_dict.get('assigned_to'),
            'assigned_at': task_dict.get('assigned_at'),
            'expires_at': task_dict.get('expires_at'),
            'created_at': task_dict['created_at'],
            'updated_at': task_dict['updated_at'],
            'campaign': campaign_data
        }
        result.append(task_response)

    return result


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get task details"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get task with campaign details
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE t.id = $1
    """
    task = await db.fetchrow(query, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_dict = dict(task)

    # Build campaign data
    campaign_data = {
        'id': task_dict['campaign_id'],
        'title': task_dict['title'],
        'description': task_dict['description'],
        'content_type': task_dict['content_type'],
        'content_text': task_dict.get('content_text'),
        'content_url': task_dict.get('content_url'),
        'proof_prompt': task_dict['proof_prompt'],
        'proof_min_length': task_dict['proof_min_length'],
        'proof_max_length': task_dict['proof_max_length'],
        'proof_guidelines': task_dict.get('proof_guidelines'),
        'bounty_amount': task_dict['bounty_amount']
    }

    return {
        'id': task_id,
        'campaign_id': task_dict['campaign_id'],
        'assigned_to': task_dict.get('assigned_to'),
        'assigned_at': task_dict.get('assigned_at'),
        'expires_at': task_dict.get('expires_at'),
        'created_at': task_dict['created_at'],
        'updated_at': task_dict['updated_at'],
        'campaign': campaign_data
    }


@router.post("/{task_id}/accept")
async def accept_task(task_id: str, clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Accept/start a task"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get task
    task_query = "SELECT * FROM \"Task\" WHERE id = $1"
    task = await db.fetchrow(task_query, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task is available
    if task['assigned_to'] and task['expires_at'] and task['expires_at'] > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Task is already assigned")

    # Check if user already has a proof for this task
    proof_query = "SELECT * FROM \"Proof\" WHERE task_id = $1"
    existing_proof = await db.fetchrow(proof_query, task_id)

    if existing_proof:
        raise HTTPException(status_code=400, detail="Task already has a submission")

    # Assign task to user (expires in 24 hours)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    update_query = """
        UPDATE "Task"
        SET assigned_to = $1, assigned_at = NOW(), expires_at = $2, updated_at = NOW()
        WHERE id = $3
        RETURNING *
    """
    updated_task = await db.fetchrow(update_query, user['id'], expires_at, task_id)

    return {"message": "Task accepted", "task": dict(updated_task)}


@router.get("/my/tasks")
async def get_my_tasks(clerk_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get tasks assigned to current user"""
    # Get user
    user_query = "SELECT id FROM \"User\" WHERE clerk_id = $1"
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get assigned tasks
    query = """
        SELECT t.*, c.*
        FROM "Task" t
        JOIN "Campaign" c ON t.campaign_id = c.id
        WHERE t.assigned_to = $1
        AND t.expires_at > NOW()
        AND NOT EXISTS (
            SELECT 1 FROM "Proof" p WHERE p.task_id = t.id
        )
        ORDER BY t.assigned_at DESC
    """
    tasks = await db.fetch(query, user['id'])

    result = []
    for task in tasks:
        task_dict = dict(task)
        campaign_data = {
            'id': task_dict['campaign_id'],
            'title': task_dict['title'],
            'description': task_dict['description'],
            'content_type': task_dict['content_type'],
            'content_text': task_dict.get('content_text'),
            'content_url': task_dict.get('content_url'),
            'proof_prompt': task_dict['proof_prompt'],
            'proof_min_length': task_dict['proof_min_length'],
            'proof_max_length': task_dict['proof_max_length'],
            'proof_guidelines': task_dict.get('proof_guidelines'),
            'bounty_amount': task_dict['bounty_amount']
        }

        task_response = {
            'id': task_dict['id'],
            'campaign_id': task_dict['campaign_id'],
            'assigned_to': task_dict.get('assigned_to'),
            'assigned_at': task_dict.get('assigned_at'),
            'expires_at': task_dict.get('expires_at'),
            'created_at': task_dict['created_at'],
            'updated_at': task_dict['updated_at'],
            'campaign': campaign_data
        }
        result.append(task_response)

    return result
