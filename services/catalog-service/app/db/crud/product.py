import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product import Product
from app.enums.currency import Currency


async def create_product(
    session: AsyncSession,
    name: str,
    sku: str,
    slug: str,
    description: str,
    base_price: Decimal,
    currency: Currency,
    category_id: uuid.UUID,
    attributes: dict,
    brand_id: uuid.UUID | None = None,
    is_active: bool = True
) -> Product:
    product = Product(
        name=name,
        sku=sku,
        slug=slug,
        description=description,
        base_price=base_price,
        currency=currency,
        category_id=category_id,
        brand_id=brand_id,
        attributes=attributes,
        is_active=is_active
    )
    session.add(product)
    await session.flush()
    return product

async def get_product_by_id(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.id == product_id)
    )
    return await session.scalar(stmt)

async def get_product_by_slug(
    session: AsyncSession,
    product_slug: str
) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.slug == product_slug)
    )

    return await session.scalar(stmt)

async def get_product_by_sku(
    session: AsyncSession,
    product_sku: str
) -> Product | None:
    stmt = (
        select(Product)
        .where(Product.sku == product_sku)
    )

    return await session.scalar(stmt)

async def get_products(
    session: AsyncSession,
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    offset: int = 0,
    limit: int = 20
) -> list[Product]:

    stmt = select(Product)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    if brand_id is not None:
        stmt = stmt.where(Product.brand_id == brand_id)

    if is_active is not None:
        stmt = stmt.where(Product.is_active == is_active)

    stmt = (
        stmt
        .order_by(Product.id)
        .offset(offset)
        .limit(limit)
    )  

    result = await session.scalars(stmt)
    return list(result.all())

async def update_product(
    session: AsyncSession,
    product: Product,
    **fields
) -> Product:

    for key, value in fields.items():
        setattr(product, key, value)

    await session.flush()
    await session.refresh(product)
    return product

async def delete_product(
    session: AsyncSession,
    product: Product
) -> None:
    await session.delete(product)
    await session.flush()
