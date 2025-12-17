from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskResponse(BaseModel):
    id: str
    campaign_id: str
    assigned_to: Optional[str]
    assigned_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Include campaign details for convenience
    campaign: Optional[dict] = None

    class Config:
        from_attributes = True


class TaskAccept(BaseModel):
    task_id: str
