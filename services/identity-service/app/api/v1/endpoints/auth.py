from fastapi import APIRouter, Response, Request

from app.schemas.token import TokenResponse
from app.schemas.auth import RegistrationRequest, LoginRequest
from app.services.auth import register_user, login_user, logout_user, get_refresh_user
from app.db.session import SessionDep

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/register', response_model=TokenResponse, status_code=201)
async def registred_user_api(session: SessionDep, response: Response, payload: RegistrationRequest):
    """Sign up a user"""
    token = await register_user(session, payload, response)
    return token


@router.post("/login", response_model=TokenResponse)
async def login_user_api(session: SessionDep, response: Response, payload: LoginRequest):
    """Sign in a user"""
    token = await login_user(session, payload, response)
    return token


@router.post('/logout', status_code=204)
async def logout_user_api(request: Request, response: Response, session: SessionDep):
    """Logout user"""
    await logout_user(request, response, session)
    return None


@router.post('/refresh', response_model=TokenResponse)
async def get_refresh_token_api(
    request: Request,
    response: Response,
    session: SessionDep,
    ):
    """Get new tokens"""
    token = await get_refresh_user(request, response, session)
    return token