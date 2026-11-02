from sqlalchemy import select

from uuid import UUID

from app.db.models import UserORM
from app.schemas.user import UserResponse, UpdateUserSchema
from app.db.session import SessionDep
from app.crud.user import update_user
from app.db.models.user_role import UserRoleORM

async def get_me(user: UserORM, session: SessionDep) -> UserResponse:
    """Get user info"""
    roles = list((
        await session.execute(
        (select(UserRoleORM).where(UserRoleORM.user_id==user.id)))
        ).scalars().all())
    return UserResponse(user.id, user.email, roles, user.is_active)


#TODO реализовать patch user
async def patch_user(user_id: UUID, session: SessionDep, payload: UpdateUserSchema) -> UserResponse:
    """Patch info user"""
    await update_user(user_id, payload, session)
    