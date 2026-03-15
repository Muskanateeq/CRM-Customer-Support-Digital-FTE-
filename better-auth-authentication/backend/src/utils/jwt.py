"""
JWT Token Utilities for Better Auth Integration

Handles JWT token validation using Better Auth's JWKS endpoint.
Verifies JWT tokens issued by Better Auth on the frontend.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from functools import lru_cache
import base64

import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from src.config import settings


# Cache for JWKS (JSON Web Key Set)
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: Optional[datetime] = None
JWKS_CACHE_DURATION = timedelta(hours=24)  # Cache JWKS for 24 hours


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """
    Get the JWKS URL from Better Auth.

    Returns:
        JWKS endpoint URL
    """
    return getattr(settings, 'BETTER_AUTH_JWKS_URL', 'http://localhost:3000/api/auth/jwks')


def fetch_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS (JSON Web Key Set) from Better Auth.

    Returns:
        JWKS dictionary containing public keys

    Raises:
        Exception: If JWKS fetch fails
    """
    global _jwks_cache, _jwks_cache_time

    # Check if cache is valid
    if _jwks_cache and _jwks_cache_time:
        if datetime.utcnow() - _jwks_cache_time < JWKS_CACHE_DURATION:
            return _jwks_cache

    # Fetch fresh JWKS
    try:
        jwks_url = get_jwks_url()
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()

        jwks = response.json()

        # Update cache
        _jwks_cache = jwks
        _jwks_cache_time = datetime.utcnow()

        return jwks
    except Exception as e:
        # If cache exists, use it even if expired
        if _jwks_cache:
            return _jwks_cache
        raise Exception(f"Failed to fetch JWKS from Better Auth: {str(e)}")


def get_signing_key(token: str, jwks: Dict[str, Any]) -> Optional[Ed25519PublicKey]:
    """
    Get the signing key from JWKS based on the token's kid (key ID).

    Args:
        token: JWT token string
        jwks: JWKS dictionary

    Returns:
        Ed25519PublicKey if found, None otherwise
    """
    try:
        # Decode token header without verification to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not kid:
            return None

        # Find the key with matching kid
        keys = jwks.get('keys', [])
        for key in keys:
            if key.get('kid') == kid:
                # Extract Ed25519 public key from JWK
                if key.get('kty') == 'OKP' and key.get('crv') == 'Ed25519':
                    # Get the x parameter (base64url encoded public key)
                    x = key.get('x')
                    if not x:
                        return None

                    # Decode base64url (add padding if needed)
                    # Base64url uses - and _ instead of + and /
                    x = x.replace('-', '+').replace('_', '/')
                    # Add padding
                    padding = 4 - (len(x) % 4)
                    if padding != 4:
                        x += '=' * padding

                    # Decode to bytes
                    public_key_bytes = base64.b64decode(x)

                    # Create Ed25519PublicKey object
                    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
                    return public_key

        return None
    except Exception as e:
        print(f"Error extracting signing key: {str(e)}")
        return None


def decode_better_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token from Better Auth using JWKS.

    Args:
        token: JWT token string from Better Auth

    Returns:
        Dictionary containing the decoded claims if valid, None if invalid

    Example:
        >>> payload = decode_better_auth_token(token)
        >>> if payload:
        >>>     user_id = payload.get("user_id")
    """
    try:
        # Fetch JWKS
        jwks = fetch_jwks()

        # Get signing key (Ed25519PublicKey object)
        signing_key = get_signing_key(token, jwks)
        if not signing_key:
            print("Token decode error: Unable to find signing key")
            return None

        # Get issuer and audience from settings
        issuer = getattr(settings, 'BETTER_AUTH_URL', 'http://localhost:3000')
        audience = issuer  # Better Auth uses same value for iss and aud by default

        # Verify and decode token using PyJWT
        # PyJWT properly supports EdDSA/Ed25519
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=['EdDSA'],
            issuer=issuer,
            audience=audience,
            options={
                'verify_signature': True,
                'verify_exp': True,
                'verify_iat': True,
                'verify_iss': True,
                'verify_aud': True,
            }
        )

        return payload
    except jwt.ExpiredSignatureError:
        print("JWT verification failed: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"JWT verification failed: {str(e)}")
        return None
    except Exception as e:
        print(f"Token decode error: {str(e)}")
        return None


def verify_better_auth_token(token: str) -> bool:
    """
    Verify if a Better Auth JWT token is valid.

    Args:
        token: JWT token string from Better Auth

    Returns:
        True if token is valid, False otherwise
    """
    return decode_better_auth_token(token) is not None


def get_user_id_from_better_auth_token(token: str) -> Optional[str]:
    """
    Extract user_id from a Better Auth JWT token.

    Args:
        token: JWT token string from Better Auth

    Returns:
        User ID if token is valid and contains user_id, None otherwise

    Example:
        >>> user_id = get_user_id_from_better_auth_token(token)
        >>> if user_id:
        >>>     # User is authenticated
    """
    payload = decode_better_auth_token(token)
    if payload:
        # Better Auth JWT payload structure: { "user_id": "...", "email": "...", "session_id": "..." }
        return payload.get("user_id")
    return None


# Legacy functions for backward compatibility (deprecated)
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    DEPRECATED: This function is deprecated. Better Auth handles token creation.

    Create a JWT access token (legacy function).
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    DEPRECATED: Use decode_better_auth_token() instead.

    Decode and validate a JWT access token (legacy function).
    """
    return decode_better_auth_token(token)


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    DEPRECATED: Use get_user_id_from_better_auth_token() instead.

    Extract user_id from a JWT token (legacy function).
    """
    return get_user_id_from_better_auth_token(token)
