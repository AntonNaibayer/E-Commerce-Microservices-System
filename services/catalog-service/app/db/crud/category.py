import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.category import Category


async def create_category(
    session: AsyncSession,
    name: str,
    slug: str,
    parent_id: uuid.UUID | None = None,
) -> Category:
    new_category = Category(
        name=name,
        slug=slug,
        parent_id=parent_id
    )
    session.add(new_category)
    await session.flush()
    
    return new_category

async def update_category(
    session: AsyncSession,
    category: Category,
    **fields
) -> Category:
    for key, value in fields.items():
        setattr(category, key, value)

    await session.flush()
    await session.refresh(category)
    return category

async def get_category_by_id(
    session: AsyncSession,
    category_id: uuid.UUID
) -> Category | None:
    stmt = (
        select(Category).
        where(Category.id == category_id)
    )
    return await session.scalar(stmt)

async def get_categories(
    session: AsyncSession,
    parent_id: uuid.UUID | None = None,
    is_active: bool | None =  None,
    offset: int = 0,
    limit: int = 20
) -> list[Category]:

    stmt = select(Category)

    if parent_id is not None:
        stmt = stmt.where(Category.parent_id == parent_id)

    if is_active is not None:
        stmt = stmt.where(Category.is_active == is_active)
    
    stmt = (
        stmt
        .order_by(Category.id)
        .offset(offset)
        .limit(limit)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())    

async def get_category_by_slug(
    session: AsyncSession,
    category_slug: str
) -> Category | None:
    stmt = (
        select(Category)
        .where(Category.slug == category_slug)
    )
    return await session.scalar(stmt)

async def delete_category(
    session: AsyncSession,
    category: Category
) -> None:
    await session.delete(category)
    await session.flush()
