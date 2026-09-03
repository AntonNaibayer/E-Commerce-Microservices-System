import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import category as category_crud


async def test_create_category(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    assert category.id is not None
    assert category.name == "Электроника"
    assert category.slug == "electronics"
    assert category.parent_id is None
    assert category.is_active is True

async def test_create_category_with_parent_category(db_session):
    parent_category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )
    child_category = await category_crud.create_category(
        session=db_session,
        name="Телефоны",
        slug="telefony",
        parent_id=parent_category.id
    )

    assert child_category.parent_id is not None
    assert child_category.parent_id == parent_category.id

async def test_create_category_with_duplicate_slug(db_session):
    await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    with pytest.raises(IntegrityError):
        await category_crud.create_category(
            session=db_session,
            name="Другая Электроника",
            slug="electronics"  # Повторяющийся slug
        )    

async def test_get_category_by_id(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    found_category = await category_crud.get_category_by_id(
        session=db_session,
        category_id=category.id
    )
    assert found_category is not None
    assert category.id == found_category.id
    assert category.name == found_category.name
    assert category.slug == found_category.slug
    assert category.parent_id == found_category.parent_id
    assert found_category.is_active

async def test_get_category_by_id_returns_none_when_not_found(db_session):
    random_id = uuid.uuid4()
    found_category = await category_crud.get_category_by_id(
        session=db_session,
        category_id=random_id
    )

    assert found_category is None

async def test_update_category(db_session: AsyncSession):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    clothing = await category_crud.create_category(
        session=db_session,
        name="Одежда",
        slug="clothing"
    )

    updated_category = await category_crud.update_category(
        session=db_session,
        category=clothing,
        name="Бытовая техника",
        slug="appliances",
        parent_id=electronics.id,
        is_active=False
    )

    assert updated_category is not None
    assert clothing.id == updated_category.id
    assert clothing.name == "Бытовая техника"
    assert clothing.slug == "appliances"
    assert clothing.parent_id == electronics.id
    assert not clothing.is_active

async def test_get_categories(db_session):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    clothing = await category_crud.create_category(
        session=db_session,
        name="Одежда",
        slug="clothing"
    )

    books = await category_crud.create_category(
        session=db_session,
        name="Книги",
        slug="books"
    )

    categories = await category_crud.get_categories(
        session=db_session
    )

    assert len(categories) == 3
    assert electronics in categories
    assert clothing in categories
    assert books in categories

async def test_get_categories_with_filter(db_session):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    telefony = await category_crud.create_category(
        session=db_session,
        name="Телефоны",
        slug="telefony",
        parent_id=electronics.id
    )

    computers = await category_crud.create_category(
        session=db_session,
        name="Компьютеры",
        slug="computers",
        parent_id=electronics.id
    )

    laptops = await category_crud.create_category(
        session=db_session,
        name="Ноутбуки",
        slug="laptops",
        parent_id=electronics.id
    )

    laptops = await category_crud.update_category(
        session=db_session,
        category=laptops,
        is_active=False
    )

    categories = await category_crud.get_categories(
        session=db_session,
        parent_id=electronics.id,
        is_active=True
    )

    assert len(categories) == 2
    assert telefony in categories
    assert computers in categories
    assert laptops not in categories

async def test_get_categories_with_pagination(db_session):
    await category_crud.create_category(
        session=db_session,
        name="Телефоны",
        slug="telefony",
    )

    await category_crud.create_category(
        session=db_session,
        name="Компьютеры",
        slug="computers",
    )

    await category_crud.create_category(
        session=db_session,
        name="Ноутбуки",
        slug="laptops",
    )

    first_page = await category_crud.get_categories(
        session=db_session,
        offset=0,
        limit=2
    )

    assert len(first_page) == 2

    second_page = await category_crud.get_categories(
        session=db_session,
        offset=2,
        limit=2
    )

    assert len(second_page) == 1

async def test_get_category_by_slug(db_session):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    found_category = await category_crud.get_category_by_slug(
        session=db_session,
        category_slug="electronics"
    )

    assert found_category is not None
    assert found_category.id == electronics.id

async def test_delete_category(db_session):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics"
    )

    await category_crud.delete_category(
        session=db_session,
        category=electronics
    )

    found_category = await category_crud.get_category_by_id(
        session=db_session,
        category_id=electronics.id
    )

    assert found_category is None
