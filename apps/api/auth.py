"""
Clerk JWT Authentication for FastAPI

Verifies Clerk session tokens and extracts user identity.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk, JWTError
from jose.utils import base64url_decode
import httpx
import time
from functools import lru_cache
from typing import Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)

# Clerk configuration - use environment variable or default
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API", "https://blessed-kid-47.clerk.accounts.dev")
CLERK_JWKS_URL = f"{CLERK_FRONTEND_API}/.well-known/jwks.json"

# Security scheme
security = HTTPBearer()

# Cache JWKS for performance (refresh every hour)
_jwks_cache = {"keys": None, "timestamp": 0}
CACHE_TTL = 3600  # 1 hour


@lru_cache(maxsize=128)
def get_jwks() -> Dict:
    """
    Fetch Clerk's public keys for JWT verification.
    Cached for performance.
    """
    global _jwks_cache

    # Check cache
    if _jwks_cache["keys"] and (time.time() - _jwks_cache["timestamp"]) < CACHE_TTL:
        return _jwks_cache["keys"]

    # Fetch fresh keys
    try:
        response = httpx.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        jwks = response.json()

        _jwks_cache["keys"] = jwks
        _jwks_cache["timestamp"] = time.time()

        logger.info("Fetched fresh JWKS from Clerk")
        return jwks
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        # Return cached keys if available, otherwise raise
        if _jwks_cache["keys"]:
            logger.warning("Using stale JWKS cache due to fetch error")
            return _jwks_cache["keys"]
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )


def verify_clerk_token(token: str) -> Dict:
    """
    Verify Clerk JWT token and return claims.

    Args:
        token: JWT token from Authorization header

    Returns:
        Dict with token claims including 'sub' (clerk user ID)

    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Get JWKS
        jwks = get_jwks()

        # Decode header to get key ID (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing key ID"
            )

        # Find the right key
        key = None
        for jwk_key in jwks.get("keys", []):
            if jwk_key.get("kid") == kid:
                key = jwk_key
                break

        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: key not found"
            )

        # Verify and decode token
        # Clerk tokens don't require audience verification in session tokens
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # Clerk session tokens don't have audience
                "verify_iss": False   # We trust our JWKS source
            }
        )

        # Verify expiration manually
        exp = claims.get("exp")
        if exp and time.time() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        logger.info(f"Successfully verified token for user: {claims.get('sub')}")
        return claims

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency that extracts and verifies the current user.

    Usage:
        @app.get("/protected")
        async def protected_route(user_id: str = Depends(get_current_user)):
            # user_id is the verified Clerk user ID
            ...

    Returns:
        str: Verified Clerk user ID (from 'sub' claim)

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # Verify token
    claims = verify_clerk_token(token)

    # Extract Clerk user ID from 'sub' claim
    clerk_id = claims.get("sub")

    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )

    return clerk_id


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    Optional authentication - returns None if no token provided.

    Usage:
        @app.get("/public-or-private")
        async def route(user_id: Optional[str] = Depends(get_current_user_optional)):
            if user_id:
                # Authenticated user
            else:
                # Anonymous user
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# For backward compatibility with clerk_id query parameter
# Use this only for migration period, then remove
async def get_clerk_id_legacy(clerk_id: str) -> str:
    """
    DEPRECATED: Temporary backward compatibility.
    Only use during migration to JWT auth.
    """
    logger.warning(f"Using legacy clerk_id parameter: {clerk_id} - INSECURE!")
    return clerk_id
