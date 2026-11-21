from uuid import UUID

from app.crud.event import (
    create_event, 
    update_event, 
    get_event_by_id, 
    publish_event, 
    cancel_event, 
    delete_event
    )
from app.db import EventORM, SessionDep
from app.schemas.event import EventCreate, EventUpdate
from app.core.exceptions.domain import PermissionDeniedException, BadRequestException, NotFoundException
from app.core.enums import EventStatus, UserRole
from app.api.deps import CurrentActor


async def create_event_serv(
        payload: EventCreate, 
        user: CurrentActor, 
        session: SessionDep,
) -> EventORM:
    """Create event, status draft"""
    event = await create_event(payload, user.user_id, session)
    return event


async def update_event_serv(
        payload: EventUpdate,
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> EventORM:
    """Patch event"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value is not user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to update this event")
    updated_event = await update_event(payload, event_id, session)
    if updated_event is None:
        return event
    return updated_event


async def publish_event_serv(
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> EventORM:
    """Publish event, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to publish this event")
    has_active_ticket = any(ticket.is_active for ticket in event.ticket_types)
    if not has_active_ticket:
        raise BadRequestException("Cannot publish event without at least one active ticket")
    return await publish_event(event_id, session)


async def cancel_event_serv(
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> EventORM:
    """Cancel event, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to cancel this event")
    return await cancel_event(event_id, session)


async def get_event_by_id_serv(
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> EventORM:
    """Get event by id, only organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id and event.status != EventStatus.PUBLISHED.value:
            raise NotFoundException('Event not found')
    return event


async def delete_event_serv(
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
):
    """Delete event, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to cancel this event")
    await delete_event(event_id, session)
    return None