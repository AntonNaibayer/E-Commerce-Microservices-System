import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product_image import ProductImage


async def create_product_image(
    session: AsyncSession,
    product_id: uuid.UUID,
    url: str,
    sort_order: int,
    alt_text: str | None = None,
) -> ProductImage:
    product_image = ProductImage(
        product_id=product_id,
        url=url,
        alt_text=alt_text,
        sort_order=sort_order
    )
    session.add(product_image)

    await session.flush()
    return product_image

async def get_product_image_by_id(
    session: AsyncSession,
    product_image_id: uuid.UUID,
) -> ProductImage | None:
    stmt = (
        select(ProductImage)
        .where(ProductImage.id == product_image_id)
    )
    return await session.scalar(stmt)

async def get_product_images(
    session: AsyncSession,
    product_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20
) -> list[ProductImage]:
    stmt = (
        select(ProductImage)
        .where(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
        .offset(offset)
        .limit(limit)
    )
    result = await session.scalars(stmt)
    return list(result.all())

async def update_product_image(
    session: AsyncSession,
    product_image: ProductImage,
    **fields
) -> ProductImage:
    for key, value in fields.items():
        setattr(product_image, key, value)

    await session.flush()
    await session.refresh(product_image)
    return product_image

async def delete_product_image(
    session: AsyncSession,
    product_image: ProductImage
) -> None:
    await session.delete(product_image)
    await session.flush()

