from pydantic import BaseModel, EmailStr, field_validator, Field, ConfigDict

from typing import Any
from uuid import UUID

from app.db.models.user_role import UserRole

class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

    @field_validator("password")
    @classmethod
    def validate_password_digits(cls, value: str) -> str:
        if not any(char.isdigit() for char in value):
            raise ValueError("The password must contain at least 1 digit.")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def validate_email_lower(cls, email: Any) -> Any:
        if isinstance(email, str):
            return email.lower()
        return email


class RegistrationData(BaseModel):
    email: EmailStr
    password_hash: str
    role: list[UserRole] = [UserRole.CUSTOMER]


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)