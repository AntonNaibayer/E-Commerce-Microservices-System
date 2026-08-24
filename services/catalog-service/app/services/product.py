import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import product as product_crud
from app.db.models.product import Product
from app.enums.currency import Currency
from app.services.brand import get_brand_or_raise
from app.services.category import get_category_or_raise
from app.services.exceptions import (
    DuplicateProductSkuError,
    DuplicateProductSlugError,
    NotFoundProductError,
    ProductCreationConflictError,
    ProductDeletionConflictError,
    ProductUpdateConflictError,
)
from app.utils.slugify import generate_slug


async def create_product(
    session: AsyncSession,
    name: str,
    sku: str,
    description: str,
    base_price: Decimal,
    currency: Currency,
    category_id: uuid.UUID,
    attributes: dict,
    brand_id: uuid.UUID | None = None,
    is_active: bool = True,
) -> Product:

    existing = await product_crud.get_product_by_sku(
        session=session,
        product_sku=sku,
    )
    if existing is not None:
        raise DuplicateProductSkuError(sku)

    product_slug = generate_slug(name)
    existing = await product_crud.get_product_by_slug(
        session=session,
        product_slug=product_slug,
    )
    if existing is not None:
        raise DuplicateProductSlugError(product_slug)

    await get_category_or_raise(
        session=session,
        category_id=category_id,
    )

    if brand_id is not None:
        await get_brand_or_raise(
            session=session,
            brand_id=brand_id,
        )

    try:
        product = await product_crud.create_product(
            session=session,
            name=name,
            sku=sku,
            slug=product_slug,
            description=description,
            base_price=base_price,
            currency=currency,
            category_id=category_id,
            attributes=attributes,
            brand_id=brand_id,
            is_active=is_active,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductCreationConflictError(
            product_name=name,
            slug=product_slug,
            sku=sku,
        )

    return product

async def get_product_or_raise(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> Product:

    product = await product_crud.get_product_by_id(
        session=session,
        product_id=product_id,
    )
    if product is None:
        raise NotFoundProductError(product_id)

    return product

async def get_product_by_sku_or_raise(
    session: AsyncSession,
    product_sku: str,
) -> Product:

    product = await product_crud.get_product_by_sku(
        session=session,
        product_sku=product_sku,
    )
    if product is None:
        raise NotFoundProductError(product_sku)

    return product

async def get_product_by_slug_or_raise(
    session: AsyncSession,
    product_slug: str,
) -> Product:

    product = await product_crud.get_product_by_slug(
        session=session,
        product_slug=product_slug,
    )
    if product is None:
        raise NotFoundProductError(product_slug)

    return product

async def get_products(
    session: AsyncSession,
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    offset: int = 0,
    limit: int = 20,
) -> list[Product]:

    # не делаю проверку на существование категории и бренда, потому что это лишние
    # запросы к бд, так как даже если они не существуют, получим пустой список
    # товаров, что соответствует бизнес-логике
    return await product_crud.get_products(
        session=session,
        category_id=category_id,
        brand_id=brand_id,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )

async def update_product(
    session: AsyncSession,
    product_id: uuid.UUID,
    **fields,
) -> Product:

    product = await get_product_or_raise(
        session=session,
        product_id=product_id,
    )

    if "category_id" in fields and fields["category_id"] is not None:
        await get_category_or_raise(session=session, category_id=fields["category_id"])

    if "brand_id" in fields and fields["brand_id"] is not None:
        await get_brand_or_raise(session=session, brand_id=fields["brand_id"])

    try:
        product = await product_crud.update_product(
            session=session,
            product=product,
            **fields,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductUpdateConflictError(
            product_id=product_id,
            **fields,
        )

    return product

async def delete_product(
    session: AsyncSession,
    product_id: uuid.UUID,
) -> None:

    product = await get_product_or_raise(
        session=session,
        product_id=product_id,
    )

    try:
        await product_crud.delete_product(
            session=session,
            product=product,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductDeletionConflictError(product_id)