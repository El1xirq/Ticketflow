from pydantic import BaseModel, ConfigDict, EmailStr, Field

from uuid import UUID

from app.db.models import UserRole

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: list[UserRole]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
