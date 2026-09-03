import json
import uuid
from datetime import datetime
from decimal import Decimal

import redis.asyncio as redis

from app.cache.constants import CACHE_TTL_PRODUCTS_LIST
from app.db.models.product import Product
from app.enums.currency import Currency


class ProductCache:

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    @staticmethod
    def _make_list_key(
        category_id: uuid.UUID | None = None,
        brand_id: uuid.UUID | None = None,
        is_active: bool | None = None, 
        offset: int = 0,
        limit: int = 20,
    ) -> str:
        parts = ["products:list"]

        parts.append(f"cat={category_id or "all"}")
        parts.append(f"brand={brand_id or "all"}")
        parts.append(f"act={"all" if is_active is None else is_active}")
        
        parts.extend([f"off={offset}", f"lim={limit}"])
        
        return ":".join(parts)
    
    @staticmethod
    def _product_to_dict(
        product: Product
    ) -> dict:
        return {
            "id": str(product.id),
            "sku": product.sku,
            "slug": product.slug,
            "name": product.name,
            "description": product.description,
            "base_price": str(product.base_price),
            "currency": product.currency.value,
            "category_id": str(product.category_id),
            "brand_id": str(product.brand_id),
            "attributes": json.dumps(product.attributes),
            "is_active": str(product.is_active),
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_product(data: dict) -> Product:
        return Product(
            id=uuid.UUID(data["id"]),
            sku=data["sku"],
            slug=data["slug"],
            name=data["name"],
            description=data["description"],
            base_price=Decimal(data["base_price"]),
            currency=Currency(data["currency"]),
            category_id=uuid.UUID(data["category_id"]),
            brand_id=uuid.UUID(data["brand_id"]) if data["brand_id"] else None,
            attributes=json.loads(data["attributes"]),
            is_active=data["is_active"].lower() == "true",
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
    )

    async def set_list(
        self,
        products: list[Product],
        category_id: uuid.UUID | None = None,
        brand_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> None:

        key = self._make_list_key(
            category_id=category_id,
            brand_id=brand_id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )

        data = [
            self._product_to_dict(product)
            for product in products
        ]

        await self.redis.set(
            key, 
            json.dumps(data),
            ex=CACHE_TTL_PRODUCTS_LIST
        )


    async def get_list(
        self,
        category_id: uuid.UUID | None = None,
        brand_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Product] | None:

        key = self._make_list_key(
            category_id=category_id,
            brand_id=brand_id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )

        cached = await self.redis.get(key)

        if  not cached:
            return None

        product_dicts = json.loads(cached)

        return [
            self._dict_to_product(product)
            for product in product_dicts 
        ]

    async def invalidate_list(
        self,
    ) -> None:
        keys_to_delete = []

        async for key in self.redis.scan_iter("products:list:*"):
            keys_to_delete.append(key)

        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)