import uuid
from decimal import Decimal

import pytest

from app.enums.currency import Currency
from app.services import product as product_services
from app.services.exceptions import (
    DuplicateProductSkuError,
    DuplicateProductSlugError,
    NotFoundBrand,
    NotFoundCategory,
    NotFoundProductError,
    ProductUpdateConflictError,
)


async def test_create_product(db_session, category):
    product = await product_services.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={"color": "black"},
    )

    assert product is not None
    assert product.name == "iPhone 17"
    assert product.sku == "IPHONE-17"
    assert product.slug == "iphone-17"
    assert product.category_id == category.id
    assert product.brand_id is None

async def test_create_product_with_brand(db_session, category, brand):
    product = await product_services.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        brand_id=brand.id,
        attributes={},
    )

    assert product.brand_id == brand.id

async def test_create_product_with_duplicate_sku(db_session, category):
    await product_services.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    with pytest.raises(DuplicateProductSkuError):
        await product_services.create_product(
            session=db_session,
            name="iPhone 17 Pro",
            sku="IPHONE-17",  # тот же sku
            description="Другое описание",
            base_price=Decimal("1199.99"),
            currency=Currency.USD,
            category_id=category.id,
            attributes={},
        )

async def test_create_product_with_duplicate_slug(db_session, category):
    await product_services.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    with pytest.raises(DuplicateProductSlugError):
        await product_services.create_product(
            session=db_session,
            name="iPhone 17",  # тот же slug получится
            sku="IPHONE-17-V2",
            description="Другое описание",
            base_price=Decimal("1199.99"),
            currency=Currency.USD,
            category_id=category.id,
            attributes={},
        )

async def test_create_product_when_category_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundCategory):
        await product_services.create_product(
            session=db_session,
            name="iPhone 17",
            sku="IPHONE-17",
            description="Apple smartphone",
            base_price=Decimal("999.99"),
            currency=Currency.USD,
            category_id=random_id,
            attributes={},
        )

async def test_create_product_when_brand_not_found(db_session, category):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundBrand):
        await product_services.create_product(
            session=db_session,
            name="iPhone 17",
            sku="IPHONE-17",
            description="Apple smartphone",
            base_price=Decimal("999.99"),
            currency=Currency.USD,
            category_id=category.id,
            brand_id=random_id,
            attributes={},
        )

async def test_get_product_or_raise(db_session, product):
    found_product = await product_services.get_product_or_raise(
        session=db_session,
        product_id=product.id,
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_product_or_raise_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductError):
        await product_services.get_product_or_raise(
            session=db_session,
            product_id=random_id,
        )

async def test_get_product_by_sku_or_raise(db_session, product):
    found_product = await product_services.get_product_by_sku_or_raise(
        session=db_session,
        product_sku=product.sku,
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_product_by_sku_or_raise_when_not_found(db_session):
    with pytest.raises(NotFoundProductError):
        await product_services.get_product_by_sku_or_raise(
            session=db_session,
            product_sku="NONEXISTENT-SKU",
        )

async def test_get_product_by_slug_or_raise(db_session, product):
    found_product = await product_services.get_product_by_slug_or_raise(
        session=db_session,
        product_slug=product.slug,
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_product_by_slug_or_raise_when_not_found(db_session):
    with pytest.raises(NotFoundProductError):
        await product_services.get_product_by_slug_or_raise(
            session=db_session,
            product_slug="nonexistent-slug",
        )

async def test_get_products(db_session, product_factory):
    first_product = await product_factory(name="iPhone 17", sku="IPHONE-17", slug="iphone-17")
    second_product = await product_factory(name="Galaxy S26", sku="GALAXY-S26", slug="galaxy-s26")

    products = await product_services.get_products(session=db_session)

    assert len(products) == 2
    assert first_product in products
    assert second_product in products

async def test_get_products_with_nonexistent_category_returns_empty_list(db_session):
    random_id = uuid.uuid4()

    products = await product_services.get_products(
        session=db_session,
        category_id=random_id,
    )

    assert products == []

async def test_update_product(db_session, product):
    updated_product = await product_services.update_product(
        session=db_session,
        product_id=product.id,
        name="iPhone 17 Pro",
        base_price=Decimal("1199.99"),
    )

    assert updated_product.id == product.id
    assert product.name == "iPhone 17 Pro"
    assert product.base_price == Decimal("1199.99")

async def test_update_product_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductError):
        await product_services.update_product(
            session=db_session,
            product_id=random_id,
            name="iPhone 17 Pro",
        )

async def test_update_product_when_category_not_found(db_session, product):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundCategory):
        await product_services.update_product(
            session=db_session,
            product_id=product.id,
            category_id=random_id,
        )

async def test_update_product_when_brand_not_found(db_session, product):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundBrand):
        await product_services.update_product(
            session=db_session,
            product_id=product.id,
            brand_id=random_id,
        )

async def test_update_product_with_duplicate_sku(db_session, category):
    first_product = await product_services.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    second_product = await product_services.create_product(
        session=db_session,
        name="Galaxy S26",
        sku="GALAXY-S26",
        description="Samsung smartphone",
        base_price=Decimal("899.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    with pytest.raises(ProductUpdateConflictError):
        await product_services.update_product(
            session=db_session,
            product_id=second_product.id,
            sku=first_product.sku,
        )

async def test_delete_product(db_session, product):
    await product_services.delete_product(
        session=db_session,
        product_id=product.id,
    )

    with pytest.raises(NotFoundProductError):
        await product_services.get_product_or_raise(
            session=db_session,
            product_id=product.id,
        )

async def test_delete_product_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductError):
        await product_services.delete_product(
            session=db_session,
            product_id=random_id,
        )