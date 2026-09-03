import decimal
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.currency import Currency


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    sku: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
    )

    slug: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True
    )

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )

    base_price: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    currency: Mapped[Currency] = mapped_column(
        default=Currency.RUB
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("brands.id", ondelete="SET NULL"),
        index=True
    )

    attributes: Mapped[dict] = mapped_column(
        JSONB,
        default=dict
    )

    is_active: Mapped[bool] = mapped_column(
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("base_price > 0", name="check_base_price_positive"),
        Index("ix_products_category_active", "category_id", "is_active"),
    )