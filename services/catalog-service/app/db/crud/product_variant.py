import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product_variant import ProductVariant


async def create_product_variant(
    session: AsyncSession,
    product_id: uuid.UUID,
    sku: str,
    attributes: dict,
    stock_quantity: int,
    price_override: Decimal | None = None,    
) -> ProductVariant:
    product_variant = ProductVariant(
        product_id=product_id,
        sku=sku,
        attributes=attributes,
        price_override=price_override,
        stock_quantity=stock_quantity
    )
    session.add(product_variant)

    await session.flush()
    return product_variant

async def get_product_variant_by_id(
    session: AsyncSession,
    product_variant_id: uuid.UUID,
) -> ProductVariant | None:
    stmt = (
        select(ProductVariant)
        .where(ProductVariant.id == product_variant_id)
    )
    return await session.scalar(stmt)

async def get_product_variant_by_sku(
    session: AsyncSession,
    product_variant_sku: str
) -> ProductVariant | None:
    stmt = (
        select(ProductVariant)
        .where(ProductVariant.sku == product_variant_sku)
    )
    return await session.scalar(stmt)

async def get_product_variants(
    session: AsyncSession,
    product_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20
) -> list[ProductVariant]:
    stmt = (
        select(ProductVariant)
        .where(ProductVariant.product_id == product_id)
        .order_by(ProductVariant.id)
        .offset(offset)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result.all())

async def update_product_variant(
    session: AsyncSession,
    product_variant: ProductVariant,
    **fields
) -> ProductVariant:
    for key, value in fields.items():
        setattr(product_variant, key, value)

    await session.flush()
    await session.refresh(product_variant)
    return product_variant

async def delete_product_variant(
    session: AsyncSession,
    product_variant: ProductVariant
) -> None:
    await session.delete(product_variant)
    await session.flush()

