import httpx
import jwt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.exceptions.domain import InvalidTokenException

_cached_key_data: dict | None = None


async def get_public_key_data(force_refresh: bool = False) -> dict:
    """
    Return public key from memory.
    If the key does not yet exist,
    or if the `force_refresh=True` flag is passed,
    it downloads the key from the identity service.
    """
    global _cached_key_data

    if _cached_key_data is not None and not force_refresh:
        return _cached_key_data

    url = f"{settings.identity_url.rstrip('/')}/.well-known/jwks.json"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            _cached_key_data = response.json()
            return _cached_key_data
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The authorization service is temporarily unavailable",
        )


def decode_jwt(token: str, key_data: dict) -> dict:
    """Decode token"""
    return jwt.decode(
        jwt=token,
        key=key_data["public_key"],
        algorithms=[key_data["algorithm"]],
    )


async def verify_access_token(token: str) -> dict:
    """Verify JWT access token using cached or fresh public key."""
    key_data = await get_public_key_data()

    try:
        return decode_jwt(token, key_data)

    except jwt.InvalidSignatureError:
        fresh_key_data = await get_public_key_data(force_refresh=True)
        try:
            return decode_jwt(token, fresh_key_data)
        except jwt.PyJWTError:
            raise InvalidTokenException("Invalid token signature")

    except jwt.ExpiredSignatureError:
        raise InvalidTokenException("Token has expired")

    except jwt.PyJWTError:
        raise InvalidTokenException("Invalid token")
