from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import EventStatus


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    venue_name: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=500)
    starts_at: datetime
    ends_at: datetime

    @field_validator("starts_at", "ends_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include a timezone")
        return value.astimezone(timezone.utc)

    @field_validator("starts_at")
    @classmethod
    def starts_at_must_be_future(cls, value: datetime) -> datetime:
        if value <= datetime.now(timezone.utc):
            raise ValueError("starts_at must be in the future")
        return value

    @model_validator(mode="after")
    def check_dates_order(self) -> "EventCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self
    
    model_config = ConfigDict(str_strip_whitespace=True)


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    venue_name: str | None = Field(default=None, min_length=1, max_length=200)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @field_validator("starts_at", "ends_at")
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

    @field_validator("starts_at")
    @classmethod
    def starts_at_must_be_future_if_present(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and value <= datetime.now(timezone.utc):
            raise ValueError("starts_at must be in the future")
        return value

    @model_validator(mode="after")
    def check_dates_order_if_both_present(self) -> "EventUpdate":
        if (
            self.starts_at is not None
            and self.ends_at is not None
            and self.ends_at <= self.starts_at
        ):
            raise ValueError("ends_at must be after starts_at")
        return self

    model_config = ConfigDict(str_strip_whitespace=True)


class EventResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    title: str
    description: str | None
    venue_name: str
    city: str
    address: str
    starts_at: datetime
    ends_at: datetime
    status: EventStatus
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)