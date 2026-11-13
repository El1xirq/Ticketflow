from fastapi import APIRouter

from .endpoints import event_router, ticket_type_router

router = APIRouter(prefix='/v1')

router.include_router(event_router)
router.include_router(ticket_type_router)