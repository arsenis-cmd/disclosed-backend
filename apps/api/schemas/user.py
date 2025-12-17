from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    clerk_id: str
    email: EmailStr
    role: str = "CONSIDERER"
    display_name: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    company_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    clerk_id: str
    email: str
    role: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    reputation_score: float
    total_proofs: int
    successful_proofs: int
    total_earned: float
    company_name: Optional[str]
    stripe_customer_id: Optional[str]
    stripe_account_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserStats(BaseModel):
    total_proofs: int
    successful_proofs: int
    success_rate: float
    total_earned: float
    reputation_score: float
    average_score: Optional[float]
