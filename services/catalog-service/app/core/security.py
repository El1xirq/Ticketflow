from typing import Any

import jwt

from app.core.config import settings
from app.core.exceptions.domain import InvalidTokenException


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_public_key,
            algorithms=[settings.algorithm],
        )
    except jwt.InvalidTokenError:
        raise InvalidTokenException()

    if payload.get("type") != "access":
        raise InvalidTokenException()

    return payload