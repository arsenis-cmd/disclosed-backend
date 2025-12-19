"""
Coherence Scorer

Measures text quality and structure:
1. Sentence structure variety
2. Logical flow (connectors)
3. Completeness (not truncated)
4. Semantic coherence between sentences
5. Appropriate length
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import re
import logging

logger = logging.getLogger(__name__)


LOGICAL_CONNECTORS = [
    'because', 'since', 'therefore', 'thus', 'hence',
    'but', 'however', 'although', 'though', 'yet',
    'and', 'also', 'additionally', 'furthermore',
    'first', 'second', 'finally', 'then', 'next',
    'for example', 'specifically', 'such as'
]


class CoherenceScorer:
    """
    Scores text coherence and structure.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 5]

    def calculate_structure_score(self, response: str) -> Dict[str, float]:
        """
        Analyze sentence structure variety.
        """
        sentences = self._split_sentences(response)

        if len(sentences) < 2:
            return {"structure_score": 0.5, "sentence_count": len(sentences)}

        lengths = [len(s.split()) for s in sentences]
        mean_len = np.mean(lengths)
        std_len = np.std(lengths)

        # Variance ratio (humans vary more)
        cv = std_len / (mean_len + 1) if mean_len > 0 else 0

        # Length score
        if mean_len < 5:
            length_score = 0.4
        elif mean_len <= 20:
            length_score = 0.9
        else:
            length_score = 0.7

        # Variance score
        variance_score = min(cv / 0.4, 1.0)

        structure = 0.5 * length_score + 0.5 * variance_score

        return {
            "structure_score": structure,
            "sentence_count": len(sentences),
            "mean_length": mean_len,
            "variance": cv
        }

    def calculate_flow_score(self, response: str) -> Dict[str, float]:
        """
        Check for logical connectors.
        """
        response_lower = response.lower()
        word_count = len(response.split())

        connector_count = sum(
            1 for c in LOGICAL_CONNECTORS
            if c in response_lower
        )

        expected = word_count / 40  # ~1 per 40 words
        ratio = connector_count / max(expected, 1)

        if ratio < 0.3:
            flow_score = 0.4
        elif ratio < 0.7:
            flow_score = 0.65
        elif ratio <= 1.5:
            flow_score = 0.9
        else:
            flow_score = 0.7  # Overused

        return {
            "flow_score": flow_score,
            "connector_count": connector_count
        }

    def calculate_completeness(self, response: str) -> Dict[str, float]:
        """
        Check if response is complete.
        """
        response = response.strip()

        if not response:
            return {"completeness_score": 0.0}

        last_char = response[-1]

        if last_char in '.!?':
            punct_score = 1.0
        elif last_char in ',;:':
            punct_score = 0.4
        else:
            punct_score = 0.6

        # Check for incomplete endings
        incomplete = ['and', 'but', 'the', 'a', 'to', 'that', 'which']
        last_word = response.split()[-1].lower().rstrip('.,!?') if response.split() else ''

        if last_word in incomplete:
            punct_score *= 0.5

        return {"completeness_score": punct_score}

    def calculate_semantic_coherence(self, response: str) -> Dict[str, float]:
        """
        Check if sentences relate to each other.
        """
        sentences = self._split_sentences(response)

        if len(sentences) < 2:
            return {"semantic_coherence": 0.7}

        embeddings = self.model.encode(sentences)

        # Adjacent sentence similarities
        adjacent_sims = []
        for i in range(len(embeddings) - 1):
            sim = np.dot(embeddings[i], embeddings[i+1])
            sim /= (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1]) + 1e-8)
            adjacent_sims.append(sim)

        mean_adjacent = np.mean(adjacent_sims)

        return {
            "semantic_coherence": float(mean_adjacent),
            "adjacent_similarities": adjacent_sims
        }

    def calculate_length_score(
        self,
        response: str,
        min_words: int = 30,
        max_words: int = 400
    ) -> Dict[str, float]:
        """
        Score based on response length.
        """
        word_count = len(response.split())

        if word_count < 15:
            score = 0.2
        elif word_count < min_words:
            score = 0.5
        elif word_count <= max_words:
            score = 1.0
        elif word_count <= max_words * 1.5:
            score = 0.8
        else:
            score = 0.5

        return {
            "length_score": score,
            "word_count": word_count
        }

    def score(self, response: str) -> Dict[str, float]:
        """
        Calculate complete coherence score.
        """
        structure = self.calculate_structure_score(response)
        flow = self.calculate_flow_score(response)
        completeness = self.calculate_completeness(response)
        semantic = self.calculate_semantic_coherence(response)
        length = self.calculate_length_score(response)

        combined = (
            0.20 * structure["structure_score"] +
            0.20 * flow["flow_score"] +
            0.20 * completeness["completeness_score"] +
            0.25 * semantic["semantic_coherence"] +
            0.15 * length["length_score"]
        )

        return {
            "structure": structure["structure_score"],
            "flow": flow["flow_score"],
            "completeness": completeness["completeness_score"],
            "semantic_coherence": semantic["semantic_coherence"],
            "length": length["length_score"],
            "combined": min(max(combined, 0), 1)
        }
