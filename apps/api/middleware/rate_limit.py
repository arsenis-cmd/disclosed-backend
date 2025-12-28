from fastapi import Request, HTTPException
from redis import Redis
import time
from config import get_settings

settings = get_settings()


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm"""

    def __init__(self, redis_url: str):
        try:
            self.redis = Redis.from_url(redis_url, decode_responses=False)
            self.redis.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis connection failed for rate limiting: {e}")
            self.enabled = False

    async def check(self, key: str, limit: int, window_seconds: int) -> bool:
        """
        Returns True if request is allowed, False if rate limited.
        Uses Redis ZSET for sliding window rate limiting.
        """
        if not self.enabled:
            return True  # Allow all requests if Redis is unavailable

        current = int(time.time() * 1000)  # Current time in milliseconds
        window_start = current - (window_seconds * 1000)

        try:
            pipe = self.redis.pipeline()

            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Add current request
            pipe.zadd(key, {str(current): current})

            # Count requests in window
            pipe.zcard(key)

            # Set expiry on key
            pipe.expire(key, window_seconds)

            results = pipe.execute()

            request_count = results[2]  # Result of zcard
            return request_count <= limit

        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True  # Fail open - allow request if rate limiter breaks


# Global rate limiter instance
rate_limiter = RateLimiter(settings.redis_url)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware with different limits for different endpoints.
    """
    # Get user ID from query params or use IP
    clerk_id = request.query_params.get('clerk_id')
    identifier = clerk_id or request.client.host

    # Get path and method
    path = request.url.path
    method = request.method

    # Different limits for different endpoints
    allowed = True

    if "/proofs" in path and method == "POST":
        # Proof submission: 10 per minute per user (prevent spam)
        allowed = await rate_limiter.check(f"rate:proof:{identifier}", 10, 60)

    elif "/checkout" in path and method == "POST":
        # Checkout session creation: 10 per hour per user (allow multiple retries)
        allowed = await rate_limiter.check(f"rate:checkout:{identifier}", 10, 3600)

    elif path.endswith("/campaigns") and method == "POST":
        # Campaign creation: 10 per hour per user (prevent abuse)
        allowed = await rate_limiter.check(f"rate:campaign:{identifier}", 10, 3600)

    elif "/verify" in path and method == "POST":
        # Verification: 20 per minute (expensive ML operation)
        allowed = await rate_limiter.check(f"rate:verify:{identifier}", 20, 60)

    elif "/tasks" in path and "/accept" in path and method == "POST":
        # Task acceptance: 30 per minute (prevent hoarding)
        allowed = await rate_limiter.check(f"rate:task_accept:{identifier}", 30, 60)

    elif "/connect/onboard" in path and method == "POST":
        # Stripe Connect onboarding: 5 per hour (prevent abuse)
        allowed = await rate_limiter.check(f"rate:stripe_connect:{identifier}", 5, 3600)

    else:
        # General API: 100 per minute per user
        allowed = await rate_limiter.check(f"rate:general:{identifier}", 100, 60)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down and try again later."
        )

    # Continue to next middleware/route handler
    response = await call_next(request)
    return response
