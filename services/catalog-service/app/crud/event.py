from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError

from uuid import UUID
from datetime import datetime, timezone

from app.core.exceptions.domain import (
    DatabaseException, 
    NotFoundException, 
    PermissionDeniedException, 
    ConflictException
)
from app.schemas.event import EventCreate, EventUpdate
from app.db import SessionDep, EventORM
from app.core.enums import EventStatus

async def create_event(
        payload: EventCreate, 
        organizer_id: UUID, 
        session: SessionDep
) -> EventORM:
    """Create event for payload"""
    event = EventORM(**payload.model_dump(), organizer_id=organizer_id)

    try:
        session.add(event)
        await session.commit()
        await session.refresh(event)
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()

    return event

async def get_event_by_id(
        event_id: UUID,
        session: SessionDep
) -> EventORM:
    """Get event by id"""
    stmt = select(EventORM).where(EventORM.id == event_id)

    try:
        event = (await session.execute(stmt)).scalar_one_or_none()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    
    if event is None:
        raise NotFoundException('Event not found')
    return event


async def get_list_published_events(session: SessionDep) -> list[EventORM]:
    """Get published events, list"""
    stmt = (
        select(EventORM)
        .where(EventORM.status == EventStatus.PUBLISHED.value)
        .order_by(EventORM.starts_at.asc())
        )
    
    try:
        events = (await session.execute(stmt)).scalars().all()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    
    return list(events)


async def update_event(
        payload: EventUpdate,
        event_id: UUID,
        session: SessionDep
) -> EventORM:
    """Patch event"""
    update_options = payload.model_dump(exclude_none=True)
    if not update_options:
        return None

    if payload.ends_at is not None:
        if payload.ends_at < datetime.now(timezone.utc):
            raise ConflictException("The event end date cannot be in the past")

    stmt = update(EventORM).where(EventORM.id == event_id).values(**update_options).returning(EventORM)
    try:
        event = (await session.execute(stmt)).scalar_one()
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    
    return event


async def publish_event(
        event_id: UUID,
        session: SessionDep,
) -> EventORM:
    """Publish event"""
    stmt = (
        update(EventORM)
        .where(EventORM.id==event_id)
        .values(published_at = datetime.now(timezone.utc), status = EventStatus.PUBLISHED.value)
        .returning(EventORM)
        )
    
    try:
        event = (await session.execute(stmt)).scalar_one()
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    return event


async def cancel_event(
        event_id: UUID,
        session: SessionDep,
) -> EventORM:
    """Cancel event"""
    stmt = (
        update(EventORM)
        .where(EventORM.id == event_id)
        .values(status = EventStatus.CANCELLED.value)
        .returning(EventORM)
        )
    try:
        event = (await session.execute(stmt)).scalar_one()
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()
    return event