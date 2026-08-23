from collections.abc import AsyncGenerator
from decimal import Decimal

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.core.config import DBSettings
from app.db.crud import brand as brand_crud
from app.db.crud import category as category_crud
from app.db.crud import product as product_crud
from app.enums.currency import Currency

test_db_settings = DBSettings(_env_file=".env.test") # type: ignore 


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(test_db_settings.database_url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    async with test_engine.connect() as connection:
        await connection.begin()

        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        yield session

        await session.close()
        await connection.rollback()

@pytest.fixture
def category_factory(db_session):
    async def create_category(
        name="Электроника",
        slug="electronics",
        parent_id=None,
    ):
        return await category_crud.create_category(
            session=db_session,
            name=name,
            slug=slug,
            parent_id=parent_id,
        )

    return create_category

@pytest.fixture
async def category(category_factory):
    return await category_factory()

@pytest.fixture
def brand_factory(db_session):
    async def create_brand(
        name="Apple",
        slug="apple",
    ):
        return await brand_crud.create_brand(
            session=db_session,
            name=name,
            slug=slug,
        )

    return create_brand

@pytest.fixture
async def brand(brand_factory):
    return await brand_factory()

@pytest.fixture
def product_factory(db_session, category):
    async def create_product(
        name="iPhone 17",
        sku="IPHONE-17",
        slug="iphone-17",
        description="Apple smartphone",
        base_price="999.99",
        currency=Currency.USD,
        category_id=None,
        brand_id=None,
        attributes=None,
        is_active=True,
    ):
        if category_id is None:
            category_id = category.id

        return await product_crud.create_product(
            session=db_session,
            name=name,
            sku=sku,
            slug=slug,
            description=description,
            base_price=Decimal(base_price),
            currency=currency,
            category_id=category_id,
            brand_id=brand_id,
            attributes=attributes or {},
            is_active=is_active,
        )

    return create_product

@pytest.fixture
async def product(product_factory):
    return await product_factory()