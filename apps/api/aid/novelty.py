"""
Novelty Scorer

Measures how novel/unique a response is:
1. Not copying the original content
2. Not copying other responses
3. Contains personal/specific elements
4. Not using generic templates
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Set
import re
import logging

logger = logging.getLogger(__name__)


# Template phrases that indicate low-effort response
TEMPLATE_PHRASES = [
    "this is a great", "i think this is", "in conclusion",
    "to summarize", "i would recommend", "overall i believe",
    "in my opinion", "it's important to", "as mentioned",
    "first of all", "last but not least", "at the end of the day"
]

# Personal markers that suggest genuine response
PERSONAL_MARKERS = [
    "i ", "my ", "me ", "i'm", "i've", "i'll",
    "personally", "in my experience", "for me",
    "my situation", "my home", "my job", "my family"
]

# Specificity markers
SPECIFICITY_MARKERS = [
    "specifically", "for example", "for instance",
    "because", "since", "last week", "yesterday",
    "about $", "around ", "miles", "minutes", "hours"
]


class NoveltyScorer:
    """
    Scores novelty and uniqueness of responses.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def calculate_content_distance(
        self,
        response: str,
        content: str
    ) -> Dict[str, float]:
        """
        Measure distance from original content.
        Response should add new information, not just paraphrase.
        """
        # Embedding similarity
        embeddings = self.model.encode([response, content])
        similarity = self._cosine_similarity(embeddings[0], embeddings[1])

        # Direct text overlap (trigrams)
        def get_trigrams(text: str) -> Set[str]:
            words = text.lower().split()
            return {' '.join(words[i:i+3]) for i in range(len(words)-2)}

        resp_tri = get_trigrams(response)
        cont_tri = get_trigrams(content)

        if not resp_tri:
            trigram_overlap = 0
        else:
            trigram_overlap = len(resp_tri & cont_tri) / len(resp_tri)

        # Score: want moderate similarity (relevant but not copying)
        if similarity > 0.85:
            distance_score = 0.2  # Too similar
        elif similarity > 0.7:
            distance_score = 0.5
        elif similarity > 0.4:
            distance_score = 0.85  # Good range
        else:
            distance_score = 0.6  # Maybe off-topic

        # Penalize direct copying
        distance_score *= (1 - trigram_overlap * 0.5)

        return {
            "similarity": similarity,
            "trigram_overlap": trigram_overlap,
            "distance_score": max(0, distance_score)
        }

    def calculate_corpus_novelty(
        self,
        response: str,
        existing_responses: List[str],
        max_compare: int = 100
    ) -> Dict[str, float]:
        """
        Measure uniqueness compared to other responses.
        """
        if not existing_responses:
            return {
                "max_similarity": 0.0,
                "mean_similarity": 0.0,
                "novelty_score": 0.9
            }

        # Limit for performance
        if len(existing_responses) > max_compare:
            existing_responses = existing_responses[:max_compare]

        # Encode all
        all_texts = [response] + existing_responses
        embeddings = self.model.encode(all_texts)

        response_emb = embeddings[0]
        existing_embs = embeddings[1:]

        # Calculate similarities
        similarities = [
            self._cosine_similarity(response_emb, e)
            for e in existing_embs
        ]

        max_sim = max(similarities)
        mean_sim = np.mean(similarities)

        # Score: lower similarity = higher novelty
        if max_sim > 0.9:
            novelty_score = 0.15  # Probably duplicate
        elif max_sim > 0.8:
            novelty_score = 0.4
        elif max_sim > 0.65:
            novelty_score = 0.65
        else:
            novelty_score = 0.9  # Very unique

        return {
            "max_similarity": max_sim,
            "mean_similarity": mean_sim,
            "corpus_size": len(existing_responses),
            "novelty_score": novelty_score
        }

    def calculate_personalization(self, response: str) -> Dict[str, float]:
        """
        Check for personal and specific markers.
        """
        response_lower = response.lower()
        word_count = len(response.split())

        if word_count < 10:
            return {"combined": 0.3}

        personal_count = sum(1 for m in PERSONAL_MARKERS if m in response_lower)
        specific_count = sum(1 for m in SPECIFICITY_MARKERS if m in response_lower)

        # Normalize
        personal_score = min(personal_count / 3, 1.0)
        specific_score = min(specific_count / 2, 1.0)

        combined = 0.5 * personal_score + 0.5 * specific_score

        # Bonus for having both
        if personal_count >= 2 and specific_count >= 1:
            combined = min(combined + 0.2, 1.0)

        return {
            "personal_count": personal_count,
            "specific_count": specific_count,
            "combined": combined
        }

    def calculate_template_penalty(self, response: str) -> Dict[str, float]:
        """
        Detect template/generic phrases.
        """
        response_lower = response.lower()

        matches = [p for p in TEMPLATE_PHRASES if p in response_lower]
        count = len(matches)

        if count == 0:
            penalty = 0.0
            score = 1.0
        elif count == 1:
            penalty = 0.15
            score = 0.85
        elif count == 2:
            penalty = 0.3
            score = 0.7
        else:
            penalty = 0.5
            score = 0.5

        return {
            "template_count": count,
            "templates_found": matches,
            "penalty": penalty,
            "score": score
        }

    def score(
        self,
        response: str,
        content: str,
        existing_responses: List[str] = None
    ) -> Dict[str, float]:
        """
        Calculate complete novelty score.
        """
        existing_responses = existing_responses or []

        content_dist = self.calculate_content_distance(response, content)
        corpus_novelty = self.calculate_corpus_novelty(response, existing_responses)
        personalization = self.calculate_personalization(response)
        template = self.calculate_template_penalty(response)

        # Combined score
        combined = (
            0.30 * content_dist["distance_score"] +
            0.30 * corpus_novelty["novelty_score"] +
            0.25 * personalization["combined"] +
            0.15 * template["score"]
        )

        return {
            "content_distance": content_dist["distance_score"],
            "corpus_novelty": corpus_novelty["novelty_score"],
            "max_corpus_similarity": corpus_novelty["max_similarity"],
            "personalization": personalization["combined"],
            "template_score": template["score"],
            "combined": min(max(combined, 0), 1)
        }
