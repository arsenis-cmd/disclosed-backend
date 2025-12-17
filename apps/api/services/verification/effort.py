class EffortEstimator:
    """
    Estimates cognitive effort based on:
    1. Time spent
    2. Response complexity relative to content
    3. Revision patterns
    4. Typing patterns (if available)
    """

    async def score(
        self,
        proof_text: str,
        content_text: str,
        metadata: dict
    ) -> float:
        scores = []

        # 1. Time-based scoring
        time_spent = metadata.get('time_spent_seconds', 0)
        time_score = self._score_time(time_spent, len(proof_text))
        scores.append(time_score)

        # 2. Complexity relative to content
        complexity_score = self._score_complexity(proof_text, content_text)
        scores.append(complexity_score)

        # 3. Revision count (some revision = thoughtful)
        revisions = metadata.get('revision_count', 0)
        revision_score = self._score_revisions(revisions)
        scores.append(revision_score)

        return sum(scores) / len(scores)

    def _score_time(self, seconds: int, response_length: int) -> float:
        """
        Too fast = suspicious (copy-paste or AI)
        Too slow = might be distracted, but not necessarily bad
        """
        if seconds == 0:
            return 0.3

        # Expected: ~1 word per 2 seconds for thoughtful writing
        words = response_length / 5  # Rough word estimate
        expected_seconds = words * 2

        ratio = seconds / max(expected_seconds, 1)

        if ratio < 0.3:  # Way too fast
            return 0.2
        elif ratio < 0.5:  # Quite fast
            return 0.5
        elif ratio < 2:  # Normal range
            return 1.0
        elif ratio < 5:  # Slow but okay
            return 0.8
        else:  # Very slow (probably distracted)
            return 0.6

    def _score_complexity(self, proof: str, content: str) -> float:
        """Response should show synthesis, not just regurgitation"""
        proof_words = set(proof.lower().split())
        content_words = set(content.lower().split())

        # Words in proof that aren't in content = new contribution
        new_words = proof_words - content_words
        new_ratio = len(new_words) / max(len(proof_words), 1)

        # Should have substantial new content (at least 50%)
        return min(new_ratio / 0.5, 1)

    def _score_revisions(self, count: int) -> float:
        """Some revision suggests thoughtfulness"""
        if count == 0:
            return 0.7  # Wrote it in one go - might be fine
        elif count <= 3:
            return 1.0  # Normal editing
        elif count <= 10:
            return 0.8  # Lots of editing - still okay
        else:
            return 0.6  # Excessive - might be gaming
