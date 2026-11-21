from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, select, delete

from datetime import datetime, timezone
from uuid import UUID

from app.db import SessionDep, TicketTypeORM
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate
from app.crud.event import get_event_by_id
from app.core.exceptions.domain import DatabaseException, ConflictException, NotFoundException

async def get_ticket_type_by_id(
        ticket_type_id: UUID,
        session: SessionDep,
) -> TicketTypeORM:
    """Get ticket by id"""
    stmt = select(TicketTypeORM).where(TicketTypeORM.id == ticket_type_id)
    try:
        ticket = (await session.execute(stmt)).scalar_one_or_none()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()

    if ticket is None:
        raise NotFoundException()
    return ticket


async def get_events_ticket(
        event_id: UUID,
        session: SessionDep,
) -> list[TicketTypeORM]:
    """Get event tickets"""
    event = await get_event_by_id(event_id, session)
    return list(event.ticket_types)


async def get_events_active_ticket(
        event_id: UUID,
        session: SessionDep,
) -> list[TicketTypeORM]:
    """Get event active tickets"""
    stmt = select(TicketTypeORM).where(TicketTypeORM.event_id == event_id, TicketTypeORM.is_active.is_(True))
    tickets = (await session.execute(stmt)).scalars().all()
    return list(tickets)


async def create_ticket_type(
        payload: TicketTypeCreate,
        event_id: UUID,
        session: SessionDep,
) -> TicketTypeORM:
    """Create ticket"""
    ticket = TicketTypeORM(**payload.model_dump(), event_id=event_id)

    try:
        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()

    return ticket


async def update_ticket_type(
        payload: TicketTypeUpdate,
        ticket_type_id: UUID, 
        session: SessionDep,
) -> TicketTypeORM:
    """Patch ticket"""
    update_options = payload.model_dump(exclude_none=True)

    if not update_options:
        return await get_ticket_type_by_id(ticket_type_id, session)

    if payload.sales_end_at is not None:
            if payload.ends_at < datetime.now(timezone.utc):
                raise ConflictException("The event end date cannot be in the past")
            
    stmt = (
        update(TicketTypeORM)
        .where(TicketTypeORM.id == ticket_type_id)
        .values(**update_options)
        .returning(TicketTypeORM)
    )
    try:
        ticket = (await session.execute(stmt)).scalar_one()
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    return ticket


async def delete_ticket_type(
        ticket_type_id: UUID,
        session: SessionDep,
):
    """Delete ticket type"""
    stmt = delete(TicketTypeORM).where(TicketTypeORM.id == ticket_type_id)
    try:
        await session.execute(stmt)
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    return None