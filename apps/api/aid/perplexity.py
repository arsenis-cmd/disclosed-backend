"""
Perplexity-based Irreducibility Scorer

Core concept:
- Language models predict text probability
- Perplexity = how "surprised" the model is
- Low perplexity = predictable = compressible = reducible
- High perplexity = surprising = incompressible = irreducible

Key measurements:
1. Unconditional perplexity: How predictable is the response alone?
2. Conditional perplexity: How predictable given the content?
3. Irreducibility = degree to which content doesn't explain response
"""

import torch
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class PerplexityScorer:
    """
    Calculates perplexity-based irreducibility scores.

    This is the most computationally expensive component,
    as it requires running the language model.
    """

    def __init__(
        self,
        model_name: str = "gpt2-medium",
        use_gpu: bool = True,
        max_length: int = 1024
    ):
        self.model_name = model_name
        self.max_length = max_length
        self.device = self._get_device(use_gpu)

        # Load model and tokenizer
        logger.info(f"Loading perplexity model: {model_name}")
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Set padding token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        logger.info(f"Model loaded on {self.device}")

    def _get_device(self, use_gpu: bool) -> str:
        """Determine best available device."""
        if use_gpu:
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        return "cpu"

    def calculate_perplexity(self, text: str) -> Tuple[float, int]:
        """
        Calculate perplexity of text.

        Returns:
            (perplexity, token_count)
        """
        if not text or not text.strip():
            return float('inf'), 0

        # Tokenize
        encodings = self.tokenizer(
            text,
            return_tensors='pt',
            truncation=True,
            max_length=self.max_length,
            padding=False
        )

        input_ids = encodings.input_ids.to(self.device)
        token_count = input_ids.size(1)

        if token_count == 0:
            return float('inf'), 0

        # Calculate loss
        with torch.no_grad():
            outputs = self.model(input_ids, labels=input_ids)
            loss = outputs.loss.item()

        perplexity = float(np.exp(loss))

        return perplexity, token_count

    def calculate_conditional_perplexity(
        self,
        response: str,
        context: str,
        separator: str = "\n\n"
    ) -> Tuple[float, float, int]:
        """
        Calculate conditional perplexity of response given context.

        Returns:
            (unconditional_perplexity, conditional_perplexity, token_count)
        """
        # Unconditional
        unconditional, tokens = self.calculate_perplexity(response)

        # Conditional (response given context)
        combined = f"{context}{separator}{response}"

        # Tokenize separately to find boundary
        context_tokens = self.tokenizer(
            f"{context}{separator}",
            return_tensors='pt',
            truncation=True,
            max_length=self.max_length // 2
        ).input_ids
        context_len = context_tokens.size(1)

        combined_encodings = self.tokenizer(
            combined,
            return_tensors='pt',
            truncation=True,
            max_length=self.max_length
        )

        input_ids = combined_encodings.input_ids.to(self.device)

        # Create labels with context masked out
        labels = input_ids.clone()
        labels[:, :context_len] = -100  # Ignore context in loss

        with torch.no_grad():
            outputs = self.model(input_ids, labels=labels)
            loss = outputs.loss.item()

        conditional = float(np.exp(loss))

        return unconditional, conditional, tokens

    def calculate_irreducibility(
        self,
        response: str,
        content: str
    ) -> Dict[str, float]:
        """
        Calculate irreducibility score.

        Measures how much the content "explains" the response.
        If content explains it well → low irreducibility (bad)
        If content doesn't explain it → high irreducibility (good)
        """
        unconditional, conditional, tokens = self.calculate_conditional_perplexity(
            response, content
        )

        # Handle edge cases
        if unconditional == float('inf') or unconditional == 0:
            return {
                "unconditional": unconditional,
                "conditional": conditional,
                "reduction_ratio": 1.0,
                "irreducibility_score": 0.5,
                "tokens": tokens
            }

        # Reduction ratio: how much context helps predict response
        reduction_ratio = conditional / unconditional

        # Convert to 0-1 score
        # ratio < 1: context helps → reducible → low score
        # ratio = 1: context doesn't help → irreducible → medium score
        # ratio > 1: context makes it harder (contradiction?) → high score

        # Clamp and map
        ratio_clamped = max(0.3, min(1.5, reduction_ratio))

        # Map [0.3, 1.5] to [0, 1]
        # 0.3 → 0.0 (very reducible)
        # 1.0 → 0.58 (neutral)
        # 1.5 → 1.0 (very irreducible)
        irreducibility = (ratio_clamped - 0.3) / 1.2

        return {
            "unconditional": unconditional,
            "conditional": conditional,
            "reduction_ratio": reduction_ratio,
            "irreducibility_score": irreducibility,
            "tokens": tokens
        }

    def estimate_ai_likelihood(self, response: str) -> Dict[str, float]:
        """
        Estimate if response is AI-generated based on perplexity.

        AI text tends to have low, consistent perplexity.
        Human text has higher, more variable perplexity.
        """
        perplexity, tokens = self.calculate_perplexity(response)

        # Thresholds (calibrate with real data)
        AI_LIKELY = 20.0
        AI_POSSIBLE = 30.0
        HUMAN_LIKELY = 45.0
        HUMAN_VERY_LIKELY = 65.0

        if perplexity < AI_LIKELY:
            score = 0.15  # Very likely AI
        elif perplexity < AI_POSSIBLE:
            score = 0.35
        elif perplexity < HUMAN_LIKELY:
            score = 0.55  # Could be either
        elif perplexity < HUMAN_VERY_LIKELY:
            score = 0.75
        else:
            score = 0.90  # Very likely human

        return {
            "perplexity": perplexity,
            "human_likelihood": score,
            "tokens": tokens
        }

    def score(
        self,
        response: str,
        content: str
    ) -> Dict[str, any]:
        """
        Complete perplexity-based scoring.
        """
        # Irreducibility
        irr = self.calculate_irreducibility(response, content)

        # AI likelihood
        ai = self.estimate_ai_likelihood(response)

        return {
            "unconditional_perplexity": irr["unconditional"],
            "conditional_perplexity": irr["conditional"],
            "reduction_ratio": irr["reduction_ratio"],
            "irreducibility_score": irr["irreducibility_score"],
            "ai_likelihood_score": ai["human_likelihood"],
            "perplexity_for_ai": ai["perplexity"],
            "tokens_analyzed": irr["tokens"],
            "model": self.model_name
        }
