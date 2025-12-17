from dataclasses import dataclass, asdict
from typing import Optional
import asyncio
import time
import hashlib
import json
from redis import Redis

from .relevance import RelevanceScorer
from .novelty import NoveltyScorer
from .coherence import CoherenceScorer
from .effort import EffortEstimator
from .ai_detection import AIDetector


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
    Main verification orchestrator.
    Coordinates all scoring components and produces final result.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.relevance_scorer = RelevanceScorer()
        self.novelty_scorer = NoveltyScorer()
        self.coherence_scorer = CoherenceScorer()
        self.effort_estimator = EffortEstimator()
        self.ai_detector = AIDetector()

        # Redis for caching
        try:
            self.redis = Redis.from_url(redis_url, decode_responses=True)
            self.redis.ping()  # Test connection
            self.cache_enabled = True
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.redis = None
            self.cache_enabled = False

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
        Run full verification pipeline with caching.
        """
        # Check cache first (same proof text = same scores)
        cache_key = None
        if self.cache_enabled:
            # Create cache key from proof text
            text_hash = hashlib.sha256(proof_text.encode()).hexdigest()[:16]
            cache_key = f"verify:{text_hash}"

            try:
                cached = self.redis.get(cache_key)
                if cached:
                    print(f"Cache hit for verification: {cache_key}")
                    return VerificationResult.from_json(cached)
            except Exception as e:
                print(f"Cache read error: {e}")

        start_time = time.time()

        # Run all scorers in parallel
        relevance_task = self.relevance_scorer.score(proof_text, content_text, proof_prompt)
        novelty_task = self.novelty_scorer.score(proof_text, content_text, existing_proofs)
        coherence_task = self.coherence_scorer.score(proof_text)
        effort_task = self.effort_estimator.score(proof_text, content_text, metadata)
        ai_task = self.ai_detector.score(proof_text)

        results = await asyncio.gather(
            relevance_task,
            novelty_task,
            coherence_task,
            effort_task,
            ai_task
        )

        relevance_score, novelty_score, coherence_score, effort_score, ai_score = results

        # Combined score formula
        # All components must be reasonable; low scores in any area tank the combined
        combined_score = (
            relevance_score *
            novelty_score *
            coherence_score *
            effort_score *
            ai_score
        ) ** (1/5)  # Geometric mean

        # Determine pass/fail
        passed = (
            relevance_score >= thresholds.min_relevance and
            novelty_score >= thresholds.min_novelty and
            coherence_score >= thresholds.min_coherence and
            combined_score >= thresholds.min_combined
        )

        # Generate feedback
        feedback = self._generate_feedback(
            relevance_score, novelty_score, coherence_score,
            effort_score, ai_score, thresholds, passed
        )

        processing_time = int((time.time() - start_time) * 1000)

        result = VerificationResult(
            relevance_score=round(relevance_score, 3),
            novelty_score=round(novelty_score, 3),
            coherence_score=round(coherence_score, 3),
            effort_score=round(effort_score, 3),
            ai_detection_score=round(ai_score, 3),
            combined_score=round(combined_score, 3),
            passed=passed,
            feedback=feedback,
            processing_time_ms=processing_time
        )

        # Cache result for 1 hour (in case of retries/disputes)
        if self.cache_enabled and cache_key:
            try:
                self.redis.setex(cache_key, 3600, result.to_json())
                print(f"Cached verification result: {cache_key}")
            except Exception as e:
                print(f"Cache write error: {e}")

        return result

    def _generate_feedback(self, rel, nov, coh, eff, ai, thresholds, passed) -> str:
        if passed:
            return "Your response demonstrated genuine consideration. Thank you!"

        issues = []
        if rel < thresholds.min_relevance:
            issues.append("Response didn't engage enough with the specific content")
        if nov < thresholds.min_novelty:
            issues.append("Response was too similar to other submissions or generic")
        if coh < thresholds.min_coherence:
            issues.append("Response lacked clear logical structure")
        if ai < 0.5:
            issues.append("Response showed patterns typical of AI-generated content")
        if eff < 0.5:
            issues.append("Response appeared to require minimal effort")

        return "Verification failed: " + "; ".join(issues)
