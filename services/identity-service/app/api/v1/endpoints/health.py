from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionDep

router = APIRouter(prefix='/health', tags=['Health'])

@router.get('/live', include_in_schema=False)
async def live_health():
    return {'status': 'ok'}

@router.get('/ready', include_in_schema=False)
async def ready(session: SessionDep):
    await session.execute(text('SELECT 1'))
    return {'status': 'ok', 'database': 'ok'}
