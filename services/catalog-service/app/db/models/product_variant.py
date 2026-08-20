import decimal
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    sku: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True
    )

    attributes: Mapped[dict] = mapped_column(
        JSONB,
        default=dict
    )

    price_override: Mapped[decimal.Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    stock_quantity: Mapped[int] = mapped_column(
        default=0,
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
        CheckConstraint("price_override IS NULL OR price_override > 0", name="check_price_override_positive"),
        CheckConstraint("stock_quantity >= 0", name="check_stock_quantity_positive"),
    )

