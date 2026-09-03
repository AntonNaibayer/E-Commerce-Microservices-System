import uuid

import pytest

from app.services import category as category_services
from app.services.exceptions import (
    DuplicateCategorySlugError,
    NotFoundCategory,
    NotFoundParentCategory,
)
from app.utils.slugify import generate_slug


async def test_create_category(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    assert category is not None
    assert category.name == "Электроника"

async def test_create_category_with_parent_category(db_session):
    parent_category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    child_category = await category_services.create_category(
        session=db_session,
        category_name="Телефоны",
        parent_id=parent_category.id
    )

    assert child_category.parent_id is not None
    assert child_category.parent_id == parent_category.id

async def test_create_category_with_duplicate_slug(db_session):
    await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    with pytest.raises(DuplicateCategorySlugError):
        await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

async def test_create_category_when_parent_category_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundParentCategory):
        await category_services.create_category(
            session=db_session,
            category_name="Электроника",
            parent_id=random_id
        )

async def test_get_category_or_raise(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    found_category = await category_services.get_category_or_raise(
        session=db_session,
        category_id=category.id
    )

    assert found_category is not None
    assert found_category.id == category.id
    assert found_category.name == category.name

async def test_get_category_or_raise_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundCategory):
        await category_services.get_category_or_raise(
            session=db_session,
            category_id=random_id
        )

async def test_get_category_by_slug_or_raise(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    category_slug = generate_slug(category.name)

    found_category = await category_services.get_category_by_slug_or_raise(
        session=db_session,
        category_slug=category_slug
    )

    assert found_category is not None
    assert found_category.id == category.id
    assert found_category.slug == category.slug

async def test_get_category_by_slug_or_raise_when_not_found(db_session):
    category_slug = generate_slug("Электроника")

    with pytest.raises(NotFoundCategory):
        await category_services.get_category_by_slug_or_raise(
            session=db_session,
            category_slug=category_slug
        )

async def test_update_category(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    await category_services.update_category(
        session=db_session,
        category_id=category.id,
        name="Телефоны",
        slug="Phones",
        is_active=False
    )

    assert category.name == "Телефоны"
    assert category.slug == "Phones"
    assert not category.is_active

async def test_update_category_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundCategory):
        await category_services.update_category(
            session=db_session,
            category_id=random_id
        )

async def test_update_category_when_parent_category_not_found(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    random_id = uuid.uuid4()

    with pytest.raises(NotFoundParentCategory):
        await category_services.update_category(
            session=db_session,
            category_id=category.id,
            parent_id=random_id
        )
async def test_update_category_when_duplicate_category_slug(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    duplicate_slug_category = await category_services.create_category(
        session=db_session,
        category_name="Другая Электроника"
    )

    with pytest.raises(DuplicateCategorySlugError):
        await category_services.update_category(
            session=db_session,
            category_id=category.id,
            slug=duplicate_slug_category.slug
        )

async def test_delete_category(db_session):
    category = await category_services.create_category(
        session=db_session,
        category_name="Электроника",
    )

    await category_services.delete_category(
        session=db_session,
        category_id=category.id
    )

    with pytest.raises(NotFoundCategory):
        await category_services.get_category_or_raise(
            session=db_session,
            category_id=category.id,
        )

async def test_delete_category_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundCategory):
        await category_services.delete_category(
            session=db_session,
            category_id=random_id,
        )