import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.brand import Brand


async def create_brand(
    session: AsyncSession,
    name: str,
    slug: str,
) -> Brand:
    new_brand = Brand(
        name=name,
        slug=slug
    )
    session.add(new_brand)
    await session.flush()

    return new_brand

async def get_brand_by_id(
    session: AsyncSession,
    brand_id: uuid.UUID,
) -> Brand | None:
    stmt = (
        select(Brand)
        .where(Brand.id == brand_id)
    )
    return await session.scalar(stmt)

async def get_brand_by_slug(
    session: AsyncSession,
    slug: str
) -> Brand | None:
    stmt = (
        select(Brand)
        .where(Brand.slug == slug)
    )
    return await session.scalar(stmt)

async def get_brands(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 20
) -> list[Brand]:
    stmt = (
        select(Brand)
        .order_by(Brand.name)
        .offset(offset)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result.all())

async def update_brand(
    session: AsyncSession,
    brand: Brand,
    name: str,
    slug: str,
) -> Brand:
    brand.name = name
    brand.slug = slug 

    await session.flush()
    await session.refresh(brand)
    return brand

async def delete_brand(
    session: AsyncSession,
    brand: Brand
) -> None:
    await session.delete(brand)