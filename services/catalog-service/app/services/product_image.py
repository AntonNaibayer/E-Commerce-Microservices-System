import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.client import redis_client
from app.cache.product_image import ProductImageCache
from app.db.crud import product_image as product_image_crud
from app.db.models.product_image import ProductImage
from app.services import product as product_services
from app.services.exceptions import (
    NotFoundProductImageError,
    ProductImageCreationConflictError,
    ProductImageDeletionConflictError,
    ProductImageUpdateConflictError,
)

product_image_cache = ProductImageCache(redis_client)

async def create_product_image(
    session: AsyncSession,
    product_id: uuid.UUID,
    url: str,
    sort_order: int,
    alt_text: str | None = None,
) -> ProductImage:

    await product_services.get_product_or_raise(
        session=session,
        product_id=product_id,
    )

    try:
        product_image = await product_image_crud.create_product_image(
            session=session,
            product_id=product_id,
            url=url,
            sort_order=sort_order,
            alt_text=alt_text,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductImageCreationConflictError(
            product_id=product_id,
            url=url,
            sort_order=sort_order,
            alt_text=alt_text,
        )

    await product_image_cache.invalidate_list()

    return product_image

async def get_product_image_or_raise(
    session: AsyncSession,
    product_image_id: uuid.UUID,
) -> ProductImage:

    product_image = await product_image_crud.get_product_image_by_id(
        session=session,
        product_image_id=product_image_id,
    )
    if product_image is None:
        raise NotFoundProductImageError(product_image_id)

    return product_image

async def get_product_images(
    session: AsyncSession,
    product_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20,
) -> list[ProductImage]:

    cached = await product_image_cache.get_list(
        product_id=product_id,
        offset=offset,
        limit=limit,
    )
    if cached:
        return cached

    product_images = await product_image_crud.get_product_images(
        session=session,
        product_id=product_id,
        offset=offset,
        limit=limit,
    )

    await product_image_cache.set_list(
        product_images=product_images,
        product_id=product_id,
        offset=offset,
        limit=limit,
    )

    return product_images



async def update_product_image(
    session: AsyncSession,
    product_image_id: uuid.UUID,
    **fields,
) -> ProductImage:

    product_image = await get_product_image_or_raise(
        session=session,
        product_image_id=product_image_id,
    )

    try:
        updated_product_image = await product_image_crud.update_product_image(
            session=session,
            product_image=product_image,
            **fields,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductImageUpdateConflictError(product_image_id, **fields)

    await product_image_cache.invalidate_list()

    return updated_product_image

async def delete_product_image(
    session: AsyncSession,
    product_image_id: uuid.UUID,
) -> None:

    product_image = await get_product_image_or_raise(
        session=session,
        product_image_id=product_image_id,
    )

    try:
        await product_image_crud.delete_product_image(
            session=session,
            product_image=product_image,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductImageDeletionConflictError(product_image_id)

    await product_image_cache.invalidate_list()