"""
Detection API endpoints for AI text detection
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import hashlib
import logging
import json
import secrets
from datetime import datetime

from auth import get_current_user
from database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


def generate_cuid() -> str:
    """Generate a CUID-like ID (simplified version)"""
    import time
    timestamp = int(time.time() * 1000)
    random_part = secrets.token_urlsafe(16)
    return f"c{timestamp}{random_part}"[:25]


class DetectRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=50000)
    detailed: bool = True


class DetectResponse(BaseModel):
    id: str
    score: float
    verdict: str
    confidence: float
    word_count: int
    analysis: Optional[Dict[str, Any]] = None
    can_verify: bool
    created_at: str


@router.post("/detect", response_model=DetectResponse)
async def detect_text(
    request: DetectRequest,
    req: Request,
    clerk_id: Optional[str] = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Detect if text is AI-generated or human-written.

    Returns scores across 6 dimensions:
    - Perplexity (unpredictability)
    - Coherence (natural flow)
    - Burstiness (complexity variation)
    - Originality (unique phrasing)
    - Personal Voice (author perspective)
    - Pattern Score (AI pattern detection)
    """
    text = request.text.strip()

    # Validate word count
    words = text.split()
    word_count = len(words)

    if word_count < 50:
        raise HTTPException(
            status_code=400,
            detail="Minimum 50 words required for accurate detection"
        )

    if word_count > 10000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10,000 words for free tier"
        )

    # Generate text hash for caching
    text_hash = hashlib.sha256(text.encode()).hexdigest()

    # Check if we've already analyzed this exact text
    cached_query = """
        SELECT id, score, verdict, confidence, "wordCount", analysis, "isVerified",
               "certificateId", "createdAt"
        FROM "Detection"
        WHERE "textHash" = $1
        ORDER BY "createdAt" DESC
        LIMIT 1
    """
    cached = await db.fetchrow(cached_query, text_hash)

    if cached:
        logger.info(f"Cache hit for text hash: {text_hash[:8]}...")
        # Parse analysis if it's a string (from JSONB)
        analysis_data = cached['analysis']
        if isinstance(analysis_data, str):
            analysis_data = json.loads(analysis_data)

        return DetectResponse(
            id=cached['id'],
            score=float(cached['score']),
            verdict=cached['verdict'].lower(),
            confidence=float(cached['confidence']),
            word_count=cached['wordCount'],
            analysis=analysis_data if request.detailed else None,
            can_verify=float(cached['score']) >= 0.60 and not cached['isVerified'],
            created_at=cached['createdAt'].isoformat()
        )

    # Run AI detection with ZeroGPT (fallback to heuristic)
    try:
        from services.zerogpt_detector import ZeroGPTDetector
        from services.simple_detector import LightweightDetector
        import os

        api_provider = "heuristic"  # Default
        raw_response = None

        # Try ZeroGPT API first if API key is configured
        if os.getenv('RAPIDAPI_KEY'):
            try:
                detector = ZeroGPTDetector()
                result = await detector.analyze(text)
                api_provider = "zerogpt"
                raw_response = result.get('raw_response')
                logger.info(f"Using ZeroGPT API for detection")
            except Exception as api_error:
                logger.warning(f"ZeroGPT API failed, falling back to heuristic: {api_error}")
                # Fall back to heuristic detector
                detector = LightweightDetector()
                result = detector.analyze(text)
                api_provider = "heuristic_fallback"
        else:
            # No API key - use heuristic
            logger.info("No RAPIDAPI_KEY set, using heuristic detector")
            detector = LightweightDetector()
            result = detector.analyze(text)

        # Map to our verdict system
        score = result['score']
        if score < 0.30:
            verdict = "LIKELY_AI"
        elif score < 0.60:
            verdict = "MIXED"
        elif score < 0.85:
            verdict = "LIKELY_HUMAN"
        else:
            verdict = "HIGHLY_HUMAN"

        # Get user ID if authenticated
        user_id = None
        if clerk_id:
            user_query = 'SELECT id FROM "User" WHERE "clerkId" = $1'
            user = await db.fetchrow(user_query, clerk_id)
            user_id = user['id'] if user else None

        # Get IP address for rate limiting
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent", "")[:500]

        # Store detection with FULL TEXT for ML training
        detection_id = generate_cuid()
        insert_query = """
            INSERT INTO "Detection" (
                id, "userId", "textHash", "textContent", "textPreview", "wordCount",
                "score", "verdict", "confidence", "analysis",
                "apiProvider", "apiRawResponse",
                "ipAddress", "userAgent"
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id, "createdAt"
        """

        detection = await db.fetchrow(
            insert_query,
            detection_id,
            user_id,
            text_hash,
            text,  # FULL TEXT for ML training
            text[:500],  # Preview
            word_count,
            score,
            verdict,
            result['confidence'],
            json.dumps(result['analysis'] if request.detailed else {}),
            api_provider,  # Track which API was used
            json.dumps(raw_response) if raw_response else None,  # Store raw API response
            ip_address,
            user_agent
        )

        logger.info(
            f"Detection completed: id={detection['id']}, score={score:.3f}, "
            f"verdict={verdict}, words={word_count}"
        )

        return DetectResponse(
            id=detection['id'],
            score=score,
            verdict=verdict.lower(),
            confidence=result['confidence'],
            word_count=word_count,
            analysis=result['analysis'] if request.detailed else None,
            can_verify=score >= 0.60,
            created_at=detection['createdAt'].isoformat()
        )

    except Exception as e:
        logger.error(f"Detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Detection engine error. Please try again."
        )


@router.get("/detections", response_model=list)
async def get_detections(
    clerk_id: str = Depends(get_current_user),
    db = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """
    Get user's detection history.
    """
    # Get user ID
    user_query = 'SELECT id FROM "User" WHERE "clerkId" = $1'
    user = await db.fetchrow(user_query, clerk_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = """
        SELECT id, score, verdict, "wordCount", "textPreview",
               "isVerified", "certificateId", "createdAt"
        FROM "Detection"
        WHERE "userId" = $1
        ORDER BY "createdAt" DESC
        LIMIT $2 OFFSET $3
    """

    detections = await db.fetch(query, user['id'], limit, offset)

    return [
        {
            "id": d['id'],
            "score": float(d['score']),
            "verdict": d['verdict'].lower(),
            "word_count": d['wordCount'],
            "preview": d['textPreview'],
            "is_verified": d['isVerified'],
            "certificate_id": d['certificateId'],
            "created_at": d['createdAt'].isoformat()
        }
        for d in detections
    ]
