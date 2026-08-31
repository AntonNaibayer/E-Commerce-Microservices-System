import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from shared.auth.dependencies import AdminUser

from app.api.exceptions import (
    duplicate_product_variant_sku_error,
    not_found_product_error,
    not_found_product_variant_error,
    product_variant_creation_conflict_error,
    product_variant_deletion_conflict_error,
    product_variant_update_conflict_error,
)
from app.db.session import SessionDep
from app.schemas.pagination_param import PaginationParams
from app.schemas.product_variant import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services import product_variant as product_variant_services
from app.services.exceptions import (
    DuplicateProductVariantSkuError,
    NotFoundProductError,
    NotFoundProductVariantError,
    ProductVariantCreationConflictError,
    ProductVariantDeletionConflictError,
    ProductVariantUpdateConflictError,
)

router = APIRouter(
    prefix="/product-variant",
    tags=["Product variant"],
)


@router.post("/", response_model=ProductVariantResponse)
async def create_product_variant(
    session: SessionDep,
    admin: AdminUser,
    data: ProductVariantCreate,
) -> ProductVariantResponse:
    try:
        product_variant = await product_variant_services.create_product_variant(
            session=session,
            product_id=data.product_id,
            sku=data.sku,
            attributes=data.attributes,
            stock_quantity=data.stock_quantity,
            price_override=data.price_override,
        )
    except NotFoundProductError:
        raise not_found_product_error
    except DuplicateProductVariantSkuError:
        raise duplicate_product_variant_sku_error
    except ProductVariantCreationConflictError:
        raise product_variant_creation_conflict_error

    return ProductVariantResponse.model_validate(product_variant)

@router.get("/", response_model=list[ProductVariantResponse])
async def get_product_variants(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    product_id: uuid.UUID,
) -> list[ProductVariantResponse]:
    product_variants = await product_variant_services.get_product_variants(
        session=session,
        product_id=product_id,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return [ProductVariantResponse.model_validate(product_variant) for product_variant in product_variants]

@router.get("/sku/{product_variant_sku}", response_model=ProductVariantResponse)
async def get_product_variant_by_sku(
    session: SessionDep,
    product_variant_sku: str,
) -> ProductVariantResponse:
    try:
        product_variant = await product_variant_services.get_product_variant_by_sku_or_raise(
            session=session,
            product_variant_sku=product_variant_sku,
        )
    except NotFoundProductVariantError:
        raise not_found_product_variant_error

    return ProductVariantResponse.model_validate(product_variant)

@router.get("/{product_variant_id}", response_model=ProductVariantResponse)
async def get_product_variant_by_id(
    session: SessionDep,
    product_variant_id: uuid.UUID,
) -> ProductVariantResponse:
    try:
        product_variant = await product_variant_services.get_product_variant_or_raise(
            session=session,
            product_variant_id=product_variant_id,
        )
    except NotFoundProductVariantError:
        raise not_found_product_variant_error

    return ProductVariantResponse.model_validate(product_variant)

@router.patch("/{product_variant_id}", response_model=ProductVariantResponse)
async def update_product_variant(
    session: SessionDep,
    admin: AdminUser,
    product_variant_id: uuid.UUID,
    data: ProductVariantUpdate,
) -> ProductVariantResponse:
    try:
        updated_product_variant = await product_variant_services.update_product_variant(
            session=session,
            product_variant_id=product_variant_id,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundProductVariantError:
        raise not_found_product_variant_error
    except NotFoundProductError:
        raise not_found_product_error
    except ProductVariantUpdateConflictError:
        raise product_variant_update_conflict_error

    return ProductVariantResponse.model_validate(updated_product_variant)

@router.delete("/{product_variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_variant(
    session: SessionDep,
    admin: AdminUser,
    product_variant_id: uuid.UUID,
) -> None:
    try:
        await product_variant_services.delete_product_variant(
            session=session,
            product_variant_id=product_variant_id,
        )
    except NotFoundProductVariantError:
        raise not_found_product_variant_error
    except ProductVariantDeletionConflictError:
        raise product_variant_deletion_conflict_error