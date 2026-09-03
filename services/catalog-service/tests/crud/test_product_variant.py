import uuid
from decimal import Decimal

from app.db.crud import product_variant as product_variant_crud


async def test_create_product_variant(
    db_session,
    product,
):
    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={
            "color": "black",
            "memory": "256GB",
        },
        stock_quantity=10,
    )

    assert variant.id is not None
    assert variant.product_id == product.id
    assert variant.sku == "IPHONE-17-BLACK-256"
    assert variant.attributes == {
        "color": "black",
        "memory": "256GB",
    }
    assert variant.stock_quantity == 10
    assert variant.price_override is None

async def test_create_product_variant_with_price_override(
    db_session,
    product,
):
    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={
            "color": "black",
            "memory": "256GB",
        },
        stock_quantity=10,
        price_override=Decimal("1099.99"),
    )

    assert variant.price_override == Decimal("1099.99")

async def test_get_product_variant_by_id(
    db_session,
    product,
):
    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    found_variant = await product_variant_crud.get_product_variant_by_id(
        session=db_session,
        product_variant_id=variant.id,
    )

    assert found_variant is not None
    assert found_variant.id == variant.id

async def test_get_product_variant_by_id_when_not_found(
    db_session,
):
    random_id = uuid.uuid4()

    found_variant = await product_variant_crud.get_product_variant_by_id(
        session=db_session,
        product_variant_id=random_id,
    )

    assert found_variant is None

async def test_get_product_variant_by_sku(
    db_session,
    product_factory,
):
    product = await product_factory()

    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-17-BLACK-256",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    found_variant = await product_variant_crud.get_product_variant_by_sku(
        session=db_session,
        product_variant_sku="IPHONE-17-BLACK-256",
    )

    assert found_variant is not None
    assert found_variant.id == variant.id

async def test_get_product_variants(
    db_session,
    product,
):
    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-WHITE",
        attributes={"color": "white"},
        stock_quantity=15,
    )

    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLUE",
        attributes={"color": "blue"},
        stock_quantity=20,
    )

    variants = await product_variant_crud.get_product_variants(
        session=db_session,
        product_id=product.id,
    )

    assert len(variants) == 3

async def test_get_product_variants_with_pagination(
    db_session,
    product,
):
    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-WHITE",
        attributes={"color": "white"},
        stock_quantity=15,
    )

    await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLUE",
        attributes={"color": "blue"},
        stock_quantity=20,
    )

    first_page = await product_variant_crud.get_product_variants(
        session=db_session,
        product_id=product.id,
        offset=0,
        limit=2,
    )

    assert len(first_page) == 2

    second_page = await product_variant_crud.get_product_variants(
        session=db_session,
        product_id=product.id,
        offset=2,
        limit=2,
    )

    assert len(second_page) == 1

async def test_update_product_variant(
    db_session,
    product,
):
    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
        price_override=Decimal("1099.99"),
    )

    updated_variant = await product_variant_crud.update_product_variant(
        session=db_session,
        product_variant=variant,
        sku="IPHONE-BLACK-256",
        attributes={
            "color": "black",
            "memory": "256GB",
        },
        stock_quantity=25,
        price_override=Decimal("999.99"),
    )

    assert updated_variant.id == variant.id
    assert variant.sku == "IPHONE-BLACK-256"
    assert variant.attributes == {
        "color": "black",
        "memory": "256GB",
    }
    assert variant.stock_quantity == 25
    assert variant.price_override == Decimal("999.99")

async def test_delete_product_variant(
    db_session,
    product,
):
    variant = await product_variant_crud.create_product_variant(
        session=db_session,
        product_id=product.id,
        sku="IPHONE-BLACK",
        attributes={"color": "black"},
        stock_quantity=10,
    )

    await product_variant_crud.delete_product_variant(
        session=db_session,
        product_variant=variant,
    )

    found_variant = await product_variant_crud.get_product_variant_by_id(
        session=db_session,
        product_variant_id=variant.id,
    )

    assert found_variant is None