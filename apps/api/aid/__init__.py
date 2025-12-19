"""
AID - Algorithmic Irreducibility Detection

A verification engine for Proof of Consideration that measures
how expensive it would be to fake genuine human engagement.
"""

from .types import (
    AIDConfig,
    AIDResult,
    VerificationStatus,
    VerificationRequest,
    PerplexityScores,
    RelevanceScores,
    NoveltyScores,
    CoherenceScores,
    EffortScores,
    AIDetectionScores
)
from .config import load_config, validate_config
from .engine import AIDEngine

__version__ = "1.0.0"
__all__ = [
    "AIDEngine",
    "AIDConfig",
    "AIDResult",
    "VerificationStatus",
    "load_config",
    "validate_config"
]


def create_engine(config: AIDConfig = None) -> AIDEngine:
    """Create and return an AID engine instance."""
    return AIDEngine(config)
