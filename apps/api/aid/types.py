"""
All type definitions for the AID engine.
Uses dataclasses for clean, typed data structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class VerificationStatus(Enum):
    """Status of a verification request."""
    PENDING = "pending"
    PROCESSING = "processing"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class AIDConfig:
    """
    Complete configuration for the AID engine.
    All parameters have sensible defaults.
    """
    # Model selection
    perplexity_model: str = "gpt2-medium"  # Options: gpt2, gpt2-medium, gpt2-large
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformer model
    use_gpu: bool = True  # Use CUDA/MPS if available

    # Verification thresholds (all 0-1 scale)
    min_relevance: float = 0.60
    min_irreducibility: float = 0.55
    min_novelty: float = 0.55
    min_coherence: float = 0.50
    min_combined: float = 0.55

    # Component weights (must sum to ~1.0)
    weight_relevance: float = 0.20
    weight_irreducibility_content: float = 0.20
    weight_irreducibility_ai: float = 0.15
    weight_novelty: float = 0.20
    weight_coherence: float = 0.15
    weight_effort: float = 0.10

    # Processing limits
    max_response_tokens: int = 1024
    max_content_tokens: int = 2048
    max_corpus_size: int = 100  # Max existing responses to compare

    # Perplexity calibration (tune based on testing)
    perplexity_ai_threshold: float = 25.0      # Below = likely AI
    perplexity_human_threshold: float = 50.0   # Above = likely human

    # Cache settings
    enable_cache: bool = True
    cache_backend: str = "memory"  # Options: memory, redis
    cache_ttl_seconds: int = 3600
    redis_url: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    log_raw_scores: bool = True


@dataclass
class PerplexityScores:
    """Results from perplexity analysis."""
    unconditional: float           # Perplexity of response alone
    conditional: float             # Perplexity given content
    reduction_ratio: float         # conditional / unconditional
    irreducibility_score: float    # 0-1 score
    ai_likelihood_score: float     # 0-1 (1 = human, 0 = AI)
    tokens_analyzed: int
    model_used: str


@dataclass
class RelevanceScores:
    """Results from relevance analysis."""
    content_similarity: float      # Embedding similarity to content
    prompt_similarity: float       # Embedding similarity to prompt
    keyword_overlap: float         # Keyword coverage
    concept_coverage: float        # Key concepts addressed
    topic_coherence: float         # Stays on topic throughout
    combined: float                # Final relevance score


@dataclass
class NoveltyScores:
    """Results from novelty analysis."""
    content_distance: float        # Not just paraphrasing content
    corpus_distance: float         # Different from other responses
    max_corpus_similarity: float   # Most similar existing response
    personalization: float         # Contains personal markers
    template_score: float          # Not using templates (1 = no templates)
    combined: float


@dataclass
class CoherenceScores:
    """Results from coherence analysis."""
    structure: float               # Sentence structure quality
    flow: float                    # Logical connectors
    completeness: float            # Not truncated
    semantic_coherence: float      # Sentences relate to each other
    length_score: float            # Appropriate length
    combined: float


@dataclass
class EffortScores:
    """Results from effort estimation."""
    time_score: float              # Based on time spent
    complexity_score: float        # Response complexity
    revision_score: float          # Revision patterns
    typing_score: float            # Typing patterns (if available)
    combined: float
    flags: List[str] = field(default_factory=list)  # Any warnings


@dataclass
class AIDetectionScores:
    """Results from AI detection."""
    phrase_score: float            # AI phrases vs human markers
    pattern_score: float           # AI-typical patterns
    burstiness_score: float        # Writing rhythm
    personality_score: float       # Human quirks
    perfection_penalty: float      # Too clean = suspicious
    combined: float                # Overall human likelihood
    confidence: float              # How confident is the detection


@dataclass
class AIDResult:
    """
    Complete verification result.
    This is what the API returns.
    """
    # Overall result
    status: VerificationStatus
    passed: bool
    combined_score: float

    # Individual component scores
    relevance: RelevanceScores
    perplexity: PerplexityScores
    novelty: NoveltyScores
    coherence: CoherenceScores
    effort: EffortScores
    ai_detection: AIDetectionScores

    # Thresholds used
    thresholds_applied: Dict[str, float]

    # Feedback
    feedback_summary: str
    feedback_details: List[str]
    improvement_suggestions: List[str]

    # Metadata
    processing_time_ms: int
    model_versions: Dict[str, str]
    cache_hit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "passed": self.passed,
            "combined_score": self.combined_score,
            "relevance": {
                "content_similarity": self.relevance.content_similarity,
                "prompt_similarity": self.relevance.prompt_similarity,
                "keyword_overlap": self.relevance.keyword_overlap,
                "concept_coverage": self.relevance.concept_coverage,
                "topic_coherence": self.relevance.topic_coherence,
                "combined": self.relevance.combined
            },
            "perplexity": {
                "unconditional": self.perplexity.unconditional,
                "conditional": self.perplexity.conditional,
                "reduction_ratio": self.perplexity.reduction_ratio,
                "irreducibility_score": self.perplexity.irreducibility_score,
                "ai_likelihood_score": self.perplexity.ai_likelihood_score,
                "tokens_analyzed": self.perplexity.tokens_analyzed,
                "model_used": self.perplexity.model_used
            },
            "novelty": {
                "content_distance": self.novelty.content_distance,
                "corpus_distance": self.novelty.corpus_distance,
                "max_corpus_similarity": self.novelty.max_corpus_similarity,
                "personalization": self.novelty.personalization,
                "template_score": self.novelty.template_score,
                "combined": self.novelty.combined
            },
            "coherence": {
                "structure": self.coherence.structure,
                "flow": self.coherence.flow,
                "completeness": self.coherence.completeness,
                "semantic_coherence": self.coherence.semantic_coherence,
                "length_score": self.coherence.length_score,
                "combined": self.coherence.combined
            },
            "effort": {
                "time_score": self.effort.time_score,
                "complexity_score": self.effort.complexity_score,
                "revision_score": self.effort.revision_score,
                "typing_score": self.effort.typing_score,
                "combined": self.effort.combined,
                "flags": self.effort.flags
            },
            "ai_detection": {
                "phrase_score": self.ai_detection.phrase_score,
                "pattern_score": self.ai_detection.pattern_score,
                "burstiness_score": self.ai_detection.burstiness_score,
                "personality_score": self.ai_detection.personality_score,
                "perfection_penalty": self.ai_detection.perfection_penalty,
                "combined": self.ai_detection.combined,
                "confidence": self.ai_detection.confidence
            },
            "thresholds_applied": self.thresholds_applied,
            "feedback_summary": self.feedback_summary,
            "feedback_details": self.feedback_details,
            "improvement_suggestions": self.improvement_suggestions,
            "processing_time_ms": self.processing_time_ms,
            "model_versions": self.model_versions,
            "cache_hit": self.cache_hit
        }

    def to_simple_dict(self) -> Dict[str, Any]:
        """Simplified dict with just key metrics."""
        return {
            "passed": self.passed,
            "score": self.combined_score,
            "relevance": self.relevance.combined,
            "novelty": self.novelty.combined,
            "coherence": self.coherence.combined,
            "human_likelihood": self.ai_detection.combined,
            "feedback": self.feedback_summary
        }


@dataclass
class VerificationRequest:
    """Input for verification."""
    response: str
    content: str
    prompt: str
    existing_responses: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    custom_thresholds: Optional[Dict[str, float]] = None
    request_id: Optional[str] = None
