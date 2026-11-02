from pydantic import BaseModel, ConfigDict, EmailStr, Field

from uuid import UUID

from app.db.models import UserRole

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: list[UserRole]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UpdateUserSchema(BaseModel):
    email: EmailStr | None = Field(default=None)
    password_hash: str | None = Field(default=None)
    roles: list[UserRole] | None = Field(default=None)