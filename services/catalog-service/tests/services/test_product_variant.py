import uuid
from decimal import Decimal

import pytest

from app.services import product_variant as product_variant_services
from app.services.exceptions import (
    DuplicateProductVariantSkuError,
    NotFoundProductError,
    NotFoundProductVariantError,
    ProductVariantUpdateConflictError,
)


async def test_create_product_variant(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black", "memory": "256GB"},
        stock_quantity=10,
    )

    assert variant.id is not None
    assert variant.product_id == product.id
    assert variant.sku == "IPHONE-17-BLACK-256"
    assert variant.stock_quantity == 10
    assert variant.price_override is None

async def test_create_product_variant_with_price_override(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
        price_override=Decimal("1099.99"),
    )

    assert variant.price_override == Decimal("1099.99")

async def test_create_product_variant_when_product_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductError):
        await product_variant_services.create_product_variant(
            session=db_session,
            product_id=random_id,
            sku="IPHONE-17-BLACK-256",
            attributes={},
            stock_quantity=10,
        )

async def test_create_product_variant_with_duplicate_sku(db_session, product):
    await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    with pytest.raises(DuplicateProductVariantSkuError):
        await product_variant_services.create_product_variant(
            session=db_session,
            product_id=product.id,
            sku="IPHONE-17-BLACK-256",
            attributes={"color": "white"},
            stock_quantity=5,
        )

async def test_get_product_variant_or_raise(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    found_variant = await product_variant_services.get_product_variant_or_raise(
        session=db_session,
        product_variant_id=variant.id,
    )

    assert found_variant is not None
    assert found_variant.id == variant.id

async def test_get_product_variant_or_raise_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductVariantError):
        await product_variant_services.get_product_variant_or_raise(
            session=db_session,
            product_variant_id=random_id,
        )

async def test_get_product_variant_or_raise_by_sku(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    found_variant = await product_variant_services.get_product_variant_or_raise_by_sku(
        session=db_session,
        product_variant_sku="IPHONE-17-BLACK-256",
    )

    assert found_variant is not None
    assert found_variant.id == variant.id

async def test_get_product_variant_or_raise_by_sku_when_not_found(db_session):
    with pytest.raises(NotFoundProductVariantError):
        await product_variant_services.get_product_variant_or_raise_by_sku(
            session=db_session,
            product_variant_sku="NONEXISTENT-SKU",
        )

async def test_get_product_variants(db_session, product):
    first_variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    second_variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-WHITE",
        attributes={"color": "white"},
        stock_quantity=15,
    )

    variants = await product_variant_services.get_product_variants(
        session=db_session,
        product_id=product.id,
    )

    assert len(variants) == 2
    assert {v.id for v in variants} == {first_variant.id, second_variant.id}

async def test_get_product_variants_with_pagination(db_session, product):
    for i in range(3):
        await product_variant_services.create_product_variant(
            session=db_session,
            product_id=product.id,
            sku=f"IPHONE-{i}",
            attributes={},
            stock_quantity=10,
        )

    first_page = await product_variant_services.get_product_variants(
        session=db_session,
        product_id=product.id,
        offset=0,
        limit=2,
    )
    assert len(first_page) == 2

    second_page = await product_variant_services.get_product_variants(
        session=db_session,
        product_id=product.id,
        offset=2,
        limit=2,
    )
    assert len(second_page) == 1

async def test_update_product_variant(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
        price_override=Decimal("1099.99"),
    )

    updated_variant = await product_variant_services.update_product_variant(
        session=db_session,
        product_variant_id=variant.id,
        sku="IPHONE-BLACK-256",
        stock_quantity=25,
        price_override=Decimal("999.99"),
    )

    assert updated_variant.id == variant.id
    assert variant.sku == "IPHONE-BLACK-256"
    assert variant.stock_quantity == 25
    assert variant.price_override == Decimal("999.99")

async def test_update_product_variant_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductVariantError):
        await product_variant_services.update_product_variant(
            session=db_session,
            product_variant_id=random_id,
            stock_quantity=5,
        )

async def test_update_product_variant_when_product_not_found(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductError):
        await product_variant_services.update_product_variant(
            session=db_session,
            product_variant_id=variant.id,
            product_id=random_id,
        )

async def test_update_product_variant_with_duplicate_sku(db_session, product):
    first_variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    second_variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-WHITE",
        attributes={"color": "white"},
        stock_quantity=5,
    )

    with pytest.raises(ProductVariantUpdateConflictError):
        await product_variant_services.update_product_variant(
            session=db_session,
            product_variant_id=second_variant.id,
            sku=first_variant.sku,
        )

async def test_delete_product_variant(db_session, product):
    variant = await product_variant_services.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    await product_variant_services.delete_product_variant(
        session=db_session,
        product_variant_id=variant.id,
    )

    with pytest.raises(NotFoundProductVariantError):
        await product_variant_services.get_product_variant_or_raise(
            session=db_session,
            product_variant_id=variant.id,
        )

async def test_delete_product_variant_when_not_found(db_session):
    random_id = uuid.uuid4()

    with pytest.raises(NotFoundProductVariantError):
        await product_variant_services.delete_product_variant(
            session=db_session,
            product_variant_id=random_id,
        )