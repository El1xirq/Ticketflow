from fastapi import APIRouter, Depends

from uuid import UUID

from app.db import SessionDep
from app.crud.ticket_type import get_events_active_ticket
from app.schemas.ticket_type import TicketTypeResponse, TicketTypeCreate, TicketTypeUpdate
from app.api.deps import CurrentActor, require_role
from app.services.ticket_type import (
    create_ticket_serv, 
    update_ticket_serv, 
    delete_ticket_serv, 
    get_ticket_type_id_serv
    )


router = APIRouter(prefix='/events', tags=['TicketType'])


@router.post('/{event_id}/ticket-types', response_model=TicketTypeResponse, status_code=201)
async def create_ticket_type_api(
    payload: TicketTypeCreate,
    event_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin')),
):
    """Create ticket"""
    ticket = await create_ticket_serv(payload, event_id, user, session)
    return ticket


@router.get('/{event_id}/ticket-types', response_model=list[TicketTypeResponse])
async def get_tickets_event_api(
    event_id: UUID,
    session: SessionDep,
):
    """Get tickets for event"""
    tickets = await get_events_active_ticket(event_id, session)
    return tickets


@router.patch('/{event_id}/ticket-types/{ticket_type_id}', response_model=TicketTypeResponse)
async def update_ticket_api(
    payload: TicketTypeUpdate,
    event_id: UUID,
    ticket_type_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Patch ticket"""
    ticket = await update_ticket_serv(payload, ticket_type_id, user, event_id, session)
    return ticket


@router.delete('/{event_id}/ticket-types/{ticket_type_id}/delete', status_code=204)
async def delete_ticket_api(
    event_id: UUID,
    ticket_type_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Delete ticket"""
    await delete_ticket_serv(ticket_type_id, event_id, user, session)
    return None


@router.get('/{event_id}/ticket-types/{ticket_type_id}', response_model=TicketTypeResponse)
async def get_ticket_by_id_api(
        event_id: UUID,
        ticket_type_id: UUID,
        session: SessionDep,
        user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Get ticket by id"""
    ticket = await get_ticket_type_id_serv(ticket_type_id, event_id, user, session)
    return ticket