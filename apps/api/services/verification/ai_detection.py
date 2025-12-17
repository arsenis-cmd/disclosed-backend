import re
import numpy as np


class AIDetector:
    """
    Detects AI-generated content using multiple signals.
    This is a heuristic approach - not perfect, but adds cost to faking.
    """

    def __init__(self):
        # Could load a trained classifier here
        pass

    async def score(self, text: str) -> float:
        """
        Returns 1 if likely human, 0 if likely AI.
        """
        signals = []

        # 1. Check for AI-typical patterns
        ai_pattern_score = 1 - self._check_ai_patterns(text)
        signals.append(ai_pattern_score)

        # 2. Check for overly perfect grammar/structure
        perfection_score = 1 - self._check_perfection(text)
        signals.append(perfection_score)

        # 3. Check for personality/quirks
        personality_score = self._check_personality(text)
        signals.append(personality_score)

        # 4. Burstiness (humans write in bursts, AI is more uniform)
        # This would need typing data, so we approximate with sentence variance
        burstiness_score = self._check_burstiness(text)
        signals.append(burstiness_score)

        return sum(signals) / len(signals)

    def _check_ai_patterns(self, text: str) -> float:
        """AI often uses certain phrases"""
        ai_phrases = [
            "as an ai",
            "i cannot",
            "i don't have personal",
            "it's important to note",
            "it's worth noting",
            "in this context",
            "that being said",
            "it's crucial",
            "delve into",
            "facilitate",
            "leverage",
            "utilize",
            "in terms of",
            "at the end of the day",
            "moving forward",
        ]

        text_lower = text.lower()
        matches = sum(1 for phrase in ai_phrases if phrase in text_lower)

        return min(matches / 3, 1)

    def _check_perfection(self, text: str) -> float:
        """Humans make small mistakes, AI doesn't"""
        # Check for minor imperfections that suggest human writing

        # Contractions (humans use them more naturally)
        contractions = ["don't", "can't", "won't", "isn't", "aren't", "I'm", "I've", "it's", "that's", "there's"]
        contraction_count = sum(1 for c in contractions if c.lower() in text.lower())

        # Informal markers
        informal = ["yeah", "kinda", "gonna", "wanna", "tbh", "imo", "honestly", "actually", "basically", "literally"]
        informal_count = sum(1 for i in informal if i.lower() in text.lower())

        # If too "perfect" (no contractions, no informal language) = suspicious
        human_markers = contraction_count + informal_count

        if human_markers >= 3:
            return 0  # Very human-like
        elif human_markers >= 1:
            return 0.3
        else:
            return 0.7  # Suspiciously perfect

    def _check_personality(self, text: str) -> float:
        """Real humans show personality quirks"""
        # Exclamations, emphatics, hedging
        personality_markers = [
            '!',  # Excitement
            '...',  # Trailing off
            '-',  # Self-correction
            'maybe', 'perhaps', 'probably',  # Hedging
            'really', 'very', 'so',  # Emphatics
            'haha', 'lol', 'wow',  # Reactions
        ]

        text_lower = text.lower()
        count = sum(1 for m in personality_markers if m in text_lower)

        return min(count / 4, 1)

    def _check_burstiness(self, text: str) -> float:
        """Human writing has more variance in sentence structure"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            return 0.5  # Not enough data

        lengths = [len(s.split()) for s in sentences]

        # Calculate coefficient of variation
        mean_len = np.mean(lengths)
        std_len = np.std(lengths)

        if mean_len == 0:
            return 0.5

        cv = std_len / mean_len

        # AI tends to have CV around 0.3-0.5
        # Humans often have CV > 0.5
        if cv > 0.6:
            return 1.0  # High variance = likely human
        elif cv > 0.4:
            return 0.7
        else:
            return 0.4  # Low variance = possibly AI
