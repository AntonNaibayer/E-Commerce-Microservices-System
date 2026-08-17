import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, func, sql
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.user import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        unique=True,
        index=True
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), 
        default=UserRole.USER, 
        nullable=False
    )

    hashed_password: Mapped[bytes] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
        server_default=sql.true()
    )