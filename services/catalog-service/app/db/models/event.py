from sqlalchemy import (
    CheckConstraint,
    DateTime,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from uuid import UUID, uuid4

from app.core.enums import EventStatus
from app.db.session import Base


class EventORM(Base):
    __tablename__ = "events"

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'cancelled')",
            name="ck_events_status",
        ),
        CheckConstraint(
            "starts_at < ends_at",
            name="ck_events_starts_before_ends",
        ),
        CheckConstraint(
            "published_at IS NULL OR published_at >= created_at",
            name="ck_events_published_after_created",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    
    organizer_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    venue_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=EventStatus.DRAFT.value,
        server_default=text("'draft'"),
        index=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    ticket_types: Mapped[list["TicketTypeORM"]] = relationship(
        "TicketTypeORM",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy='selectin',
    )