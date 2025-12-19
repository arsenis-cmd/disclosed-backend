# AID - Algorithmic Irreducibility Detection

**Version 1.0.0**

A production-ready verification engine for Proof of Consideration that measures how expensive it would be to fake genuine human engagement.

## Overview

AID (Algorithmic Irreducibility Detection) is a sophisticated verification system that analyzes responses across 6 dimensions to determine if they demonstrate authentic human consideration. Unlike binary AI detectors, AID produces continuous scores that feed into economic calculations about cost-to-fake.

## Core Philosophy

**The goal is not to detect AI.** The goal is to measure **irreducibility** - how much unique cognitive work went into a response that can't be easily compressed or replicated.

## Architecture

```
AID Engine
├── Perplexity Scorer    → Measures linguistic surprise/unpredictability
├── Relevance Scorer     → Measures engagement with content
├── Novelty Scorer       → Measures uniqueness and personalization
├── Coherence Scorer     → Measures text quality and structure
├── Effort Estimator     → Measures cognitive investment
└── AI Detector          → Detects AI-typical patterns
```

## Scoring Components

### 1. Perplexity Scorer (`perplexity.py`)

Measures how "surprised" a language model is by the text.

**Key Metrics:**
- **Unconditional Perplexity**: How predictable is the response alone?
- **Conditional Perplexity**: How predictable given the source content?
- **Irreducibility Score**: Degree to which content doesn't explain response

**Formula:** `irreducibility = (conditional_ppl / unconditional_ppl - 0.3) / 1.2`

**Interpretation:**
- High perplexity = unpredictable = human-like
- Low perplexity = predictable = AI-like
- Reduction ratio shows if response just paraphrases content

### 2. Relevance Scorer (`relevance.py`)

Measures how well the response engages with content and prompt.

**Techniques:**
- Semantic similarity (sentence embeddings)
- Keyword overlap analysis
- Topic coherence across sentences

**Combined:** 35% content similarity + 30% prompt similarity + 20% keywords + 15% coherence

### 3. Novelty Scorer (`novelty.py`)

Measures uniqueness and originality.

**Checks:**
- Distance from original content (not just paraphrasing)
- Distance from other responses (corpus comparison)
- Personalization markers ("I", "my", specific details)
- Template phrase detection

**Combined:** 30% content distance + 30% corpus novelty + 25% personalization + 15% anti-template

### 4. Coherence Scorer (`coherence.py`)

Measures text quality and structure.

**Analysis:**
- Sentence structure variety
- Logical connectors ("because", "however", etc.)
- Completeness (proper ending)
- Semantic coherence between sentences
- Appropriate length

**Combined:** 20% structure + 20% flow + 20% completeness + 25% semantic + 15% length

### 5. Effort Estimator (`effort.py`)

Estimates cognitive investment.

**Factors:**
- Time spent (reading + writing estimate)
- Response complexity (new vocabulary, long words, subclauses)
- Revision count
- Typing patterns (if available)

**Combined:** Weighted based on available metadata

### 6. AI Detector (`ai_detection.py`)

Detects AI-typical patterns using heuristics.

**Signals:**
- AI phrases ("furthermore", "delve", "it's worth noting")
- Human markers ("don't", "lol", "i guess", "honestly")
- Burstiness (sentence length variance - humans vary more)
- Personality markers (!, ..., ?)

**Combined:** 40% phrase score + 35% burstiness + 25% personality

## Combined Scoring

Uses **weighted geometric mean** to ensure all dimensions matter:

```python
score = exp(Σ(weight_i * log(score_i + ε))) - ε
```

**Weights:**
- Relevance: 20%
- Irreducibility (content): 20%
- Irreducibility (AI): 15%
- Novelty: 20%
- Coherence: 15%
- Effort: 10%

**Why geometric mean?** One very low score tanks the combined score. You can't compensate for terrible relevance with great coherence.

## Configuration

Default configuration in `AIDConfig`:

```python
config = AIDConfig(
    perplexity_model="gpt2-medium",
    embedding_model="all-MiniLM-L6-v2",
    use_gpu=True,

    # Thresholds
    min_relevance=0.60,
    min_irreducibility=0.55,
    min_novelty=0.55,
    min_coherence=0.50,
    min_combined=0.55,

    # Weights (must sum to ~1.0)
    weight_relevance=0.20,
    weight_irreducibility_content=0.20,
    weight_irreducibility_ai=0.15,
    weight_novelty=0.20,
    weight_coherence=0.15,
    weight_effort=0.10,

    enable_cache=True,
    cache_backend="memory"
)
```

## Usage

### Basic Usage

```python
from aid import AIDEngine, AIDConfig

# Create engine
engine = AIDEngine(AIDConfig())

# Verify a response
result = engine.verify_sync(
    response="I live in a small apartment...",
    content="Introducing the SmartHome Hub...",
    prompt="Describe how this would help your situation",
    metadata={"time_spent_seconds": 180}
)

print(f"Passed: {result.passed}")
print(f"Score: {result.combined_score:.2f}")
print(f"Feedback: {result.feedback_summary}")
```

### Custom Thresholds

```python
result = await engine.verify(
    response=response_text,
    content=content_text,
    prompt=prompt_text,
    custom_thresholds={
        'min_relevance': 0.70,  # Stricter
        'min_combined': 0.60
    }
)
```

### With Existing Responses (Novelty Check)

```python
result = await engine.verify(
    response=new_response,
    content=content_text,
    prompt=prompt_text,
    existing_responses=[resp1, resp2, resp3]  # Check for duplicates
)
```

## FastAPI Integration

The AID engine is integrated into the FastAPI backend via an adapter:

```python
# services/verification/engine.py
from aid import AIDEngine, AIDConfig

class VerificationEngine:
    def __init__(self):
        self.aid_engine = AIDEngine(AIDConfig())

    async def verify(self, proof_text, content_text, ...):
        aid_result = await self.aid_engine.verify(...)
        return convert_to_legacy_format(aid_result)
```

This maintains backward compatibility with existing API endpoints while using the new AID engine under the hood.

## Performance

**Target Performance:**
- GPU: < 2 seconds
- CPU: < 10 seconds
- Memory cache: Repeated requests near-instant

**Actual Performance** (on typical responses):
- First run (model loading): ~5-15 seconds
- Subsequent runs: 1-3 seconds (GPU) / 5-8 seconds (CPU)
- Cached results: < 10ms

**Optimization:**
- Models loaded once on startup
- In-memory caching of results
- Parallel execution of independent scorers
- Embedding model shared across components

## Model Dependencies

**Required:**
- `transformers` (GPT-2 for perplexity)
- `sentence-transformers` (embeddings)
- `torch` (deep learning backend)
- `numpy` (numerical operations)

**Size:**
- GPT-2 Medium: ~600 MB
- Sentence transformers: ~100 MB
- Total: ~700 MB disk space

## Calibration

The thresholds are based on initial estimates. For production, calibrate using:

1. **Human Baseline**: Collect genuine human responses
2. **AI Baseline**: Generate synthetic responses
3. **ROC Analysis**: Find optimal threshold for your use case
4. **A/B Testing**: Measure impact on participation and quality

**Recommended Calibration Dataset Size:**
- 100+ genuine human responses
- 100+ low-effort responses
- 100+ AI-generated responses
- Various content types and prompts

## Limitations

**Known Issues:**
1. **Cold Start**: First request is slow (model loading)
2. **GPU Required**: CPU mode is 3-5x slower
3. **English Only**: Models trained primarily on English
4. **Context Length**: Limited to 1024 tokens
5. **Perplexity Calibration**: Thresholds may need tuning

**Not Detected:**
- High-quality AI with human editing
- Humans who write like AI
- Domain-specific jargon (may look like high perplexity)

## Future Enhancements

**Planned:**
- [ ] Multi-language support
- [ ] Fine-tuned models on domain data
- [ ] Redis caching backend
- [ ] Streaming/progressive scoring
- [ ] Explainability dashboard
- [ ] Adversarial robustness testing
- [ ] Lightweight mode (no perplexity)

## Files

```
aid/
├── __init__.py          # Package exports
├── types.py             # Type definitions
├── config.py            # Configuration management
├── engine.py            # Main orchestrator
├── perplexity.py        # Perplexity scorer
├── relevance.py         # Relevance scorer
├── novelty.py           # Novelty scorer
├── coherence.py         # Coherence scorer
├── effort.py            # Effort estimator
├── ai_detection.py      # AI detector
├── example.py           # Usage example
└── README.md            # This file
```

## Credits

Built following the comprehensive specification for Algorithmic Irreducibility Detection.

**License:** Proprietary (Part of Proof of Consideration platform)

---

For questions or issues, contact the development team.
