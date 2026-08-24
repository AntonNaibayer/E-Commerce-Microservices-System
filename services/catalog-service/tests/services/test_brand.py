import uuid

import pytest

from app.services import brand as brand_services
from app.services.exceptions import (
    DuplicateBrandSlugError,
    NotFoundBrand,
)


async def test_create_brand(db_session):
    brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    assert brand is not None
    assert brand.name == "Apple"
    assert brand.slug == "apple"

async def test_create_brand_with_duplicate_slug(db_session):
    await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    with pytest.raises(DuplicateBrandSlugError):
        await brand_services.create_brand(
            session=db_session,
            brand_name="Apple",
        )

async def test_get_brand_or_raise(db_session):
    brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    found_brand = await brand_services.get_brand_or_raise(
        session=db_session,
        brand_id=brand.id,
    )

    assert found_brand is not None
    assert found_brand.id == brand.id
    assert found_brand.name == brand.name

async def test_get_brand_or_raise_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundBrand):
        await brand_services.get_brand_or_raise(
            session=db_session,
            brand_id=random_id,
        )

async def test_get_brand_by_slug(db_session):
    brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    found_brand = await brand_services.get_brand_by_slug_or_raise(
        session=db_session,
        brand_slug="apple",
    )

    assert found_brand is not None
    assert found_brand.id == brand.id

async def test_get_brand_by_slug_when_not_found(db_session):
    with pytest.raises(NotFoundBrand):
        await brand_services.get_brand_by_slug_or_raise(
            session=db_session,
            brand_slug="apple",
        )

async def test_update_brand(db_session):
    brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    updated_brand = await brand_services.update_brand(
        session=db_session,
        brand_id=brand.id,
        name="Xiaomi",
        slug="xiaomi",
    )

    assert updated_brand.id == brand.id
    assert brand.name == "Xiaomi"
    assert brand.slug == "xiaomi"

async def test_update_brand_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundBrand):
        await brand_services.update_brand(
            session=db_session,
            brand_id=random_id,
            name="Xiaomi",
        )

async def test_update_brand_when_duplicate_slug(db_session):
    await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    other_brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Samsung",
    )

    with pytest.raises(DuplicateBrandSlugError):
        await brand_services.update_brand(
            session=db_session,
            brand_id=other_brand.id,
            slug="apple",
        )

async def test_delete_brand(db_session):
    brand = await brand_services.create_brand(
        session=db_session,
        brand_name="Apple",
    )

    await brand_services.delete_brand(
        session=db_session,
        brand_id=brand.id,
    )

    with pytest.raises(NotFoundBrand):
        await brand_services.get_brand_or_raise(
            session=db_session,
            brand_id=brand.id,
        )

async def test_delete_brand_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundBrand):
        await brand_services.delete_brand(
            session=db_session,
            brand_id=random_id,
        )