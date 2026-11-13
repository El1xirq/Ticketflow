from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime
from uuid import UUID, uuid4

from app.core.enums import CurrencyCode
from app.db.session import Base

_CURRENCY_VALUES_SQL = ", ".join(
    f"'{currency.value}'" for currency in CurrencyCode
)


class TicketTypeORM(Base):
    __tablename__ = "ticket_types"

    __table_args__ = (
        CheckConstraint(
            "price_minor >= 0",
            name="ck_ticket_types_price_non_negative",
        ),
        CheckConstraint(
            "total_quantity > 0",
            name="ck_ticket_types_quantity_positive",
        ),
        CheckConstraint(
            "sales_start_at IS NULL "
            "OR sales_end_at IS NULL "
            "OR sales_start_at < sales_end_at",
            name="ck_ticket_types_sales_window_valid",
        ),
        CheckConstraint(
            f"currency IN ({_CURRENCY_VALUES_SQL})",
            name="ck_ticket_types_currency",
        ),
        UniqueConstraint(
            "event_id",
            "name",
            name="uq_ticket_types_event_name",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    event_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    price_minor: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    total_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    sales_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    sales_end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    event: Mapped["EventORM"] = relationship(
        "EventORM",
        back_populates="ticket_types",
    )