import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from shared.auth.dependencies import AdminUser

from app.api.exceptions import (
    category_creation_conflict_error,
    category_deletion_conflict_error,
    category_update_conflict_error,
    duplicate_category_slug_error,
    not_found_category_error,
    not_found_parent_category_error,
)
from app.db.session import SessionDep
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.pagination_param import PaginationParams
from app.services import category as category_services
from app.services.exceptions import (
    CategoryCreationConflictError,
    CategoryDeletionConflictError,
    CategoryUpdateConflictError,
    DuplicateCategorySlugError,
    NotFoundCategoryError,
    NotFoundParentCategoryError,
)

router = APIRouter(
    prefix="/category",
    tags=["Category"],
)


@router.post("/", response_model=CategoryResponse)
async def create_category(
    session: SessionDep,
    data: CategoryCreate,
    admin: AdminUser,
) -> CategoryResponse:
    try:
        category = await category_services.create_category(
            session=session,
            category_name=data.name,
            parent_id=data.parent_id,
        )
    except DuplicateCategorySlugError:
        raise duplicate_category_slug_error
    except NotFoundParentCategoryError:
        raise not_found_parent_category_error
    except CategoryCreationConflictError:
        raise category_creation_conflict_error

    return CategoryResponse.model_validate(category)

@router.get("/", response_model=list[CategoryResponse])
async def get_categories(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    parent_id: uuid.UUID | None = None,
    is_active: bool | None = None,
) -> list[CategoryResponse]:
    categories = await category_services.get_categories(
        session=session,
        parent_id=parent_id,
        is_active=is_active,
        offset=pagination.offset,
        limit=pagination.limit,
    )

    return [CategoryResponse.model_validate(category) for category in categories]

@router.get("/slug/{category_slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    session: SessionDep,
    category_slug: str,
) -> CategoryResponse:
    try:
        category = await category_services.get_category_by_slug_or_raise(
            session=session,
            category_slug=category_slug,
        )
    except NotFoundCategoryError:
        raise not_found_category_error

    return CategoryResponse.model_validate(category)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(
    session: SessionDep,
    category_id: uuid.UUID,
) -> CategoryResponse:
    try:
        category = await category_services.get_category_or_raise(
            session=session,
            category_id=category_id,
        )
    except NotFoundCategoryError:
        raise not_found_category_error

    return CategoryResponse.model_validate(category)

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    session: SessionDep,
    admin: AdminUser,
    category_id: uuid.UUID,
    data: CategoryUpdate,
) -> CategoryResponse:
    try:
        category = await category_services.update_category(
            session=session,
            category_id=category_id,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundCategoryError:
        raise not_found_category_error
    except NotFoundParentCategoryError:
        raise not_found_parent_category_error
    except DuplicateCategorySlugError:
        raise duplicate_category_slug_error
    except CategoryUpdateConflictError:
        raise category_update_conflict_error

    return CategoryResponse.model_validate(category)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: SessionDep,
    admin: AdminUser,
    category_id: uuid.UUID,
) -> None:
    try:
        await category_services.delete_category(
            session=session,
            category_id=category_id,
        )
    except NotFoundCategoryError:
        raise not_found_category_error
    except CategoryDeletionConflictError:
        raise category_deletion_conflict_error