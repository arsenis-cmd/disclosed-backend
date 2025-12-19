"""
AID Engine - Main Orchestrator

Combines all scoring components and produces final result.
"""

import time
import hashlib
import asyncio
from typing import Dict, List, Optional, Any
import numpy as np
import logging

from .types import (
    AIDConfig, AIDResult, VerificationStatus,
    PerplexityScores, RelevanceScores, NoveltyScores,
    CoherenceScores, EffortScores, AIDetectionScores,
    VerificationRequest
)
from .perplexity import PerplexityScorer
from .relevance import RelevanceScorer
from .novelty import NoveltyScorer
from .coherence import CoherenceScorer
from .effort import EffortEstimator
from .ai_detection import AIDetector

logger = logging.getLogger(__name__)


class AIDEngine:
    """
    Main AID verification engine.
    """

    def __init__(self, config: AIDConfig = None):
        self.config = config or AIDConfig()
        self._cache = {}
        self._init_scorers()

    def _init_scorers(self):
        """Initialize all scoring components."""
        logger.info("Initializing AID engine...")

        self.perplexity_scorer = PerplexityScorer(
            model_name=self.config.perplexity_model,
            use_gpu=self.config.use_gpu
        )
        self.relevance_scorer = RelevanceScorer(self.config.embedding_model)
        self.novelty_scorer = NoveltyScorer(self.config.embedding_model)
        self.coherence_scorer = CoherenceScorer(self.config.embedding_model)
        self.effort_estimator = EffortEstimator()
        self.ai_detector = AIDetector()

        logger.info("AID engine ready")

    def _cache_key(self, response: str, content: str) -> str:
        """Generate cache key."""
        return hashlib.sha256(f"{response}|{content}".encode()).hexdigest()[:16]

    def _calculate_combined_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted geometric mean of all scores.
        """
        weights = {
            'relevance': self.config.weight_relevance,
            'irreducibility': self.config.weight_irreducibility_content,
            'novelty': self.config.weight_novelty,
            'coherence': self.config.weight_coherence,
            'effort': self.config.weight_effort,
            'ai_detection': self.config.weight_irreducibility_ai
        }

        eps = 0.01
        log_sum = sum(
            weights[k] * np.log(scores[k] + eps)
            for k in weights
        )
        weight_sum = sum(weights.values())

        combined = np.exp(log_sum / weight_sum) - eps
        return float(max(0, min(1, combined)))

    def _check_thresholds(
        self,
        scores: Dict[str, float],
        thresholds: Dict[str, float]
    ) -> bool:
        """Check if scores meet thresholds."""
        return (
            scores['relevance'] >= thresholds['min_relevance'] and
            scores['irreducibility'] >= thresholds['min_irreducibility'] and
            scores['novelty'] >= thresholds['min_novelty'] and
            scores['coherence'] >= thresholds['min_coherence'] and
            scores['combined'] >= thresholds['min_combined']
        )

    def _generate_feedback(
        self,
        scores: Dict[str, float],
        thresholds: Dict[str, float],
        passed: bool
    ) -> tuple:
        """Generate human-readable feedback."""
        if passed:
            return "Response verified successfully!", []

        details = []

        if scores['relevance'] < thresholds['min_relevance']:
            details.append("Engage more directly with the content")
        if scores['irreducibility'] < thresholds['min_irreducibility']:
            details.append("Add more personal perspective beyond summarizing")
        if scores['novelty'] < thresholds['min_novelty']:
            details.append("Make your response more unique and specific")
        if scores['coherence'] < thresholds['min_coherence']:
            details.append("Improve response structure and clarity")
        if scores['ai_detection'] < 0.4:
            details.append("Response shows AI-like patterns")

        summary = f"Verification failed: {details[0]}" if details else "Below threshold"
        return summary, details

    async def verify(
        self,
        response: str,
        content: str,
        prompt: str,
        existing_responses: List[str] = None,
        metadata: Dict[str, Any] = None,
        custom_thresholds: Dict[str, float] = None
    ) -> AIDResult:
        """
        Run complete verification.
        """
        start_time = time.time()
        existing_responses = existing_responses or []
        metadata = metadata or {}

        # Check cache
        cache_key = self._cache_key(response, content)
        if self.config.enable_cache and cache_key in self._cache:
            cached = self._cache[cache_key]
            cached.cache_hit = True
            return cached

        # Active thresholds
        thresholds = {
            'min_relevance': custom_thresholds.get('min_relevance', self.config.min_relevance) if custom_thresholds else self.config.min_relevance,
            'min_irreducibility': custom_thresholds.get('min_irreducibility', self.config.min_irreducibility) if custom_thresholds else self.config.min_irreducibility,
            'min_novelty': custom_thresholds.get('min_novelty', self.config.min_novelty) if custom_thresholds else self.config.min_novelty,
            'min_coherence': custom_thresholds.get('min_coherence', self.config.min_coherence) if custom_thresholds else self.config.min_coherence,
            'min_combined': custom_thresholds.get('min_combined', self.config.min_combined) if custom_thresholds else self.config.min_combined,
        }

        try:
            # Run all scorers
            perplexity_raw = self.perplexity_scorer.score(response, content)
            relevance_raw = self.relevance_scorer.score(response, content, prompt)
            novelty_raw = self.novelty_scorer.score(response, content, existing_responses)
            coherence_raw = self.coherence_scorer.score(response)
            effort_raw = self.effort_estimator.score(response, content, metadata)
            ai_raw = self.ai_detector.score(response)

            # Extract combined scores
            scores = {
                'relevance': relevance_raw['combined'],
                'irreducibility': perplexity_raw['irreducibility_score'],
                'novelty': novelty_raw['combined'],
                'coherence': coherence_raw['combined'],
                'effort': effort_raw['combined'],
                'ai_detection': ai_raw['human_likelihood']
            }

            # Calculate combined
            scores['combined'] = self._calculate_combined_score(scores)

            # Check pass/fail
            passed = self._check_thresholds(scores, thresholds)

            # Generate feedback
            feedback, details = self._generate_feedback(scores, thresholds, passed)

            processing_time = int((time.time() - start_time) * 1000)

            # Build result
            result = AIDResult(
                status=VerificationStatus.PASSED if passed else VerificationStatus.FAILED,
                passed=passed,
                combined_score=scores['combined'],
                relevance=RelevanceScores(
                    content_similarity=relevance_raw['content_similarity'],
                    prompt_similarity=relevance_raw['prompt_similarity'],
                    keyword_overlap=relevance_raw['keyword_overlap'],
                    concept_coverage=0,
                    topic_coherence=relevance_raw['topic_coherence'],
                    combined=relevance_raw['combined']
                ),
                perplexity=PerplexityScores(
                    unconditional=perplexity_raw['unconditional_perplexity'],
                    conditional=perplexity_raw['conditional_perplexity'],
                    reduction_ratio=perplexity_raw['reduction_ratio'],
                    irreducibility_score=perplexity_raw['irreducibility_score'],
                    ai_likelihood_score=perplexity_raw['ai_likelihood_score'],
                    tokens_analyzed=perplexity_raw['tokens_analyzed'],
                    model_used=perplexity_raw['model']
                ),
                novelty=NoveltyScores(
                    content_distance=novelty_raw['content_distance'],
                    corpus_distance=novelty_raw['corpus_novelty'],
                    max_corpus_similarity=novelty_raw['max_corpus_similarity'],
                    personalization=novelty_raw['personalization'],
                    template_score=novelty_raw['template_score'],
                    combined=novelty_raw['combined']
                ),
                coherence=CoherenceScores(
                    structure=coherence_raw['structure'],
                    flow=coherence_raw['flow'],
                    completeness=coherence_raw['completeness'],
                    semantic_coherence=coherence_raw['semantic_coherence'],
                    length_score=coherence_raw['length'],
                    combined=coherence_raw['combined']
                ),
                effort=EffortScores(
                    time_score=effort_raw['time'],
                    complexity_score=effort_raw['complexity'],
                    revision_score=effort_raw['revision'],
                    typing_score=0,
                    combined=effort_raw['combined'],
                    flags=effort_raw.get('flags', [])
                ),
                ai_detection=AIDetectionScores(
                    phrase_score=ai_raw['phrase_score'],
                    pattern_score=0,
                    burstiness_score=ai_raw['burstiness_score'],
                    personality_score=ai_raw['personality_score'],
                    perfection_penalty=0,
                    combined=ai_raw['human_likelihood'],
                    confidence=0.7
                ),
                thresholds_applied=thresholds,
                feedback_summary=feedback,
                feedback_details=details,
                improvement_suggestions=details,
                processing_time_ms=processing_time,
                model_versions={
                    'perplexity': self.config.perplexity_model,
                    'embedding': self.config.embedding_model
                }
            )

            # Cache
            if self.config.enable_cache:
                self._cache[cache_key] = result

            logger.info(f"Verification: passed={passed}, score={scores['combined']:.3f}, time={processing_time}ms")

            return result

        except Exception as e:
            logger.error(f"Verification error: {e}", exc_info=True)
            raise

    def verify_sync(self, *args, **kwargs) -> AIDResult:
        """Synchronous wrapper."""
        return asyncio.run(self.verify(*args, **kwargs))
