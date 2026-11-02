from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends

from uuid import UUID

from app.db.session import SessionDep
from app.db.models.user import UserORM
from app.db.models.user_role import UserRole
from app.core.security import verify_token
from app.core.exceptions.domain import InvalidTokenException, PermissionDeniedException
from app.crud.user import get_user_by_id

bearer_schema = HTTPBearer()

async def get_current_user(
        session: SessionDep, creds: HTTPAuthorizationCredentials = Depends(bearer_schema)
) -> UserORM:
    """Extarct user from bearer token"""
    payload = verify_token(creds.credentials, "access")

    sub = payload.get('sub')
    if not sub:
        raise InvalidTokenException("Invalid token payload")
    try: 
        user_id = UUID(sub)
    except (TypeError, ValueError):
        raise InvalidTokenException("Invalid token payload")

    user = await get_user_by_id(user_id, session)
    return user

from fastapi import Depends
from typing import Sequence

def require_role(*roles: UserRole):
    """Only allows access to users with specified roles"""
    
    async def checker(user: UserORM = Depends(get_current_user)) -> UserORM:
        user_role_values = [user_role.role for user_role in user.roles]
        
        if not any(role in roles for role in user_role_values):
            raise PermissionDeniedException(detail="Insufficient permissions")
            
        return user
        
    return checker

