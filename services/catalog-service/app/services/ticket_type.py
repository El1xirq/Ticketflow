from uuid import UUID

from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate
from app.db import SessionDep, TicketTypeORM
from app.crud.event import get_event_by_id
from app.core.exceptions.domain import PermissionDeniedException, NotFoundException
from app.crud.ticket_type import (
    create_ticket_type, 
    get_ticket_type_by_id, 
    update_ticket_type,
    delete_ticket_type
    )
from app.api.deps import CurrentActor
from app.core.enums import UserRole


async def create_ticket_serv(
        payload: TicketTypeCreate,
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> TicketTypeORM:
    """Create ticket, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to create a ticket for this event")
    ticket = await create_ticket_type(payload, event_id, session)
    return ticket


async def update_ticket_serv(
        payload: TicketTypeUpdate,
        ticket_type_id: UUID,
        user: CurrentActor,
        event_id: UUID,
        session: SessionDep,
) -> TicketTypeORM:
    """Patch ticket, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to change this ticket")

    ticket_type = await get_ticket_type_by_id(ticket_type_id, session)
    if ticket_type.event_id != event.id:
        raise NotFoundException("Ticket type not found")

    ticket = await update_ticket_type(payload, ticket_type_id, session)
    return ticket


async def delete_ticket_serv(
        ticket_type_id: UUID,
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> None:
    """Delete ticket, check organizer"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise PermissionDeniedException("You do not have permission to change this ticket")

    ticket_type = await get_ticket_type_by_id(ticket_type_id, session)
    if ticket_type.event_id != event.id:
        raise NotFoundException("Ticket type not found")
    return await delete_ticket_type(ticket_type_id, session)


async def get_ticket_type_id_serv(
        ticket_type_id: UUID,
        event_id: UUID,
        user: CurrentActor,
        session: SessionDep,
) -> TicketTypeORM:
    """Get ticket_type organizer or admin by id"""
    event = await get_event_by_id(event_id, session)
    if UserRole.ADMIN.value not in user.roles:
        if event.organizer_id != user.user_id:
            raise NotFoundException('Ticket type not found')
    ticket_type = await get_ticket_type_by_id(ticket_type_id, session)
    if ticket_type.event_id != event_id:
        raise NotFoundException('Ticket type not found')
    return ticket_type