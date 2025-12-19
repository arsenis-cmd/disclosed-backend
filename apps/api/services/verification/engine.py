"""
Verification Engine - AID Integration
Adapter for the new AID (Algorithmic Irreducibility Detection) engine.
"""

from dataclasses import dataclass, asdict
from typing import Optional
import asyncio
import time
import hashlib
import json
import sys
import os

# Add parent directory to path to import aid module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aid import AIDEngine, AIDConfig


@dataclass
class VerificationResult:
    relevance_score: float      # 0-1
    novelty_score: float        # 0-1
    coherence_score: float      # 0-1
    effort_score: float         # 0-1
    ai_detection_score: float   # 0-1 (1 = human, 0 = AI)
    combined_score: float       # 0-1
    passed: bool
    feedback: str
    processing_time_ms: int

    def to_json(self) -> str:
        """Serialize to JSON for caching"""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> 'VerificationResult':
        """Deserialize from JSON"""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class VerificationThresholds:
    min_relevance: float = 0.65
    min_novelty: float = 0.70
    min_coherence: float = 0.60
    min_combined: float = 0.60


class VerificationEngine:
    """
    Main verification orchestrator using the AID engine.
    Maintains backward compatibility with existing API.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        # Initialize AID engine with configuration
        config = AIDConfig(
            perplexity_model="gpt2-medium",
            embedding_model="all-MiniLM-L6-v2",
            use_gpu=True,
            min_relevance=0.60,
            min_irreducibility=0.55,
            min_novelty=0.55,
            min_coherence=0.50,
            min_combined=0.55,
            enable_cache=True,
            cache_backend="memory",  # Use memory cache for now (redis optional)
            log_level="INFO"
        )

        print("Initializing AID verification engine...")
        self.aid_engine = AIDEngine(config)
        print("AID engine initialized successfully")

        # Redis caching (optional, AID has its own cache)
        self.cache_enabled = False
        self.redis = None

    async def verify(
        self,
        proof_text: str,
        content_text: str,
        content_type: str,
        proof_prompt: str,
        existing_proofs: list[str],  # Other proofs for this campaign (for novelty)
        metadata: dict,  # timing, revisions, etc.
        thresholds: VerificationThresholds
    ) -> VerificationResult:
        """
        Run full verification pipeline using AID engine.
        """
        start_time = time.time()

        # Convert threshold to AID format
        aid_thresholds = {
            'min_relevance': thresholds.min_relevance,
            'min_irreducibility': 0.55,  # Use default from AID config
            'min_novelty': thresholds.min_novelty,
            'min_coherence': thresholds.min_coherence,
            'min_combined': thresholds.min_combined
        }

        # Run AID verification
        aid_result = await self.aid_engine.verify(
            response=proof_text,
            content=content_text,
            prompt=proof_prompt,
            existing_responses=existing_proofs,
            metadata=metadata,
            custom_thresholds=aid_thresholds
        )

        processing_time = int((time.time() - start_time) * 1000)

        # Convert AID result to legacy VerificationResult format
        result = VerificationResult(
            relevance_score=round(aid_result.relevance.combined, 3),
            novelty_score=round(aid_result.novelty.combined, 3),
            coherence_score=round(aid_result.coherence.combined, 3),
            effort_score=round(aid_result.effort.combined, 3),
            ai_detection_score=round(aid_result.ai_detection.combined, 3),
            combined_score=round(aid_result.combined_score, 3),
            passed=aid_result.passed,
            feedback=aid_result.feedback_summary,
            processing_time_ms=processing_time
        )

        return result
