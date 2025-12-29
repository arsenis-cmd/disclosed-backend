"""
Lightweight AI detection without heavy ML models.

Uses linguistic heuristics instead of ML models to detect AI-generated text.
This avoids memory issues while still providing meaningful detection.
"""

import logging
import re
from typing import Dict, Any
from collections import Counter
import math

logger = logging.getLogger(__name__)


class LightweightDetector:
    """
    Lightweight AI detector using linguistic heuristics.

    No heavy ML models - uses statistical analysis of text patterns.
    """

    # Common AI phrases and patterns
    AI_PHRASES = [
        "it's important to note",
        "it is important to note",
        "it's worth noting",
        "it is worth noting",
        "in conclusion",
        "in summary",
        "to summarize",
        "as an AI",
        "as a language model",
        "i don't have personal",
        "i cannot provide",
        "delve into",
        "navigating the",
        "landscape of",
        "robust",
        "leverage",
        "facilitate",
        "comprehensive",
        "multifaceted",
        "holistic",
        "paradigm shift"
    ]

    def __init__(self):
        logger.info("LightweightDetector initialized")

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for AI-generation likelihood.

        Returns scores from 0-1 where higher = more human-like.
        """
        try:
            # Calculate individual metrics
            perplexity_score = self._calculate_perplexity(text)
            coherence_score = self._calculate_coherence(text)
            burstiness_score = self._calculate_burstiness(text)
            originality_score = self._calculate_originality(text)
            voice_score = self._calculate_personal_voice(text)
            pattern_score = self._calculate_pattern_score(text)

            # Build analysis
            analysis = {
                'perplexity': {
                    'score': perplexity_score,
                    'interpretation': self._interpret_perplexity(perplexity_score)
                },
                'coherence': {
                    'score': coherence_score,
                    'interpretation': self._interpret_coherence(coherence_score)
                },
                'burstiness': {
                    'score': burstiness_score,
                    'interpretation': self._interpret_burstiness(burstiness_score)
                },
                'originality': {
                    'score': originality_score,
                    'interpretation': self._interpret_originality(originality_score)
                },
                'personal_voice': {
                    'score': voice_score,
                    'interpretation': self._interpret_voice(voice_score)
                },
                'pattern_score': {
                    'score': pattern_score,
                    'interpretation': self._interpret_patterns(pattern_score)
                }
            }

            # Calculate overall score (weighted average)
            overall_score = (
                perplexity_score * 0.20 +
                coherence_score * 0.15 +
                burstiness_score * 0.20 +
                originality_score * 0.15 +
                voice_score * 0.15 +
                pattern_score * 0.15
            )

            # Confidence based on score variance
            scores = [perplexity_score, coherence_score, burstiness_score,
                     originality_score, voice_score, pattern_score]
            variance = sum((s - overall_score) ** 2 for s in scores) / len(scores)
            std_dev = math.sqrt(variance)
            confidence = max(0.0, min(1.0, 1.0 - std_dev))

            return {
                'score': round(overall_score, 3),
                'confidence': round(confidence, 3),
                'analysis': analysis
            }

        except Exception as e:
            logger.error(f"Detection error: {e}", exc_info=True)
            raise

    def _calculate_perplexity(self, text: str) -> float:
        """
        Estimate perplexity using word length and vocabulary diversity.
        Human text tends to have more varied word lengths.
        """
        words = text.lower().split()
        if len(words) < 10:
            return 0.5

        # Calculate word length variance
        word_lengths = [len(w) for w in words]
        avg_length = sum(word_lengths) / len(word_lengths)
        variance = sum((l - avg_length) ** 2 for l in word_lengths) / len(word_lengths)

        # Higher variance = more human
        # Normalize to 0-1 (variance typically 0-20)
        score = min(1.0, variance / 15.0)

        return round(score, 3)

    def _calculate_coherence(self, text: str) -> float:
        """
        Estimate coherence using sentence length variation.
        AI tends to have very uniform sentence lengths.
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            return 0.5

        # Calculate sentence length variance
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)

        # Moderate variance is good (not too uniform, not too chaotic)
        # AI tends to be very uniform (low variance)
        # Normalize: sweet spot is variance of 20-50
        if variance < 10:
            score = 0.3  # Too uniform (AI-like)
        elif variance < 30:
            score = 0.7  # Good variation
        elif variance < 60:
            score = 0.9  # Excellent variation
        else:
            score = 0.6  # Too chaotic

        return round(score, 3)

    def _calculate_burstiness(self, text: str) -> float:
        """
        Measure complexity variation (burstiness).
        Human writing has bursts of complex and simple sentences.
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            return 0.5

        # Complexity = avg word length + punctuation density
        complexities = []
        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            avg_word_len = sum(len(w) for w in words) / len(words)
            punct_count = len(re.findall(r'[,;:]', sentence))
            complexity = avg_word_len + (punct_count * 2)
            complexities.append(complexity)

        if not complexities:
            return 0.5

        # Calculate variance in complexity
        avg_complexity = sum(complexities) / len(complexities)
        variance = sum((c - avg_complexity) ** 2 for c in complexities) / len(complexities)

        # Higher variance = more bursty = more human
        score = min(1.0, variance / 30.0)

        return round(score, 3)

    def _calculate_originality(self, text: str) -> float:
        """
        Check for AI-typical phrases and clichés.
        """
        text_lower = text.lower()

        # Count AI phrases
        ai_phrase_count = 0
        for phrase in self.AI_PHRASES:
            ai_phrase_count += text_lower.count(phrase)

        # Penalize based on phrase density
        words = text.split()
        if len(words) < 50:
            phrase_density = 0
        else:
            phrase_density = (ai_phrase_count / len(words)) * 100

        # Convert to 0-1 score (higher = more original)
        if phrase_density == 0:
            score = 1.0
        elif phrase_density < 0.5:
            score = 0.8
        elif phrase_density < 1.0:
            score = 0.5
        elif phrase_density < 2.0:
            score = 0.3
        else:
            score = 0.1

        return round(score, 3)

    def _calculate_personal_voice(self, text: str) -> float:
        """
        Detect personal voice through first-person pronouns and opinions.
        """
        text_lower = text.lower()

        # Count personal indicators
        first_person = len(re.findall(r'\b(i|my|mine|myself|we|our|ours)\b', text_lower))
        opinions = len(re.findall(r'\b(i think|i believe|in my opinion|i feel|personally)\b', text_lower))
        contractions = len(re.findall(r"n't|'ll|'ve|'re|'m|'d", text_lower))

        # Calculate density
        words = text.split()
        word_count = len(words)

        if word_count < 50:
            return 0.5

        personal_density = ((first_person + opinions * 2 + contractions) / word_count) * 100

        # Convert to score
        if personal_density == 0:
            score = 0.2  # No personal voice
        elif personal_density < 1:
            score = 0.4
        elif personal_density < 3:
            score = 0.7
        elif personal_density < 6:
            score = 0.9
        else:
            score = 1.0  # Very personal

        return round(score, 3)

    def _calculate_pattern_score(self, text: str) -> float:
        """
        Detect AI-typical structural patterns.
        """
        # Check for overly structured lists
        list_markers = len(re.findall(r'^\d+\.|\n\d+\.|\n-|\n\*', text, re.MULTILINE))

        # Check for transition word overuse
        transitions = len(re.findall(r'\b(however|moreover|furthermore|additionally|consequently|therefore|thus|hence)\b', text.lower()))

        # Check for perfect grammar (lack of minor errors)
        # AI rarely makes small errors humans make
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)

        # AI tends to have very consistent sentence lengths around 15-25 words
        if 15 <= avg_sentence_length <= 25:
            consistency_penalty = 0.3
        else:
            consistency_penalty = 0.0

        words = text.split()
        word_count = len(words)

        if word_count < 50:
            return 0.5

        # Calculate penalties
        list_penalty = min(0.3, (list_markers / (word_count / 100)) * 0.1)
        transition_penalty = min(0.3, (transitions / (word_count / 100)) * 0.1)

        total_penalty = list_penalty + transition_penalty + consistency_penalty
        score = max(0.0, 1.0 - total_penalty)

        return round(score, 3)

    def _interpret_perplexity(self, score: float) -> str:
        if score > 0.7:
            return "High unpredictability - very human-like"
        elif score > 0.5:
            return "Moderate variation - likely human"
        elif score > 0.3:
            return "Low variation - possibly AI"
        else:
            return "Very predictable - likely AI"

    def _interpret_coherence(self, score: float) -> str:
        if score > 0.8:
            return "Natural logical flow"
        elif score > 0.6:
            return "Good coherence"
        elif score > 0.4:
            return "Moderate coherence"
        else:
            return "Overly uniform flow - AI-like"

    def _interpret_burstiness(self, score: float) -> str:
        if score > 0.7:
            return "High complexity variation - human-like"
        elif score > 0.5:
            return "Some variation present"
        elif score > 0.3:
            return "Low variation - possibly AI"
        else:
            return "Uniform complexity - likely AI"

    def _interpret_originality(self, score: float) -> str:
        if score > 0.7:
            return "Highly original phrasing"
        elif score > 0.5:
            return "Mostly original"
        elif score > 0.3:
            return "Some AI-typical phrases"
        else:
            return "Many AI patterns detected"

    def _interpret_voice(self, score: float) -> str:
        if score > 0.7:
            return "Strong personal perspective"
        elif score > 0.5:
            return "Some personal voice"
        elif score > 0.3:
            return "Weak personal voice"
        else:
            return "No personal perspective - likely AI"

    def _interpret_patterns(self, score: float) -> str:
        if score > 0.7:
            return "Few AI patterns detected"
        elif score > 0.5:
            return "Some AI-like patterns"
        elif score > 0.3:
            return "Multiple AI patterns"
        else:
            return "Strong AI signature detected"
