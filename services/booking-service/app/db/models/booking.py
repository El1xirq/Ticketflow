from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BookingORM(Base):
    __tablename__ = "bookings"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_payment', 'confirmed', 'cancelled', 'expired')",
            name="ck_bookings_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        primary_key=True, 
        default=uuid4
        )
    
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), 
        nullable=False, 
        index=True
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
        String(30),
        nullable=False,
        default=BookingStatus.PENDING_PAYMENT.value,
        server_default=BookingStatus.PENDING_PAYMENT.value,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )