from fastapi import APIRouter, Depends

from app.schemas.user import UserResponse
from app.api.deps import get_current_user
from app.db.models.user import UserORM
from app.services.user import get_me

router = APIRouter(prefix='/users')

@router.get('/me', response_model=UserResponse)
async def get_me_api(user: UserORM = Depends(get_current_user)):
    """Get info user"""
    return await get_me(user)
