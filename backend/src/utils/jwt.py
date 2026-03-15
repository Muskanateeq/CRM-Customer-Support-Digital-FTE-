"""
JWT Token Utilities

Utilities for decoding and validating Better Auth JWT tokens.
Uses JWKS (JSON Web Key Set) for token verification.
"""

import os
import jwt
import requests
from typing import Optional, Dict, Any
from functools import lru_cache

from src.utils.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """
    Get JWKS URL from Better Auth.

    Returns:
        JWKS URL for fetching public keys
    """
    better_auth_url = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
    return f"{better_auth_url}/api/auth/jwks"


@lru_cache(maxsize=10)
def fetch_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Better Auth.

    Cached to avoid repeated requests.

    Returns:
        JWKS dictionary containing public keys
    """
    try:
        jwks_url = get_jwks_url()
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch JWKS: {e}")
        return {"keys": []}


def get_signing_key(token: str) -> Optional[str]:
    """
    Get the signing key for a JWT token from JWKS.

    Args:
        token: JWT token string

    Returns:
        Signing key (PEM format) or None if not found
    """
    try:
        # Decode token header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            logger.warning("Token does not contain 'kid' in header")
            return None

        # Fetch JWKS
        jwks = fetch_jwks()

        # Find matching key
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM format
                from jwt.algorithms import RSAAlgorithm
                public_key = RSAAlgorithm.from_jwk(key)
                return public_key

        logger.warning(f"No matching key found for kid: {kid}")
        return None

    except Exception as e:
        logger.error(f"Failed to get signing key: {e}")
        return None


def decode_better_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate Better Auth JWT token.

    This function:
    1. Fetches the JWKS from Better Auth
    2. Finds the matching public key
    3. Verifies the token signature
    4. Validates token claims (exp, iss, aud)
    5. Returns the decoded payload

    Args:
        token: JWT token string from Authorization header

    Returns:
        Decoded token payload or None if invalid

    Example payload:
        {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "session_id": "abc123",
            "iss": "http://localhost:3000",
            "aud": "http://localhost:3000",
            "exp": 1234567890
        }
    """
    try:
        # Get signing key from JWKS
        signing_key = get_signing_key(token)

        if not signing_key:
            logger.warning("Could not get signing key for token")
            return None

        # Decode and verify token
        better_auth_url = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            issuer=better_auth_url,
            audience=better_auth_url,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            }
        )

        logger.info(f"Successfully decoded token for user: {payload.get('user_id')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to decode token: {e}", exc_info=True)
        return None


def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid.

    Args:
        token: JWT token string

    Returns:
        True if token is valid, False otherwise
    """
    payload = decode_better_auth_token(token)
    return payload is not None
