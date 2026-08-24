import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import product_variant as product_variant_crud
from app.db.models.product_variant import ProductVariant
from app.services import product as product_services
from app.services.exceptions import (
    DuplicateProductVariantSkuError,
    NotFoundProductVariantError,
    ProductVariantCreationConflictError,
    ProductVariantDeletionConflictError,
    ProductVariantUpdateConflictError,
)


async def create_product_variant(
    session: AsyncSession,
    product_id: uuid.UUID,
    sku: str,
    attributes: dict,
    stock_quantity: int,
    price_override: Decimal | None = None,
) -> ProductVariant:

    await product_services.get_product_or_raise(
        session=session,
        product_id=product_id,
    )

    existing = await product_variant_crud.get_product_variant_by_sku(
        session=session,
        product_variant_sku=sku,
    )
    if existing is not None:
        raise DuplicateProductVariantSkuError(sku)

    try:
        product_variant = await product_variant_crud.create_product_variant(
            session=session,
            product_id=product_id,
            sku=sku,
            attributes=attributes,
            stock_quantity=stock_quantity,
            price_override=price_override,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductVariantCreationConflictError(
            product_id=product_id,
            sku=sku,
            attributes=attributes,
            stock_quantity=stock_quantity,
            price_override=price_override,
        )

    return product_variant

async def get_product_variant_or_raise(
    session: AsyncSession,
    product_variant_id: uuid.UUID,
) -> ProductVariant:

    product_variant = await product_variant_crud.get_product_variant_by_id(
        session=session,
        product_variant_id=product_variant_id,
    )
    if product_variant is None:
        raise NotFoundProductVariantError(product_variant_id)

    return product_variant

async def get_product_variant_by_sku_or_raise(
    session: AsyncSession,
    product_variant_sku: str,
) -> ProductVariant:

    product_variant = await product_variant_crud.get_product_variant_by_sku(
        session=session,
        product_variant_sku=product_variant_sku,
    )
    if product_variant is None:
        raise NotFoundProductVariantError(product_variant_sku)

    return product_variant

async def get_product_variants(
    session: AsyncSession,
    product_id: uuid.UUID,
    offset: int = 0,
    limit: int = 20,
) -> list[ProductVariant]:

    return await product_variant_crud.get_product_variants(
        session=session,
        product_id=product_id,
        offset=offset,
        limit=limit,
    )

async def update_product_variant(
    session: AsyncSession,
    product_variant_id: uuid.UUID,
    **fields,
) -> ProductVariant:

    product_variant = await get_product_variant_or_raise(
        session=session,
        product_variant_id=product_variant_id,
    )

    if "product_id" in fields and fields["product_id"] is not None:
        await product_services.get_product_or_raise(
            session=session,
            product_id=fields["product_id"],
        )

    try:
        updated_product_variant = await product_variant_crud.update_product_variant(
            session=session,
            product_variant=product_variant,
            **fields,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductVariantUpdateConflictError(product_variant_id, **fields)

    return updated_product_variant

async def delete_product_variant(
    session: AsyncSession,
    product_variant_id: uuid.UUID,
) -> None:

    product_variant = await get_product_variant_or_raise(
        session=session,
        product_variant_id=product_variant_id,
    )

    try:
        await product_variant_crud.delete_product_variant(
            session=session,
            product_variant=product_variant,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise ProductVariantDeletionConflictError(product_variant_id)