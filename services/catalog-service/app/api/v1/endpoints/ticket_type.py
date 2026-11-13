from fastapi import APIRouter, Depends

from uuid import UUID

from app.db import SessionDep
from app.crud.ticket_type import get_events_ticket
from app.schemas.ticket_type import TicketTypeResponse, TicketTypeCreate, TicketTypeUpdate
from app.api.deps import CurrentActor, require_role
from app.services.ticket_type import create_ticket_serv, update_ticket_serv


router = APIRouter(prefix='/events', tags=['TicketType'])


@router.post('/{event_id}/ticket-types', response_model=TicketTypeResponse, status_code=201)
async def create_ticket_type_api(
    payload: TicketTypeCreate,
    event_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin')),
):
    """Create ticket"""
    ticket = await create_ticket_serv(payload, event_id, user.user_id, session)
    return ticket


@router.get('/{event_id}/ticket-types', response_model=list[TicketTypeResponse])
async def get_tickets_event_api(
    event_id: UUID,
    session: SessionDep,
):
    """Get tickets for event"""
    tickets = await get_events_ticket(event_id, session)
    return tickets


@router.post('/{event_id}/ticket-types/{ticket_type_id}', response_model=TicketTypeResponse)
async def update_ticket(
    payload: TicketTypeUpdate,
    event_id: UUID,
    ticket_type_id: UUID,
    session: SessionDep,
    user: CurrentActor = Depends(require_role('organizer', 'admin'))
):
    """Patch ticket"""
    ticket = await update_ticket_serv(payload, ticket_type_id, user.user_id, event_id, session)
    return ticket