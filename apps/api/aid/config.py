"""
Configuration management for AID engine.
Supports environment variables and config files.
"""

import os
from typing import Optional, List
from .types import AIDConfig


def load_config(
    config_path: Optional[str] = None,
    env_prefix: str = "AID_"
) -> AIDConfig:
    """
    Load configuration with priority:
    1. Environment variables (highest)
    2. Config file
    3. Defaults (lowest)
    """
    config = AIDConfig()

    # Override from environment
    env_mappings = {
        "PERPLEXITY_MODEL": "perplexity_model",
        "EMBEDDING_MODEL": "embedding_model",
        "USE_GPU": "use_gpu",
        "MIN_RELEVANCE": "min_relevance",
        "MIN_IRREDUCIBILITY": "min_irreducibility",
        "MIN_NOVELTY": "min_novelty",
        "MIN_COHERENCE": "min_coherence",
        "MIN_COMBINED": "min_combined",
        "CACHE_BACKEND": "cache_backend",
        "REDIS_URL": "redis_url",
        "LOG_LEVEL": "log_level"
    }

    for env_suffix, attr in env_mappings.items():
        env_var = f"{env_prefix}{env_suffix}"
        value = os.environ.get(env_var)
        if value is not None:
            # Type conversion
            current_type = type(getattr(config, attr))
            if current_type == bool:
                value = value.lower() in ('true', '1', 'yes')
            elif current_type == float:
                value = float(value)
            elif current_type == int:
                value = int(value)
            setattr(config, attr, value)

    return config


def validate_config(config: AIDConfig) -> List[str]:
    """Validate configuration, return list of warnings/errors."""
    issues = []

    # Check weights sum
    weights_sum = (
        config.weight_relevance +
        config.weight_irreducibility_content +
        config.weight_irreducibility_ai +
        config.weight_novelty +
        config.weight_coherence +
        config.weight_effort
    )
    if not (0.95 <= weights_sum <= 1.05):
        issues.append(f"Weights sum to {weights_sum}, should be ~1.0")

    # Check thresholds are valid
    for attr in ['min_relevance', 'min_irreducibility', 'min_novelty',
                 'min_coherence', 'min_combined']:
        value = getattr(config, attr)
        if not (0 <= value <= 1):
            issues.append(f"{attr}={value} should be between 0 and 1")

    # Check model names
    valid_perplexity_models = ['gpt2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl']
    if config.perplexity_model not in valid_perplexity_models:
        issues.append(f"Unknown perplexity model: {config.perplexity_model}")

    return issues
