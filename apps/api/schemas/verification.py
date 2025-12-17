from pydantic import BaseModel


class VerificationResponse(BaseModel):
    relevance_score: float
    novelty_score: float
    coherence_score: float
    effort_score: float
    ai_detection_score: float
    combined_score: float
    passed: bool
    feedback: str
    processing_time_ms: int
