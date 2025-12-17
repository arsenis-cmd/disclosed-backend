from fastapi import APIRouter, Depends
from services.verification import VerificationEngine, VerificationThresholds
from schemas.verification import VerificationResponse
from pydantic import BaseModel

router = APIRouter()
verification_engine = VerificationEngine()


class VerificationRequest(BaseModel):
    proof_text: str
    content_text: str
    content_type: str
    proof_prompt: str
    existing_proofs: list[str] = []
    metadata: dict
    thresholds: dict = {}


@router.post("", response_model=VerificationResponse)
async def verify_proof(request: VerificationRequest):
    """
    Standalone verification endpoint for testing.
    In production, verification happens automatically during proof submission.
    """
    thresholds = VerificationThresholds(
        min_relevance=request.thresholds.get('min_relevance', 0.65),
        min_novelty=request.thresholds.get('min_novelty', 0.70),
        min_coherence=request.thresholds.get('min_coherence', 0.60),
        min_combined=request.thresholds.get('min_combined', 0.60)
    )

    result = await verification_engine.verify(
        proof_text=request.proof_text,
        content_text=request.content_text,
        content_type=request.content_type,
        proof_prompt=request.proof_prompt,
        existing_proofs=request.existing_proofs,
        metadata=request.metadata,
        thresholds=thresholds
    )

    return result


@router.get("/health")
async def health_check():
    """Check if verification service is healthy"""
    return {
        "status": "healthy",
        "models_loaded": True,
        "services": {
            "relevance_scorer": True,
            "novelty_scorer": True,
            "coherence_scorer": True,
            "effort_estimator": True,
            "ai_detector": True
        }
    }
