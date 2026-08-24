import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import brand as brand_crud
from app.db.models.brand import Brand
from app.services.exceptions import (
    BrandCreationConflictError,
    BrandDeletionConflictError,
    BrandUpdateConflictError,
    DuplicateBrandSlugError,
    NotFoundBrandError,
)
from app.utils.slugify import generate_slug

_UNSET = object()

async def create_brand(
    session: AsyncSession,
    brand_name: str,
) -> Brand:

    brand_slug = generate_slug(brand_name)

    existing = await brand_crud.get_brand_by_slug(
        session=session,
        slug=brand_slug,
    )
    if existing is not None:
        raise DuplicateBrandSlugError(brand_slug)

    try:
        brand = await brand_crud.create_brand(
            session=session,
            name=brand_name,
            slug=brand_slug,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BrandCreationConflictError(name=brand_name, slug=brand_slug)

    return brand

async def get_brand_or_raise(
    session: AsyncSession,
    brand_id: uuid.UUID,
) -> Brand:

    brand = await brand_crud.get_brand_by_id(
        session=session,
        brand_id=brand_id,
    )
    if brand is None:
        raise NotFoundBrandError(brand_id)

    return brand

async def get_brand_by_slug_or_raise(
    session: AsyncSession,
    brand_slug: str,
) -> Brand:

    brand = await brand_crud.get_brand_by_slug(
        session=session,
        slug=brand_slug,
    )
    if brand is None:
        raise NotFoundBrandError(brand_slug)

    return brand

async def get_brands(
    session: AsyncSession,
    offset: int = 0,
    limit: int = 20,
) -> list[Brand]:

    return await brand_crud.get_brands(
        session=session,
        offset=offset,
        limit=limit,
    )

async def update_brand(
    session: AsyncSession,
    brand_id: uuid.UUID,
    **fields,
) -> Brand:

    brand = await get_brand_or_raise(
        session=session,
        brand_id=brand_id,
    )

    brand_name = fields.get("name", _UNSET)

    if brand_name is not _UNSET and brand_name is not None:
        new_slug = generate_slug(brand_name)

        existing = await brand_crud.get_brand_by_slug(
            session=session,
            slug=new_slug,
        )
        if existing is not None and existing.id != brand_id:
            raise DuplicateBrandSlugError(new_slug)

        fields["slug"] = new_slug

    try:
        updated_brand = await brand_crud.update_brand(
            session=session,
            brand=brand,
            **fields,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BrandUpdateConflictError(brand_id, **fields)

    return updated_brand

async def delete_brand(
    session: AsyncSession,
    brand_id: uuid.UUID,
) -> None:

    brand = await get_brand_or_raise(
        session=session,
        brand_id=brand_id,
    )

    try:
        await brand_crud.delete_brand(
            session=session,
            brand=brand,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise BrandDeletionConflictError(brand_id)