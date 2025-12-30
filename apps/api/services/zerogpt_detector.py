"""
ZeroGPT API Integration for AI Text Detection

Uses RapidAPI to detect AI-generated text with high accuracy.
Stores all data for future ML model training.
"""

import logging
import httpx
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ZeroGPTDetector:
    """
    AI detector using ZeroGPT API via RapidAPI.

    Cost: $0.034 per 1,000 words (highly cost-effective for data collection)
    """

    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.api_host = "zerogpt.p.rapidapi.com"
        self.api_url = f"https://{self.api_host}/api/v1/detectText"

        if not self.api_key:
            logger.warning("RAPIDAPI_KEY not set - ZeroGPT detector will not work")
        else:
            logger.info("ZeroGPT detector initialized")

    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using ZeroGPT API.

        Returns:
            {
                'score': float (0-1, higher = more human),
                'confidence': float (0-1),
                'analysis': dict (detailed breakdown),
                'raw_response': dict (full API response for training)
            }
        """
        if not self.api_key:
            raise Exception("ZeroGPT API key not configured")

        try:
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": self.api_host
            }

            payload = {
                "input_text": text
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

            # Store raw response for ML training
            raw_response = data.copy()

            # Parse ZeroGPT response
            # ZeroGPT returns isHuman, fakePercentage, textWords, etc.
            is_human = data.get('isHuman', False)
            fake_percentage = data.get('fakePercentage', 0)  # 0-100
            text_words = data.get('textWords', 0)

            # Convert to our 0-1 scale (higher = more human)
            # fake_percentage: 0% = fully human, 100% = fully AI
            human_percentage = 100 - fake_percentage
            score = human_percentage / 100.0  # Convert to 0-1

            # Estimate confidence based on certainty of score
            # Scores close to 0 or 1 are more confident
            distance_from_middle = abs(score - 0.5)
            confidence = 0.5 + (distance_from_middle * 2) * 0.5
            confidence = max(0.5, min(1.0, confidence))

            # Create detailed analysis matching our schema
            analysis = {
                'ai_percentage': {
                    'score': fake_percentage / 100.0,
                    'interpretation': f"{'Low' if fake_percentage < 30 else 'Moderate' if fake_percentage < 70 else 'High'} AI probability"
                },
                'human_percentage': {
                    'score': human_percentage / 100.0,
                    'interpretation': f"{'Low' if human_percentage < 30 else 'Moderate' if human_percentage < 70 else 'High'} human probability"
                },
                'is_human': {
                    'score': 1.0 if is_human else 0.0,
                    'interpretation': "Classified as human-written" if is_human else "Classified as AI-generated"
                },
                'word_count': {
                    'score': text_words / 10000.0,  # Normalize
                    'interpretation': f"{text_words} words analyzed"
                },
                'api_provider': {
                    'score': 1.0,
                    'interpretation': "ZeroGPT API via RapidAPI"
                },
                'confidence_level': {
                    'score': confidence,
                    'interpretation': f"{'High' if confidence > 0.8 else 'Moderate' if confidence > 0.6 else 'Low'} confidence"
                }
            }

            logger.info(
                f"ZeroGPT analysis: score={score:.3f}, fake%={fake_percentage:.1f}, "
                f"isHuman={is_human}, words={text_words}"
            )

            return {
                'score': round(score, 3),
                'confidence': round(confidence, 3),
                'analysis': analysis,
                'raw_response': raw_response  # Store for ML training
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"ZeroGPT API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"ZeroGPT API error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("ZeroGPT API timeout")
            raise Exception("ZeroGPT API timeout - please try again")
        except Exception as e:
            logger.error(f"ZeroGPT API error: {e}", exc_info=True)
            raise Exception(f"ZeroGPT API error: {str(e)}")
