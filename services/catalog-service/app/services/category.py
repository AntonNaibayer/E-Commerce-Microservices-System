import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import category as category_crud
from app.db.models.category import Category
from app.services.exceptions import (
    CategoryCreationConflictError,
    CategoryDeletionConflictError,
    CategoryUpdateConflictError,
    DuplicateCategorySlugError,
    NotFoundCategoryError,
    NotFoundParentCategoryError,
)
from app.utils.slugify import generate_slug

_UNSET = object()

async def create_category(
    session: AsyncSession,
    category_name: str,
    parent_id: uuid.UUID | None = None,
) -> Category:

    category_slug = generate_slug(category_name)

    existing = await category_crud.get_category_by_slug(
        session=session,
        category_slug=category_slug,
    )
    if existing is not None:
        raise DuplicateCategorySlugError(category_slug)

    if parent_id is not None:
        parent_category = await category_crud.get_category_by_id(
            session=session,
            category_id=parent_id,
        )
        if parent_category is None:
            raise NotFoundParentCategoryError(parent_id)

    try:
        category = await category_crud.create_category(
            session=session,
            name=category_name,
            slug=category_slug,
            parent_id=parent_id,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryCreationConflictError(name=category_name, slug=category_slug)

    return category

async def get_category_or_raise(
    session: AsyncSession,
    category_id: uuid.UUID,
) -> Category:

    category = await category_crud.get_category_by_id(
        session=session,
        category_id=category_id,
    )
    if category is None:
        raise NotFoundCategoryError(category_id)

    return category

async def get_category_by_slug_or_raise(
    session: AsyncSession,
    category_slug: str,
) -> Category:

    category = await category_crud.get_category_by_slug(
        session=session,
        category_slug=category_slug,
    )
    if category is None:
        raise NotFoundCategoryError(category_slug)

    return category

async def get_categories(
    session: AsyncSession,
    parent_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    offset: int = 0,
    limit: int = 20,
) -> list[Category]:

    return await category_crud.get_categories(
        session=session,
        parent_id=parent_id,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )

async def update_category(
    session: AsyncSession,
    category_id: uuid.UUID,
    **fields,
) -> Category:

    category = await get_category_or_raise(
        session=session,
        category_id=category_id,
    )

    parent_id = fields.get("parent_id", _UNSET)

    if parent_id is not _UNSET and parent_id is not None:
        parent_category = await category_crud.get_category_by_id(
            session=session,
            category_id=parent_id,
        )
        if parent_category is None:
            raise NotFoundParentCategoryError(parent_id)

    category_name = fields.get("name", _UNSET)

    if category_name is not _UNSET and category_name is not None:
        new_slug = generate_slug(category_name)

        existing = await category_crud.get_category_by_slug(
            session=session,
            category_slug=new_slug,
        )
        if existing is not None and existing.id != category_id:
            raise DuplicateCategorySlugError(new_slug)

        fields["slug"] = new_slug

    try:
        updated_category = await category_crud.update_category(
            session=session,
            category=category,
            **fields,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryUpdateConflictError(category_id, **fields)

    return updated_category

async def delete_category(
    session: AsyncSession,
    category_id: uuid.UUID,
) -> None:

    category = await get_category_or_raise(
        session=session,
        category_id=category_id,
    )

    try:
        await category_crud.delete_category(
            session=session,
            category=category,
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise CategoryDeletionConflictError(category_id)