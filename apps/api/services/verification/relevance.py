from sentence_transformers import SentenceTransformer
import numpy as np


class RelevanceScorer:
    """
    Measures semantic relevance between proof and content.
    Uses embedding similarity + keyword overlap + concept coverage.
    """

    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def score(
        self,
        proof_text: str,
        content_text: str,
        proof_prompt: str
    ) -> float:
        # 1. Embedding similarity
        embeddings = self.model.encode([proof_text, content_text, proof_prompt])

        proof_emb = embeddings[0]
        content_emb = embeddings[1]
        prompt_emb = embeddings[2]

        # Similarity to content
        content_sim = self._cosine_similarity(proof_emb, content_emb)

        # Similarity to prompt (should address the question)
        prompt_sim = self._cosine_similarity(proof_emb, prompt_emb)

        # 2. Key concept coverage
        content_keywords = self._extract_keywords(content_text)
        proof_keywords = self._extract_keywords(proof_text)
        keyword_overlap = len(content_keywords & proof_keywords) / max(len(content_keywords), 1)

        # 3. Combine signals
        # Weight: 40% content similarity, 30% prompt addressing, 30% keyword coverage
        score = (
            0.4 * content_sim +
            0.3 * prompt_sim +
            0.3 * keyword_overlap
        )

        return min(max(score, 0), 1)  # Clamp to 0-1

    def _cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _extract_keywords(self, text: str) -> set:
        # Simple keyword extraction - can be improved
        import re
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        # Filter common words
        stopwords = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they', 'their', 'what', 'when', 'where', 'which', 'would', 'could', 'should', 'about', 'there', 'these', 'those', 'being', 'because', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'same', 'than', 'very', 'just', 'also'}
        return set(w for w in words if w not in stopwords)
