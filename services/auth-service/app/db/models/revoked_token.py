import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, MappedColumn

from app.db.base import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[uuid.UUID] = MappedColumn(
        primary_key=True, 
        default=uuid.uuid4,
    )

    jti: Mapped[str] = MappedColumn(
        unique=True,
        index=True
    )

    expires_at: Mapped[datetime] = MappedColumn(
        DateTime(timezone=True), 
        nullable=False
    )