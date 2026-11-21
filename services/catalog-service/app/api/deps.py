from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions.domain import (
    InvalidTokenException,
    PermissionDeniedException,
)
from app.core.security import verify_access_token


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentActor:
    user_id: UUID
    roles: frozenset[str]


async def get_current_actor(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentActor:
    if credentials is None:
        raise InvalidTokenException()

    payload = await verify_access_token(credentials.credentials)

    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise InvalidTokenException("Invalid token payload")

    try:
        user_id = UUID(sub)
    except ValueError:
        raise InvalidTokenException("Invalid token payload")

    roles_claim = payload.get("roles")
    if not isinstance(roles_claim, list) or not all(
        isinstance(role, str) for role in roles_claim
    ):
        raise InvalidTokenException("Invalid token roles")

    return CurrentActor(
        user_id=user_id,
        roles=frozenset(roles_claim),
    )


def require_role(*required_roles: str):
    async def checker(
        actor: CurrentActor = Depends(get_current_actor),
    ) -> CurrentActor:
        if actor.roles.isdisjoint(required_roles):
            raise PermissionDeniedException(
                detail="Insufficient permissions"
            )

        return actor

    return checker