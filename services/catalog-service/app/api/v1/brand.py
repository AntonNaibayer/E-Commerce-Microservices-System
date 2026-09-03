import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from shared.auth.dependencies import AdminUser

from app.api.exceptions import (
    brand_creation_conflict_error,
    brand_deletion_conflict_error,
    brand_update_conflict_error,
    duplicate_brand_slug_error,
    not_found_brand_error,
)
from app.db.session import SessionDep
from app.schemas.brand import BrandCreate, BrandResponse, BrandUpdate
from app.schemas.pagination_param import PaginationParams
from app.services import brand as brand_services
from app.services.exceptions import (
    BrandCreationConflictError,
    BrandDeletionConflictError,
    BrandUpdateConflictError,
    DuplicateBrandSlugError,
    NotFoundBrandError,
)

router = APIRouter(
    prefix="/brand",
    tags=["Brand"],
)


@router.post("/", response_model=BrandResponse)
async def create_brand(
    session: SessionDep,
    data: BrandCreate,
    admin: AdminUser,
) -> BrandResponse:
    try:
        brand = await brand_services.create_brand(
            session=session,
            brand_name=data.name,
        )
    except DuplicateBrandSlugError:
        raise duplicate_brand_slug_error
    except BrandCreationConflictError:
        raise brand_creation_conflict_error

    return BrandResponse.model_validate(brand)

@router.get("/", response_model=list[BrandResponse])
async def get_brands(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
) -> list[BrandResponse]:
    brands = await brand_services.get_brands(
        session=session,
        offset=pagination.offset,
        limit=pagination.limit,
    )
    return [BrandResponse.model_validate(brand) for brand in brands]

@router.get("/slug/{brand_slug}", response_model=BrandResponse)
async def get_brand_by_slug(
    session: SessionDep,
    brand_slug: str,
) -> BrandResponse:
    try:
        brand = await brand_services.get_brand_by_slug_or_raise(
            session=session,
            brand_slug=brand_slug,
        )
    except NotFoundBrandError:
        raise not_found_brand_error

    return BrandResponse.model_validate(brand)

@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand_by_id(
    session: SessionDep,
    brand_id: uuid.UUID,
) -> BrandResponse:
    try:
        brand = await brand_services.get_brand_or_raise(
            session=session,
            brand_id=brand_id,
        )
    except NotFoundBrandError:
        raise not_found_brand_error

    return BrandResponse.model_validate(brand)

@router.patch("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    session: SessionDep,
    admin: AdminUser,
    brand_id: uuid.UUID,
    data: BrandUpdate,
) -> BrandResponse:
    try:
        updated_brand = await brand_services.update_brand(
            session=session,
            brand_id=brand_id,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundBrandError:
        raise not_found_brand_error
    except DuplicateBrandSlugError:
        raise duplicate_brand_slug_error
    except BrandUpdateConflictError:
        raise brand_update_conflict_error

    return BrandResponse.model_validate(updated_brand)

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    session: SessionDep,
    admin: AdminUser,
    brand_id: uuid.UUID,
) -> None:
    try:
        await brand_services.delete_brand(
            session=session,
            brand_id=brand_id,
        )
    except NotFoundBrandError:
        raise not_found_brand_error
    except BrandDeletionConflictError:
        raise brand_deletion_conflict_error