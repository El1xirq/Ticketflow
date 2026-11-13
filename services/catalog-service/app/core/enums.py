from enum import Enum


class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class CurrencyCode(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"