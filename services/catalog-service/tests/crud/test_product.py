import uuid
from decimal import Decimal

from app.db.crud import brand as brand_crud
from app.db.crud import category as category_crud
from app.db.crud import product as product_crud
from app.enums.currency import Currency


async def test_create_product(db_session, category):
    product = await product_crud.create_product(
            session=db_session,
            name="iPhone 17",
            sku="IPHONE-17",
            slug="iphone-17",
            description="Apple smartphone",
            base_price=Decimal("999.99"),
            currency=Currency.USD,
            category_id=category.id,
            attributes={"color": "black", "memory": "256GB"},
        )
    assert product.id is not None
    assert product.name == "iPhone 17"
    assert product.sku == "IPHONE-17"
    assert product.slug == "iphone-17"
    assert product.description == "Apple smartphone"
    assert product.base_price == Decimal("999.99")
    assert product.currency == Currency.USD
    assert product.category_id == category.id
    assert product.brand_id is None
    assert product.attributes == {
        "color": "black",
        "memory": "256GB",
    }
    assert product.is_active is True
    
async def test_create_product_with_brand(db_session, category, brand):

    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        brand_id=brand.id,
        attributes={"color": "black"},
    )

    assert product.brand_id == brand.id
    assert product.category_id == category.id

async def test_get_product_by_id(db_session, category):
    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    found_product = await product_crud.get_product_by_id(
        session=db_session,
        product_id=product.id,
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_product_by_id_when_not_found(db_session):
    random_id = uuid.uuid4()

    found_product = await product_crud.get_product_by_id(
        session=db_session,
        product_id=random_id,
    )

    assert found_product is None

async def test_get_product_by_slug(db_session, category):
    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    found_product = await product_crud.get_product_by_slug(
        session=db_session,
        product_slug="iphone-17",
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_product_by_sku(db_session, category):
    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    found_product = await product_crud.get_product_by_sku(
        session=db_session,
        product_sku="IPHONE-17",
    )

    assert found_product is not None
    assert found_product.id == product.id

async def test_get_products_with_filters(db_session):
    electronics = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics",
    )

    clothing = await category_crud.create_category(
        session=db_session,
        name="Одежда",
        slug="clothing",
    )

    apple = await brand_crud.create_brand(
        session=db_session,
        name="Apple",
        slug="apple",
    )

    samsung = await brand_crud.create_brand(
        session=db_session,
        name="Samsung",
        slug="samsung",
    )

    iphone = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=electronics.id,
        brand_id=apple.id,
        attributes={},
    )

    samsung_phone = await product_crud.create_product(
        session=db_session,
        name="Galaxy S26",
        sku="GALAXY-S26",
        slug="galaxy-s26",
        description="Samsung smartphone",
        base_price=Decimal("899.99"),
        currency=Currency.USD,
        category_id=electronics.id,
        brand_id=samsung.id,
        attributes={},
    )

    clothing_product = await product_crud.create_product(
        session=db_session,
        name="T-Shirt",
        sku="TSHIRT-001",
        slug="t-shirt",
        description="Cotton T-shirt",
        base_price=Decimal("29.99"),
        currency=Currency.USD,
        category_id=clothing.id,
        attributes={},
    )

    await product_crud.update_product(
        session=db_session,
        product=samsung_phone,
        is_active=False,
    )

    products = await product_crud.get_products(
        session=db_session,
        category_id=electronics.id,
        brand_id=apple.id,
        is_active=True,
    )

    assert len(products) == 1
    assert products[0].id == iphone.id
    assert samsung_phone not in products
    assert clothing_product not in products

async def test_get_products(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics",
    )

    first_product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    second_product = await product_crud.create_product(
        session=db_session,
        name="Galaxy S26",
        sku="GALAXY-S26",
        slug="galaxy-s26",
        description="Samsung smartphone",
        base_price=Decimal("899.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    products = await product_crud.get_products(
        session=db_session,
    )

    assert len(products) == 2
    assert first_product in products
    assert second_product in products

async def test_get_products_with_pagination(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics",
    )

    await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    await product_crud.create_product(
        session=db_session,
        name="Galaxy S26",
        sku="GALAXY-S26",
        slug="galaxy-s26",
        description="Samsung smartphone",
        base_price=Decimal("899.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    await product_crud.create_product(
        session=db_session,
        name="Pixel 10",
        sku="PIXEL-10",
        slug="pixel-10",
        description="Google smartphone",
        base_price=Decimal("799.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    first_page = await product_crud.get_products(
        session=db_session,
        offset=0,
        limit=2,
    )

    assert len(first_page) == 2

    second_page = await product_crud.get_products(
        session=db_session,
        offset=2,
        limit=2,
    )

    assert len(second_page) == 1

async def test_update_product(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics",
    )

    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={"color": "black"},
    )

    updated_product = await product_crud.update_product(
        session=db_session,
        product=product,
        name="iPhone 17 Pro",
        slug="iphone-17-pro",
        base_price=Decimal("1199.99"),
        attributes={"color": "silver"},
        is_active=False,
    )

    assert updated_product.id == product.id
    assert product.name == "iPhone 17 Pro"
    assert product.slug == "iphone-17-pro"
    assert product.base_price == Decimal("1199.99")
    assert product.attributes == {"color": "silver"}
    assert product.is_active is False

async def test_delete_product(db_session):
    category = await category_crud.create_category(
        session=db_session,
        name="Электроника",
        slug="electronics",
    )

    product = await product_crud.create_product(
        session=db_session,
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price=Decimal("999.99"),
        currency=Currency.USD,
        category_id=category.id,
        attributes={},
    )

    await product_crud.delete_product(
        session=db_session,
        product=product,
    )

    found_product = await product_crud.get_product_by_id(
        session=db_session,
        product_id=product.id,
    )

    assert found_product is None