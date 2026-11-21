from fastapi import APIRouter, Depends

from uuid import UUID

from app.api.deps import require_role, CurrentActor
from app.services.event import (
    create_event_serv, 
    update_event_serv, 
    cancel_event_serv, 
    publish_event_serv, 
    get_event_by_id_serv,
    delete_event_serv,
)
from app.schemas.event import EventResponse, EventCreate, EventUpdate
from app.crud.event import get_list_published_events
from app.db import SessionDep
from app.api.deps import get_current_actor, CurrentActor


router = APIRouter(prefix='/events', tags=['Event'])

@router.post('', response_model=EventResponse, status_code=201)
async def create_event_api(
    payload: EventCreate,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin')),
):
    """Create event organizer"""
    event = await create_event_serv(payload, user, session)
    return event


@router.patch('/{event_id}', response_model=EventResponse)
async def patch_event_api(
    payload: EventUpdate,
    event_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin')),
):
    """PATCH event organizer"""
    event = await update_event_serv(payload, event_id, user, session)
    return event


@router.get('', response_model=list[EventResponse])
async def get_events_api(session: SessionDep):
    """Get all published events"""
    events = await get_list_published_events(session)
    return events


@router.get('/{event_id}', response_model=EventResponse)
async def get_event_by_id_api(
    event_id: UUID, 
    session: SessionDep, 
    user: CurrentActor = Depends(get_current_actor)
):
    """Get event by id"""
    event = await get_event_by_id_serv(event_id, user, session)
    return event


@router.post('/{event_id}/publish', response_model=EventResponse)
async def publish_event_api(
    event_id: UUID, 
    session: SessionDep, 
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Publish event, organizer"""
    event = await publish_event_serv(event_id, user, session)
    return event


@router.post('/{event_id}/cancel', status_code=204)
async def cancel_event_api(
    event_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Cancel event, organizer"""
    await cancel_event_serv(event_id, user, session)
    return None


@router.delete('/{event_id}/delete', status_code=204)
async def delete_event_api(
    event_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Delete event, organizer"""
    await delete_event_serv(event_id, user, session)
    return None