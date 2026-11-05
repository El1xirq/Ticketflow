from fastapi import APIRouter, Depends

from app.schemas.user import UserResponse
from app.api.deps import get_current_user
from app.db.models.user import UserORM
from app.services.user import get_me
from app.db.session import SessionDep

router = APIRouter(prefix='/users', tags=['Users'])

@router.get('/me', response_model=UserResponse)
async def get_me_api(
    session: SessionDep,
    user: UserORM = Depends(get_current_user)
    ):
    """Get info user"""
    return await get_me(user, session)


