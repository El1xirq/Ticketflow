from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class TicketStatus(str, Enum):
    FREE = "free"
    HELD = "held"
    SOLD = "sold"


class TicketInventory(Base):
    __tablename__ = "ticket_inventory"

    __table_args__ = (
        UniqueConstraint("event_id", "seat_id", name="uq_ticket_inventory_event_seat"),
        CheckConstraint(
            "status IN ('free', 'held', 'sold')",
            name="ck_ticket_inventory_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        primary_key=True, 
        default=uuid4
        )

    event_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        nullable=False, 
        index=True
        )
    
    seat_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        nullable=False
        )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TicketStatus.FREE.value,
        server_default=TicketStatus.FREE.value,
    )

    hold_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        index=True
    )
    
    booking_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("bookings.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )