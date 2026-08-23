import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.crud import brand as brand_crud


async def test_create_brand(db_session):
    brand = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    assert brand.id is not None
    assert brand.name == "Apple"
    assert brand.slug == "apple"

async def test_create_brand_with_duplicate_slug(db_session):
    await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    with pytest.raises(IntegrityError):
        await brand_crud.create_brand(
            session=db_session,
            name="AnotherAppple",
            slug="apple"
        )
    
async def test_get_brand_by_id(db_session):
    brand = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    found_brand = await brand_crud.get_brand_by_id(
        session=db_session,
        brand_id=brand.id
    )

    assert found_brand is not None
    assert found_brand.id == brand.id

async def test_get_brand_by_id_when_not_found(db_session):
    random_id = uuid.uuid4()

    found_brand = await brand_crud.get_brand_by_id(
        session=db_session,
        brand_id=random_id
    )

    assert found_brand is None

async def test_get_brand_by_slug(db_session):
    brand = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    found_brand = await brand_crud.get_brand_by_slug(
        session=db_session,
        slug="apple"
    )

    assert found_brand is not None
    assert brand.id == found_brand.id

async def test_get_brand_by_slug_when_not_found(db_session):
    found_brand = await brand_crud.get_brand_by_slug(
        session=db_session,
        slug="apple"
    )

    assert found_brand is None

async def test_get_brands(db_session):
    await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )
    await brand_crud.create_brand(
        session=db_session,
        name="Samsung",
        slug="samsung"
    )
    await brand_crud.create_brand(
        session=db_session,
        name="Xiaomi",
        slug="xiaomi"
    )

    brands = await brand_crud.get_brands(
        session=db_session
    )

    assert len(brands) == 3

async def test_get_brands_with_pagination(db_session):
    await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )
    await brand_crud.create_brand(
        session=db_session,
        name="Samsung",
        slug="samsung"
    )
    await brand_crud.create_brand(
        session=db_session,
        name="Xiaomi",
        slug="xiaomi"
    )

    first_page = await brand_crud.get_brands(
        session=db_session,
        offset=0,
        limit=2
    )

    assert len(first_page) == 2

    second_page = await brand_crud.get_brands(
        session=db_session,
        offset=2,
        limit=2
    )

    assert len(second_page) == 1

async def test_update_brand(db_session):
    brand = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    updated_brand = await brand_crud.update_brand(
        session=db_session,
        brand=brand,
        name="Xiaomi",
        slug="xiaomi"
    )

    assert brand.id == updated_brand.id
    assert brand.name == "Xiaomi"
    assert brand.slug == "xiaomi"

async def test_delete_brand(db_session):
    brand = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple"
    )

    await brand_crud.delete_brand(
        session=db_session,
        brand=brand
    )

    found_brand = await brand_crud.get_brand_by_id(
        session=db_session,
        brand_id=brand.id
    )

    assert found_brand is None