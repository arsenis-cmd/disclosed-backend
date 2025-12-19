"""
AI Detection Module

Detects AI-generated content using heuristics:
1. AI-typical phrases
2. Human markers
3. Writing rhythm (burstiness)
4. Personality signals
"""

import numpy as np
from typing import Dict, List
import re
import logging

logger = logging.getLogger(__name__)


AI_PHRASES = [
    "as an ai", "i cannot", "it's important to note",
    "it's worth noting", "that being said", "furthermore",
    "moreover", "additionally", "delve", "crucial",
    "facilitate", "utilize", "leverage", "comprehensive",
    "in conclusion", "to summarize", "let me"
]

HUMAN_MARKERS = [
    "don't", "can't", "won't", "i'm", "i've",
    "yeah", "yep", "nope", "kinda", "gonna",
    "tbh", "imo", "lol", "haha", "i think",
    "i guess", "maybe", "probably", "actually",
    "honestly", "basically", "wow", "oh", "hmm"
]


class AIDetector:
    """
    Detects AI-generated content.
    """

    def calculate_phrase_score(self, text: str) -> Dict[str, float]:
        """
        Check for AI vs human phrases.
        """
        text_lower = text.lower()
        word_count = len(text.split())

        ai_count = sum(1 for p in AI_PHRASES if p in text_lower)
        human_count = sum(1 for m in HUMAN_MARKERS if m in text_lower)

        ai_density = (ai_count / max(word_count, 1)) * 100
        human_density = (human_count / max(word_count, 1)) * 100

        if ai_density > 4:
            ai_score = 0.25
        elif ai_density > 2:
            ai_score = 0.5
        else:
            ai_score = 0.85

        if human_density > 2:
            human_score = 0.9
        elif human_density > 0.5:
            human_score = 0.7
        else:
            human_score = 0.5

        return {
            "ai_phrase_count": ai_count,
            "human_marker_count": human_count,
            "phrase_score": 0.5 * ai_score + 0.5 * human_score
        }

    def calculate_burstiness(self, text: str) -> Dict[str, float]:
        """
        Measure writing rhythm variance.
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

        if len(sentences) < 3:
            return {"burstiness_score": 0.6}

        lengths = [len(s.split()) for s in sentences]
        cv = np.std(lengths) / (np.mean(lengths) + 1e-8)

        if cv > 0.5:
            score = 0.9
        elif cv > 0.35:
            score = 0.7
        elif cv > 0.2:
            score = 0.5
        else:
            score = 0.3

        return {"burstiness_score": score, "cv": float(cv)}

    def calculate_personality(self, text: str) -> Dict[str, float]:
        """
        Check for personality markers.
        """
        word_count = len(text.split())

        markers = (
            text.count('!') +
            text.count('...') * 2 +
            text.count('(') +
            text.count('?') * 0.5
        )

        density = markers / max(word_count, 1) * 100

        if density > 2.5:
            score = 0.9
        elif density > 1:
            score = 0.7
        elif density > 0.3:
            score = 0.55
        else:
            score = 0.4

        return {"personality_score": score, "density": density}

    def score(self, text: str) -> Dict[str, float]:
        """
        Calculate complete AI detection score.
        """
        phrase = self.calculate_phrase_score(text)
        burstiness = self.calculate_burstiness(text)
        personality = self.calculate_personality(text)

        combined = (
            0.40 * phrase["phrase_score"] +
            0.35 * burstiness["burstiness_score"] +
            0.25 * personality["personality_score"]
        )

        return {
            "phrase_score": phrase["phrase_score"],
            "burstiness_score": burstiness["burstiness_score"],
            "personality_score": personality["personality_score"],
            "human_likelihood": min(max(combined, 0), 1),
            "interpretation": self._interpret(combined)
        }

    def _interpret(self, score: float) -> str:
        if score >= 0.75:
            return "likely_human"
        elif score >= 0.55:
            return "uncertain"
        else:
            return "possibly_ai"
