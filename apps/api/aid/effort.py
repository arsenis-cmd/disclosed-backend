"""
Effort Estimator

Estimates cognitive effort based on:
1. Time spent
2. Response complexity
3. Revision patterns
4. Typing patterns (if available)
"""

import numpy as np
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class EffortEstimator:
    """
    Estimates effort put into a response.
    """

    def calculate_time_score(
        self,
        time_seconds: int,
        response_length: int,
        content_length: int
    ) -> Dict[str, float]:
        """
        Score based on time spent.
        """
        if time_seconds <= 0:
            return {"time_score": 0.5, "flag": "no_time"}

        # Expected time (seconds)
        response_words = response_length / 5
        content_words = content_length / 5

        read_time = (content_words / 200) * 60  # 200 wpm reading
        write_time = (response_words / 35) * 60  # 35 wpm thoughtful writing
        expected = read_time + write_time

        ratio = time_seconds / max(expected, 1)

        if ratio < 0.25:
            score, flag = 0.2, "very_fast"
        elif ratio < 0.5:
            score, flag = 0.45, "fast"
        elif ratio < 1.5:
            score, flag = 0.9, "normal"
        elif ratio < 3:
            score, flag = 0.75, "slow"
        else:
            score, flag = 0.5, "very_slow"

        return {
            "time_score": score,
            "ratio": ratio,
            "expected_seconds": expected,
            "flag": flag
        }

    def calculate_complexity_score(
        self,
        response: str,
        content: str
    ) -> Dict[str, float]:
        """
        Measure response complexity.
        """
        response_words = response.lower().split()
        content_words = set(content.lower().split())

        # New vocabulary
        response_vocab = set(response_words)
        new_vocab = response_vocab - content_words
        new_ratio = len(new_vocab) / max(len(response_vocab), 1)

        # Long words (more specific)
        long_words = [w for w in response_words if len(w) > 8]
        long_ratio = len(long_words) / max(len(response_words), 1)

        # Subclauses
        subclause_count = len(re.findall(r'[,;]', response))
        sentence_count = len(re.split(r'[.!?]+', response))
        avg_subclauses = subclause_count / max(sentence_count, 1)

        vocab_score = min(new_ratio * 2, 1.0)
        long_score = min(long_ratio * 10, 1.0)
        clause_score = min(avg_subclauses / 2, 1.0)

        complexity = 0.4 * vocab_score + 0.3 * long_score + 0.3 * clause_score

        return {
            "complexity_score": complexity,
            "new_vocab_ratio": new_ratio,
            "long_word_ratio": long_ratio
        }

    def calculate_revision_score(
        self,
        revision_count: int,
        response_length: int
    ) -> Dict[str, float]:
        """
        Score based on revisions.
        """
        if revision_count < 0:
            return {"revision_score": 0.7, "flag": "no_data"}

        expected = response_length / 400

        if revision_count == 0:
            score, flag = 0.6, "none"
        elif revision_count <= expected * 2:
            score, flag = 0.9, "normal"
        elif revision_count <= expected * 5:
            score, flag = 0.7, "many"
        else:
            score, flag = 0.5, "excessive"

        return {"revision_score": score, "flag": flag}

    def score(
        self,
        response: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate complete effort score.
        """
        time_result = self.calculate_time_score(
            metadata.get("time_spent_seconds", 0),
            len(response),
            len(content)
        )

        complexity = self.calculate_complexity_score(response, content)

        revision = self.calculate_revision_score(
            metadata.get("revision_count", -1),
            len(response)
        )

        # Combine based on available data
        has_time = metadata.get("time_spent_seconds", 0) > 0
        has_revisions = metadata.get("revision_count", -1) >= 0

        if has_time and has_revisions:
            combined = (
                0.40 * time_result["time_score"] +
                0.35 * complexity["complexity_score"] +
                0.25 * revision["revision_score"]
            )
        elif has_time:
            combined = 0.55 * time_result["time_score"] + 0.45 * complexity["complexity_score"]
        else:
            combined = complexity["complexity_score"]

        return {
            "time": time_result["time_score"],
            "complexity": complexity["complexity_score"],
            "revision": revision["revision_score"],
            "combined": min(max(combined, 0), 1),
            "flags": [time_result.get("flag", ""), revision.get("flag", "")]
        }
