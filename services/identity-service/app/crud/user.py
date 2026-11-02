from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from uuid import UUID

from app.db.session import SessionDep
from app.db.models import UserORM
from app.db.models import UserRoleORM, UserRole
from app.schemas.auth import RegistrationData
from app.schemas.user import UpdateUserSchema
from app.core.exceptions.domain import (
    NotFoundException,
    DatabaseException,
    ConflictException,
)


async def get_user_by_id(user_id: UUID, session: SessionDep) -> UserORM:
    """Get user by id"""
    stmt = select(UserORM).where(UserORM.id == user_id, UserORM.is_active.is_(True))
    result = (await session.execute(stmt)).scalar_one_or_none()
    if result is None:
        raise NotFoundException("User not found")
    return result


async def get_user_by_email(email: str, session: SessionDep) -> UserORM | None:
    """Get user by email"""
    stmt = select(UserORM).where(UserORM.email == email)
    return (await session.execute(stmt)).scalar_one_or_none()


async def get_active_user_by_email(email: str, session: SessionDep) -> UserORM:
    """Get user by email is_active = True"""
    stmt = select(UserORM).where(UserORM.email == email, UserORM.is_active.is_(True))
    user = (await session.execute(stmt)).scalar_one_or_none()
    if user is None:
        raise NotFoundException("User not found")
    return user


async def create_user(user: RegistrationData, session: SessionDep) -> UserORM:
    """Create user"""
    try:
        new_user = UserORM(
            email=user.email, password_hash=user.password_hash
        )
        await session.flush(new_user)
        new_user_roles = UserRoleORM(
            user_id=new_user.id, role=UserRole.CUSTOMER.value,
        )
        session.add(new_user_roles)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ConflictException("User with this email already exists")
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()

    await session.refresh(new_user)
    return new_user


async def update_user(
    user_id: UUID, 
    user_update: UpdateUserSchema, 
    session: SessionDep
) -> UserORM:
    """Patch user and their roles"""
    user = await get_user_by_id(user_id, session)
    
    update_data = user_update.model_dump(exclude_none=True)
    if not update_data:
        return user

    roles_to_update = update_data.pop("roles", None)

    try:
        if update_data:
            user_stmt = update(UserORM).where(UserORM.id == user_id).values(update_data)
            await session.execute(user_stmt)

        if roles_to_update is not None:
            delete_roles_stmt = delete(UserRoleORM).where(UserRoleORM.user_id == user_id)
            await session.execute(delete_roles_stmt)
            
            if roles_to_update:
                insert_roles_stmt = insert(UserRoleORM).values(
                    [{"user_id": user_id, "role": role} for role in roles_to_update]
                )
                await session.execute(insert_roles_stmt)

        await session.commit()
        
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    
    return await get_user_by_id(user_id, session)



async def delete_user(user_id: UUID, session: SessionDep) -> bool:
    """Soft delete user"""
    stmt = (
        update(UserORM)
        .where(UserORM.id == user_id, UserORM.is_active.is_(True))
        .values(is_active=False)
        .returning(UserORM.id)
    )
    try:
        result = await session.execute(stmt)
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()

    if result.scalar_one_or_none() is None:
        raise NotFoundException("User not found")
    return True