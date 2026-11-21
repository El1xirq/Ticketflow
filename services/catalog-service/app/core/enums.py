from enum import Enum


class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"


class CurrencyCode(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"



class UserRole(str, Enum):
    CUSTOMER = 'customer'
    ORGANIZER = 'organizer'
    ADMIN = 'admin'