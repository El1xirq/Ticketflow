from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from uuid import UUID
from datetime import datetime, timezone

from app.core.enums import CurrencyCode

class TicketTypeResponse(BaseModel):
    id: UUID
    event_id: UUID
    name: str
    description: str | None
    price_minor: int
    currency: CurrencyCode
    total_quantity: int
    sales_start_at: datetime | None
    sales_end_at: datetime | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    price_minor: int
    currency: CurrencyCode
    total_quantity: int
    sales_start_at: datetime | None = None
    sales_end_at: datetime | None = None
    is_active: bool = True

    @field_validator("sales_start_at", "sales_end_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include a timezone")
        return value.astimezone(timezone.utc)

    @field_validator("sales_start_at")
    @classmethod
    def starts_at_must_be_future(cls, value: datetime) -> datetime:
        if value <= datetime.now(timezone.utc):
            raise ValueError("sales_start_at must be in the future")
        return value

    model_config = ConfigDict(str_strip_whitespace=True)


class TicketTypeUpdate(BaseModel):
    name: str | None = Field(min_length=1, max_length=100, default=None)
    description: str | None = None
    price_minor: int | None = None
    currency: CurrencyCode | None = None
    total_quantity: int | None = None
    sales_start_at: datetime | None = None
    sales_end_at: datetime | None = None
    is_active: bool | None = None

    @field_validator("sales_start_at", "sales_end_at")
    @classmethod
    def require_timezone_if_present(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is None:
            return value

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include a timezone")

        return value.astimezone(timezone.utc)

    @field_validator("sales_start_at")
    @classmethod
    def starts_at_must_be_future_if_present(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and value <= datetime.now(timezone.utc):
            raise ValueError("sales_start_at must be in the future")
        return value

    @model_validator(mode="after")
    def check_dates_order_if_both_present(self) -> "TicketTypeUpdate":
        if (
            self.sales_start_at is not None
            and self.sales_end_at is not None
            and self.sales_end_at <= self.sales_start_at
        ):
            raise ValueError("sales_end_at must be after sales_start_at")
        return self

    model_config = ConfigDict(str_strip_whitespace=True)