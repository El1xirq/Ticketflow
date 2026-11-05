from sqlalchemy import select

from uuid import UUID

from app.db.models import UserORM
from app.schemas.user import UserResponse
from app.db.session import SessionDep
from app.db.models.user_role import UserRoleORM

async def get_me(user: UserORM, session: SessionDep) -> UserResponse:
    """Get user info"""
    roles_orm = list((
        await session.execute(
            select(UserRoleORM).where(UserRoleORM.user_id == user.id)
        )
    ).scalars().all())
    roles = [r.role for r in roles_orm] 
    return UserResponse(id=user.id, email=user.email, role=roles, is_active=user.is_active)

