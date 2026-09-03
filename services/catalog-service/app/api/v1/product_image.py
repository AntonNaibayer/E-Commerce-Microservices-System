import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from shared.auth.dependencies import AdminUser

from app.api.exceptions import (
    not_found_product_error,
    not_found_product_image_error,
    product_image_creation_conflict_error,
    product_image_deletion_conflict_error,
    product_image_update_conflict_error,
)
from app.db.session import SessionDep
from app.schemas.pagination_param import PaginationParams
from app.schemas.product_image import (
    ProductImageCreate,
    ProductImageResponse,
    ProductImageUpdate,
)
from app.services import product_image as product_image_services
from app.services.exceptions import (
    NotFoundProductError,
    NotFoundProductImageError,
    ProductImageCreationConflictError,
    ProductImageDeletionConflictError,
    ProductImageUpdateConflictError,
)

router = APIRouter(
    prefix="/product-image",
    tags=["Product image"],
)


@router.post("/", response_model=ProductImageResponse)
async def create_product_image(
    session: SessionDep,
    admin: AdminUser,
    data: ProductImageCreate,
) -> ProductImageResponse:
    try:
        product_image = await product_image_services.create_product_image(
            session=session,
            product_id=data.product_id,
            url=data.url,
            sort_order=data.sort_order,
            alt_text=data.alt_text,
        )
    except NotFoundProductError:
        raise not_found_product_error
    except ProductImageCreationConflictError:
        raise product_image_creation_conflict_error

    return ProductImageResponse.model_validate(product_image)

@router.get("/", response_model=list[ProductImageResponse])
async def get_product_images(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    product_id: uuid.UUID,
) -> list[ProductImageResponse]:
    product_images = await product_image_services.get_product_images(
        session=session,
        product_id=product_id,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return [ProductImageResponse.model_validate(product_image) for product_image in product_images]

@router.get("/{product_image_id}", response_model=ProductImageResponse)
async def get_product_image_by_id(
    session: SessionDep,
    product_image_id: uuid.UUID,
) -> ProductImageResponse:
    try:
        product_image = await product_image_services.get_product_image_or_raise(
            session=session,
            product_image_id=product_image_id,
        )
    except NotFoundProductImageError:
        raise not_found_product_image_error

    return ProductImageResponse.model_validate(product_image)

@router.patch("/{product_image_id}", response_model=ProductImageResponse)
async def update_product_image(
    session: SessionDep,
    admin: AdminUser,
    product_image_id: uuid.UUID,
    data: ProductImageUpdate,
) -> ProductImageResponse:
    try:
        updated_product_image = await product_image_services.update_product_image(
            session=session,
            product_image_id=product_image_id,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundProductImageError:
        raise not_found_product_image_error
    except ProductImageUpdateConflictError:
        raise product_image_update_conflict_error

    return ProductImageResponse.model_validate(updated_product_image)

@router.delete("/{product_image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    session: SessionDep,
    admin: AdminUser,
    product_image_id: uuid.UUID,
) -> None:
    try:
        await product_image_services.delete_product_image(
            session=session,
            product_image_id=product_image_id,
        )
    except NotFoundProductImageError:
        raise not_found_product_image_error
    except ProductImageDeletionConflictError:
        raise product_image_deletion_conflict_error