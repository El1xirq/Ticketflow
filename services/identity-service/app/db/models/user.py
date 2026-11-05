from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, String, func, DateTime

from datetime import datetime
from uuid import UUID, uuid4

from app.db.session import Base

class UserORM(Base):
    __tablename__='users'

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    roles: Mapped[list["UserRoleORM"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy='selectin',
    )

    refresh_tokens: Mapped[list["RefreshTokenORM"]] = relationship(
        "RefreshTokenORM",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )