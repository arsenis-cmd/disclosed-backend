from sentence_transformers import SentenceTransformer
import numpy as np


class NoveltyScorer:
    """
    Measures novelty of proof:
    1. Not copied from content
    2. Not too similar to other proofs
    3. Contains unique personal elements
    """

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def score(
        self,
        proof_text: str,
        content_text: str,
        existing_proofs: list[str]
    ) -> float:

        # 1. Check it's not just paraphrasing the content
        content_distance = self._compute_distance(proof_text, content_text)

        # 2. Check it's not too similar to other proofs
        if existing_proofs:
            proof_similarities = [
                self._compute_similarity(proof_text, other)
                for other in existing_proofs
            ]
            max_proof_similarity = max(proof_similarities)
        else:
            max_proof_similarity = 0

        # 3. Check for personal/specific elements
        personal_score = self._check_personalization(proof_text)

        # 4. Check for templated patterns
        template_score = 1 - self._check_template_patterns(proof_text)

        # Combine
        # Must not be too close to content (min 0.3 distance)
        # Must not be too close to other proofs (max 0.7 similarity)
        # Should have personal elements
        # Should not match templates

        content_novelty = min(content_distance / 0.5, 1)  # Normalize
        proof_novelty = 1 - max_proof_similarity

        score = (
            0.3 * content_novelty +
            0.3 * proof_novelty +
            0.2 * personal_score +
            0.2 * template_score
        )

        return min(max(score, 0), 1)

    def _compute_similarity(self, text1: str, text2: str) -> float:
        emb = self.model.encode([text1, text2])
        return np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))

    def _compute_distance(self, text1: str, text2: str) -> float:
        return 1 - self._compute_similarity(text1, text2)

    def _check_personalization(self, text: str) -> float:
        """Check for personal pronouns and specific details"""
        personal_indicators = ['i ', 'my ', 'me ', "i'm", "i've", 'personally', 'in my experience', 'for me']
        specific_indicators = ['specifically', 'for example', 'in particular', 'such as']

        text_lower = text.lower()

        personal_count = sum(1 for p in personal_indicators if p in text_lower)
        specific_count = sum(1 for s in specific_indicators if s in text_lower)

        # Normalize to 0-1
        score = min((personal_count + specific_count) / 5, 1)
        return score

    def _check_template_patterns(self, text: str) -> float:
        """Detect templated/formulaic responses"""
        templates = [
            "this is a great",
            "i think this is",
            "in conclusion",
            "to summarize",
            "overall i believe",
            "this product is",
            "i would recommend",
        ]

        text_lower = text.lower()
        matches = sum(1 for t in templates if t in text_lower)

        return min(matches / 3, 1)  # More than 3 matches = very templated
