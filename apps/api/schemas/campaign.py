from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CampaignCreate(BaseModel):
    title: str
    description: str
    content_type: str
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    proof_prompt: str
    proof_min_length: int = 100
    proof_max_length: int = 2000
    proof_guidelines: Optional[str] = None
    min_relevance: float = 0.65
    min_novelty: float = 0.70
    min_coherence: float = 0.60
    min_combined_score: float = 0.60
    bounty_amount: float
    max_responses: int
    target_audience: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    bounty_amount: Optional[float] = None
    max_responses: Optional[int] = None
    end_date: Optional[datetime] = None


class CampaignResponse(BaseModel):
    id: str
    buyer_id: str
    title: str
    description: str
    status: str
    content_type: str
    content_text: Optional[str]
    content_url: Optional[str]
    proof_prompt: str
    proof_min_length: int
    proof_max_length: int
    proof_guidelines: Optional[str]
    min_relevance: float
    min_novelty: float
    min_coherence: float
    min_combined_score: float
    bounty_amount: float
    max_responses: int
    current_responses: int
    budget_total: float
    budget_spent: float
    target_audience: Optional[Dict[str, Any]]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CampaignAnalytics(BaseModel):
    total_responses: int
    verified_responses: int
    rejected_responses: int
    average_relevance_score: float
    average_novelty_score: float
    average_coherence_score: float
    average_combined_score: float
    budget_spent: float
    budget_remaining: float
