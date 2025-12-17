import numpy as np


class CoherenceScorer:
    """
    Measures logical coherence and structure of the response.
    """

    async def score(self, proof_text: str) -> float:
        scores = []

        # 1. Length check (not too short, not too long)
        length_score = self._score_length(proof_text)
        scores.append(length_score)

        # 2. Sentence structure
        structure_score = self._score_structure(proof_text)
        scores.append(structure_score)

        # 3. Logical flow (presence of connectors)
        flow_score = self._score_flow(proof_text)
        scores.append(flow_score)

        # 4. Completeness (not cut off)
        completeness_score = self._score_completeness(proof_text)
        scores.append(completeness_score)

        return sum(scores) / len(scores)

    def _score_length(self, text: str) -> float:
        words = len(text.split())
        # Ideal: 50-500 words
        if words < 20:
            return 0.2
        elif words < 50:
            return 0.5
        elif words <= 500:
            return 1.0
        elif words <= 1000:
            return 0.8
        else:
            return 0.6

    def _score_structure(self, text: str) -> float:
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.3

        # Check sentence length variance (good writing has variety)
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) > 1:
            variance = np.std(lengths) / (np.mean(lengths) + 1)
            variety_score = min(variance / 0.5, 1)
        else:
            variety_score = 0.5

        return 0.5 + 0.5 * variety_score

    def _score_flow(self, text: str) -> float:
        connectors = [
            'because', 'therefore', 'however', 'although', 'while',
            'since', 'but', 'and', 'so', 'thus', 'hence',
            'for example', 'specifically', 'in particular',
            'first', 'second', 'finally', 'also', 'additionally'
        ]

        text_lower = text.lower()
        connector_count = sum(1 for c in connectors if c in text_lower)

        # Ideal: 2-6 connectors per response
        if connector_count == 0:
            return 0.4
        elif connector_count <= 2:
            return 0.7
        elif connector_count <= 6:
            return 1.0
        else:
            return 0.8

    def _score_completeness(self, text: str) -> float:
        # Check if response ends properly
        text = text.strip()
        if not text:
            return 0

        # Ends with punctuation?
        if text[-1] in '.!?':
            return 1.0
        elif text[-1] in ',;:':
            return 0.5  # Cut off mid-sentence
        else:
            return 0.7
