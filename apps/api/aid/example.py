"""
Example usage of the AID engine
"""

from aid import AIDEngine, AIDConfig

# Create engine with custom config
config = AIDConfig(
    perplexity_model="gpt2-medium",
    use_gpu=True,
    min_combined=0.55
)
engine = AIDEngine(config)

# Example verification
result = engine.verify_sync(
    response="I live in a small apartment with my partner, and we've been struggling with keeping our home organized. This smart storage system would be perfect for maximizing our limited space, especially the modular shelving that can fit in our narrow hallway. We've tried several organization solutions before, but they were either too bulky or didn't hold enough. The fact that this adapts to different room sizes is exactly what we need.",
    content="Introducing the SmartHome Hub X1 - the revolutionary home automation system that learns your habits and optimizes your living space. Features include: AI-powered climate control, voice-activated lighting, and a mobile app for remote management.",
    prompt="Describe how this product would help your situation",
    metadata={"time_spent_seconds": 180, "revision_count": 2}
)

print(f"Passed: {result.passed}")
print(f"Score: {result.combined_score:.2f}")
print(f"Feedback: {result.feedback_summary}")
print(f"\nDetailed Scores:")
print(f"  Relevance: {result.relevance.combined:.2f}")
print(f"  Irreducibility: {result.perplexity.irreducibility_score:.2f}")
print(f"  Novelty: {result.novelty.combined:.2f}")
print(f"  Coherence: {result.coherence.combined:.2f}")
print(f"  Effort: {result.effort.combined:.2f}")
print(f"  Human Likelihood: {result.ai_detection.combined:.2f}")
