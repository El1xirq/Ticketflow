from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=['PublicKey'])

@router.get('/.well-known/jwks.json')
async def get_public_key():
    return {
        "public_key": settings.public_key,
        "algorithm": settings.algorithm,
    }