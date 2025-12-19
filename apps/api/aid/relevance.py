"""
Relevance Scorer

Measures how well the response engages with the content and prompt.
Uses semantic similarity (embeddings) + keyword analysis.

High relevance = response actually addresses the topic
Low relevance = off-topic or generic
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Set, Dict
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)


# Stopwords to exclude from keyword analysis
STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
    'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
    'what', 'which', 'who', 'whom', 'where', 'when', 'why', 'how', 'all',
    'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
    'no', 'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just', 'also'
}


class RelevanceScorer:
    """
    Scores relevance of response to content and prompt.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def _extract_keywords(self, text: str, min_len: int = 4) -> Set[str]:
        """Extract meaningful keywords."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return {w for w in words if len(w) >= min_len and w not in STOPWORDS}

    def calculate_semantic_similarity(
        self,
        response: str,
        content: str,
        prompt: str
    ) -> Dict[str, float]:
        """
        Calculate embedding-based semantic similarity.
        """
        # Encode all texts
        embeddings = self.model.encode([response, content, prompt])
        resp_emb, cont_emb, prompt_emb = embeddings

        content_sim = self._cosine_similarity(resp_emb, cont_emb)
        prompt_sim = self._cosine_similarity(resp_emb, prompt_emb)

        return {
            "content_similarity": content_sim,
            "prompt_similarity": prompt_sim
        }

    def calculate_keyword_overlap(
        self,
        response: str,
        content: str
    ) -> Dict[str, float]:
        """
        Calculate keyword coverage.
        """
        response_kw = self._extract_keywords(response)
        content_kw = self._extract_keywords(content)

        if not content_kw:
            return {"keyword_overlap": 0.5, "keywords_matched": 0}

        overlap = response_kw & content_kw
        coverage = len(overlap) / len(content_kw)

        return {
            "keyword_overlap": min(coverage, 1.0),
            "keywords_matched": len(overlap),
            "content_keywords": len(content_kw)
        }

    def calculate_topic_coherence(
        self,
        response: str,
        content: str
    ) -> float:
        """
        Check if all parts of response stay on topic.
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

        if len(sentences) < 2:
            return 0.7  # Not enough to analyze

        # Embed content and all sentences
        texts = [content] + sentences
        embeddings = self.model.encode(texts)
        content_emb = embeddings[0]
        sentence_embs = embeddings[1:]

        # Check each sentence's relevance to content
        similarities = [
            self._cosine_similarity(s_emb, content_emb)
            for s_emb in sentence_embs
        ]

        # Score based on consistency
        mean_sim = np.mean(similarities)
        min_sim = min(similarities)

        # Penalize if any sentence is way off topic
        coherence = 0.6 * mean_sim + 0.4 * min_sim

        return float(coherence)

    def score(
        self,
        response: str,
        content: str,
        prompt: str
    ) -> Dict[str, float]:
        """
        Calculate complete relevance score.
        """
        # Semantic similarity
        semantic = self.calculate_semantic_similarity(response, content, prompt)

        # Keyword overlap
        keywords = self.calculate_keyword_overlap(response, content)

        # Topic coherence
        coherence = self.calculate_topic_coherence(response, content)

        # Combined score
        combined = (
            0.35 * semantic["content_similarity"] +
            0.30 * semantic["prompt_similarity"] +
            0.20 * keywords["keyword_overlap"] +
            0.15 * coherence
        )

        return {
            "content_similarity": semantic["content_similarity"],
            "prompt_similarity": semantic["prompt_similarity"],
            "keyword_overlap": keywords["keyword_overlap"],
            "topic_coherence": coherence,
            "combined": min(max(combined, 0), 1)
        }
