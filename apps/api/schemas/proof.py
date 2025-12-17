from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProofCreate(BaseModel):
    task_id: str
    response_text: str
    metadata: dict  # Contains timeSpentSeconds, revisionCount, startedAt


class ProofResponse(BaseModel):
    id: str
    task_id: str
    considerer_id: str
    response_text: str
    started_at: datetime
    submitted_at: datetime
    time_spent_seconds: int
    revision_count: int
    status: str
    relevance_score: Optional[float]
    novelty_score: Optional[float]
    coherence_score: Optional[float]
    effort_score: Optional[float]
    ai_detection_score: Optional[float]
    combined_score: Optional[float]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    # For considerer's view
    passed: Optional[bool] = None
    net_amount: Optional[float] = None

    class Config:
        from_attributes = True
