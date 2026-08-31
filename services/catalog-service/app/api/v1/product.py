import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from shared.auth.dependencies import AdminUser

from app.api.exceptions import (
    duplicate_product_sku_error,
    duplicate_product_slug_error,
    not_found_brand_error,
    not_found_category_error,
    not_found_product_error,
    product_creation_conflict_error,
    product_deletion_conflict_error,
    product_update_conflict_error,
)
from app.db.session import SessionDep
from app.schemas.pagination_param import PaginationParams
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services import product as product_services
from app.services.exceptions import (
    DuplicateProductSkuError,
    DuplicateProductSlugError,
    NotFoundBrandError,
    NotFoundCategoryError,
    NotFoundProductError,
    ProductCreationConflictError,
    ProductDeletionConflictError,
    ProductUpdateConflictError,
)

router = APIRouter(
    prefix="/product",
    tags=["Product"],
)


@router.post("/", response_model=ProductResponse)
async def create_product(
    session: SessionDep,
    admin: AdminUser,
    data: ProductCreate,
) -> ProductResponse:
    try:
        product = await product_services.create_product(
            session=session,
            name=data.name,
            sku=data.sku,
            description=data.description,
            base_price=data.base_price,
            currency=data.currency,
            category_id=data.category_id,
            brand_id=data.brand_id,
            attributes=data.attributes,
            is_active=data.is_active,
        )
    except DuplicateProductSkuError:
        raise duplicate_product_sku_error
    except DuplicateProductSlugError:
        raise duplicate_product_slug_error
    except NotFoundCategoryError:
        raise not_found_category_error
    except NotFoundBrandError:
        raise not_found_brand_error
    except ProductCreationConflictError:
        raise product_creation_conflict_error

    return ProductResponse.model_validate(product)

@router.get("/", response_model=list[ProductResponse])
async def get_products(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    category_id: uuid.UUID | None = None,
    brand_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> list[ProductResponse]:
    products = await product_services.get_products(
        session=session,
        category_id=category_id,
        brand_id=brand_id,
        is_active=is_active,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return [ProductResponse.model_validate(product) for product in products]

@router.get("/sku/{product_sku}", response_model=ProductResponse)
async def get_product_by_sku(
    session: SessionDep,
    product_sku: str,
) -> ProductResponse:
    try:
        product = await product_services.get_product_by_sku_or_raise(
            session=session,
            product_sku=product_sku,
        )
    except NotFoundProductError:
        raise not_found_product_error

    return ProductResponse.model_validate(product)

@router.get("/slug/{product_slug}", response_model=ProductResponse)
async def get_product_by_slug(
    session: SessionDep,
    product_slug: str,
) -> ProductResponse:
    try:
        product = await product_services.get_product_by_slug_or_raise(
            session=session,
            product_slug=product_slug,
        )
    except NotFoundProductError:
        raise not_found_product_error

    return ProductResponse.model_validate(product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    session: SessionDep,
    product_id: uuid.UUID,
) -> ProductResponse:
    try:
        product = await product_services.get_product_or_raise(
            session=session,
            product_id=product_id,
        )
    except NotFoundProductError:
        raise not_found_product_error

    return ProductResponse.model_validate(product)

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    session: SessionDep,
    admin: AdminUser,
    product_id: uuid.UUID,
    data: ProductUpdate,
) -> ProductResponse:
    try:
        updated_product = await product_services.update_product(
            session=session,
            product_id=product_id,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundProductError:
        raise not_found_product_error
    except NotFoundCategoryError:
        raise not_found_category_error
    except NotFoundBrandError:
        raise not_found_brand_error
    except ProductUpdateConflictError:
        raise product_update_conflict_error

    return ProductResponse.model_validate(updated_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    session: SessionDep,
    admin: AdminUser,
    product_id: uuid.UUID,
) -> None:
    try:
        await product_services.delete_product(
            session=session,
            product_id=product_id,
        )
    except NotFoundProductError:
        raise not_found_product_error
    except ProductDeletionConflictError:
        raise product_deletion_conflict_error