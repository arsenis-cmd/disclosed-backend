from pydantic import BaseModel, Field, ConfigDict
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
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    buyer_id: str = Field(alias="buyerId")
    title: str
    description: str
    status: str
    content_type: str = Field(alias="contentType")
    content_text: Optional[str] = Field(alias="contentText")
    content_url: Optional[str] = Field(alias="contentUrl")
    proof_prompt: str = Field(alias="proofPrompt")
    proof_min_length: int = Field(alias="proofMinLength")
    proof_max_length: int = Field(alias="proofMaxLength")
    proof_guidelines: Optional[str] = Field(alias="proofGuidelines")
    min_relevance: float = Field(alias="minRelevance")
    min_novelty: float = Field(alias="minNovelty")
    min_coherence: float = Field(alias="minCoherence")
    min_combined_score: float = Field(alias="minCombinedScore")
    bounty_amount: float = Field(alias="bountyAmount")
    max_responses: int = Field(alias="maxResponses")
    current_responses: int = Field(alias="currentResponses")
    budget_total: float = Field(alias="budgetTotal")
    budget_spent: float = Field(alias="budgetSpent")
    target_audience: Optional[Dict[str, Any]] = Field(alias="targetAudience")
    start_date: Optional[datetime] = Field(alias="startDate")
    end_date: Optional[datetime] = Field(alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


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
