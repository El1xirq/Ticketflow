from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, ForeignKey, String, CheckConstraint

from enum import Enum
from uuid import UUID

from app.db.session import Base

class UserRole(str, Enum):
    CUSTOMER = 'customer'
    ORGANIZER = 'organizer'
    ADMIN = 'admin'


class UserRoleORM(Base):
    __tablename__ = "user_roles"

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'organizer', 'admin')",
            name="ck_users_role",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        autoincrement=False,
    )
    role: Mapped[str] = mapped_column(String(20), primary_key=True, autoincrement=False)

    user: Mapped["UserORM"] = relationship(back_populates="roles")