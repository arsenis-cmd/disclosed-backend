"""
Simple text detector wrapper around AID engine.

Adapts the complex AID engine (designed for proof verification)
to simple standalone text detection.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SimpleDetector:
    """
    Simplified detector for standalone text analysis.

    The AID engine was designed for campaign proof verification,
    but we can use it for general AI detection by:
    1. Using the text itself as both "response" and "content"
    2. Using a generic prompt
    3. Focusing on the AI detection scores
    """

    _engine = None  # Class-level lazy-loaded engine

    def __init__(self):
        logger.info("SimpleDetector initialized (engine will load on first use)")

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return AI/Human detection scores.

        Returns:
            {
                'score': float (0-1, higher = more human),
                'confidence': float (0-1),
                'analysis': {
                    'perplexity': {...},
                    'coherence': {...},
                    'burstiness': {...},
                    'originality': {...},
                    'personal_voice': {...},
                    'pattern_score': {...}
                }
            }
        """
        try:
            # Lazy load the AID engine on first use
            if SimpleDetector._engine is None:
                logger.info("Loading AID engine for first time...")
                from aid.engine import AIDEngine
                from aid.types import AIDConfig
                config = AIDConfig()
                SimpleDetector._engine = AIDEngine(config)
                logger.info("AID engine loaded successfully")

            # For standalone detection, we use the text as both response and content
            # with a generic prompt
            generic_prompt = "Provide your thoughts on this content."

            # Run AID verification
            result = SimpleDetector._engine.verify(
                response=text,
                content=text,  # Self-referential
                prompt=generic_prompt,
                existing_responses=[],  # No corpus comparison
                metadata={
                    'time_spent_seconds': None,  # Unknown for standalone text
                    'revision_count': 0
                }
            )

            # Extract the key scores we care about for AI detection
            analysis = {
                'perplexity': {
                    'score': result.perplexity.irreducibility_score,
                    'interpretation': self._interpret_perplexity(
                        result.perplexity.irreducibility_score
                    )
                },
                'coherence': {
                    'score': result.coherence.combined,
                    'interpretation': self._interpret_coherence(
                        result.coherence.combined
                    )
                },
                'burstiness': {
                    'score': result.ai_detection.burstiness_score,
                    'interpretation': self._interpret_burstiness(
                        result.ai_detection.burstiness_score
                    )
                },
                'originality': {
                    'score': result.novelty.combined,
                    'interpretation': self._interpret_originality(
                        result.novelty.combined
                    )
                },
                'personal_voice': {
                    'score': result.ai_detection.personality_score,
                    'interpretation': self._interpret_voice(
                        result.ai_detection.personality_score
                    )
                },
                'pattern_score': {
                    'score': result.ai_detection.phrase_score,
                    'interpretation': self._interpret_patterns(
                        result.ai_detection.phrase_score
                    )
                }
            }

            # Calculate overall score
            # Weight the AI detection components more heavily
            overall_score = (
                result.perplexity.irreducibility_score * 0.20 +
                result.coherence.combined * 0.15 +
                result.ai_detection.burstiness_score * 0.20 +
                result.novelty.combined * 0.15 +
                result.ai_detection.personality_score * 0.15 +
                result.ai_detection.phrase_score * 0.15
            )

            # Confidence is based on how much scores agree
            scores = [
                result.perplexity.irreducibility_score,
                result.coherence.combined,
                result.ai_detection.burstiness_score,
                result.novelty.combined,
                result.ai_detection.personality_score,
                result.ai_detection.phrase_score
            ]

            # High agreement = high confidence
            import numpy as np
            confidence = 1.0 - min(1.0, np.std(scores))

            return {
                'score': round(overall_score, 3),
                'confidence': round(confidence, 3),
                'analysis': analysis,
                'raw_result': {
                    'perplexity_score': result.perplexity.irreducibility_score,
                    'ai_likelihood': result.ai_detection.combined,
                    'processing_time_ms': result.processing_time_ms
                }
            }

        except Exception as e:
            logger.error(f"Detection error: {e}", exc_info=True)
            raise

    def _interpret_perplexity(self, score: float) -> str:
        """Interpret perplexity score."""
        if score > 0.8:
            return "High unpredictability - very human-like"
        elif score > 0.6:
            return "Moderate variation - likely human"
        elif score > 0.4:
            return "Low variation - possibly AI"
        else:
            return "Very predictable - likely AI"

    def _interpret_coherence(self, score: float) -> str:
        """Interpret coherence score."""
        if score > 0.8:
            return "Natural logical flow"
        elif score > 0.6:
            return "Good coherence"
        elif score > 0.4:
            return "Moderate coherence"
        else:
            return "Disconnected or over-perfect flow"

    def _interpret_burstiness(self, score: float) -> str:
        """Interpret burstiness score."""
        if score > 0.7:
            return "High complexity variation - human-like"
        elif score > 0.5:
            return "Some variation present"
        elif score > 0.3:
            return "Low variation - possibly AI"
        else:
            return "Uniform complexity - likely AI"

    def _interpret_originality(self, score: float) -> str:
        """Interpret originality score."""
        if score > 0.7:
            return "Highly original phrasing"
        elif score > 0.5:
            return "Mostly original"
        elif score > 0.3:
            return "Some common phrases"
        else:
            return "Many AI-typical phrases"

    def _interpret_voice(self, score: float) -> str:
        """Interpret personal voice score."""
        if score > 0.7:
            return "Strong personal perspective"
        elif score > 0.5:
            return "Some personal voice"
        elif score > 0.3:
            return "Weak personal voice"
        else:
            return "No personal perspective - likely AI"

    def _interpret_patterns(self, score: float) -> str:
        """Interpret AI pattern score."""
        if score > 0.7:
            return "Few AI patterns detected"
        elif score > 0.5:
            return "Some AI-like patterns"
        elif score > 0.3:
            return "Multiple AI patterns"
        else:
            return "Strong AI signature detected"
