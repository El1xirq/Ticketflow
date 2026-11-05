from fastapi import Response, Request

from app.schemas.auth import RegistrationRequest, RegistrationData, LoginRequest
from app.schemas.token import TokenResponse
from app.db.session import SessionDep
from app.core.security import (
    get_password_hash, 
    create_access_token, 
    create_refresh_token, 
    hash_refresh_token,
    verify_password,
    verify_token,
    )
from app.crud.user import create_user, get_user_by_email, get_user_by_id
from app.crud.refresh_token import (
    save_refresh_token, 
    revoke_all_user_tokens, 
    revoke_refresh_token, 
    get_refresh_by_hash
    )
from app.core.config import settings
from app.core.exceptions.domain import (
    InvalidCredentialsException, 
    PermissionDeniedException, 
    InvalidTokenException
    )


async def register_user(
        session: SessionDep, user_data: RegistrationRequest, response: Response,
) -> TokenResponse:
    """Registred user"""
    password_hash = get_password_hash(user_data.password)
    user = RegistrationData(
        **user_data.model_dump(exclude={"password"}), password_hash=password_hash
    )
    result = await create_user(user, session)

    access_token = create_access_token(result.id, user.role, user.email)
    refresh_token, expire_at = create_refresh_token(result.id)

    await save_refresh_token(
        result.id,
        hash_refresh_token(refresh_token),
        expire_at,
        session
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=not settings.debug,
        httponly=True,
        samesite="strict",
        max_age=settings.refresh_token_expire * 24 * 3600,
        path="/",
    )

    return TokenResponse(access_token=access_token)


async def login_user(
        session: SessionDep, 
        user_data: LoginRequest,
        response: Response,
) -> TokenResponse:
    """Login user with email and password"""

    user = await get_user_by_email(user_data.email, session)
    if user is None:
        raise InvalidCredentialsException()

    if not user.is_active:
        raise PermissionDeniedException("Account is inactivated")

    if not verify_password(user_data.password, user.password_hash):
        raise InvalidCredentialsException()

    user_roles = [role.role for role in user.roles]
    access_token = create_access_token(user.id, user_roles, user.email)
    refresh_token, expire_at = create_refresh_token(user.id)

    await save_refresh_token(
        user.id,
        hash_refresh_token(refresh_token),
        expire_at,
        session
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        secure=not settings.debug,
        httponly=True,
        samesite="strict",
        max_age=settings.refresh_token_expire * 24 * 3600,
        path="/",
    )

    return TokenResponse(access_token=access_token)


async def get_refresh_user(
    request: Request, response: Response, session: SessionDep
) -> TokenResponse:
    """Refresh token rotation, new access token"""
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        raise InvalidTokenException()

    verify_token(refresh_token, "refresh")
    token_hash = hash_refresh_token(refresh_token)

    record = await get_refresh_by_hash(token_hash, session)
    if record is None:
        raise InvalidTokenException()
    if record.revoked_at is not None:
        await revoke_all_user_tokens(record.user_id, session)
        raise InvalidTokenException()
    await revoke_refresh_token(record, session)

    user = await get_user_by_id(record.user_id, session)
    user_roles = [role.role for role in user.roles]

    new_access_token = create_access_token(user.id, user_roles, user.email)
    new_refresh_token, expires_at = create_refresh_token(user.id)

    await save_refresh_token(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_token),
        expires_at=expires_at,
        session=session,
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        secure=not settings.debug,
        httponly=True,
        samesite="strict",
        max_age=settings.refresh_token_expire * 24 * 3600,
        path="/",
    )

    return TokenResponse(access_token=new_access_token)


async def logout_user(
    request: Request, response: Response, session: SessionDep
) -> None:
    """Logout user: revoke user and clear cookie"""
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is not None:
        token_hash = hash_refresh_token(refresh_token)
        record = await get_refresh_by_hash(token_hash, session)
        if record is not None and record.revoked_at is None:
            await revoke_refresh_token(record, session)

    response.delete_cookie("refresh_token", path="/")
    