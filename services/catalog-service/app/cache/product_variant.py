import json
import uuid
from datetime import datetime
from decimal import Decimal

import redis.asyncio as redis

from app.cache.constants import CACHE_TTL_PRODUCT_VARIANTS_LIST
from app.db.models.product_variant import ProductVariant


class ProductVariantCache:

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    @staticmethod
    def _make_key_list(
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> str:
        parts = ["product_variants:list"]

        parts.append(f"prod={product_id}")
        parts.extend([f"off={offset}", f"lim={limit}"])
        
        return ":".join(parts)

    @staticmethod
    def _product_variant_to_dict(
        product_variant: ProductVariant,
    ) -> dict:
        return {
            "id": str(product_variant.id),
            "product_id": str(product_variant.product_id),
            "sku": product_variant.sku,
            "attributes": json.dumps(product_variant.attributes),
            "price_override": str(product_variant.price_override),
            "stock_quantity": str(product_variant.stock_quantity),
            "created_at": product_variant.created_at.isoformat(),
            "updated_at": product_variant.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_product_variant(
        product_variant_dict: dict,
    ) -> ProductVariant:
        return ProductVariant(
            id=uuid.UUID(product_variant_dict["id"]),
            product_id=uuid.UUID(product_variant_dict["product_id"]),
            sku=product_variant_dict.get("sku"),
            attributes=json.loads(product_variant_dict["attributes"]),
            price_override=Decimal(product_variant_dict["price_override"]),
            stock_quantity=int(product_variant_dict["stock_quantity"]),
            created_at=datetime.fromisoformat(product_variant_dict["created_at"]),
            updated_at=datetime.fromisoformat(product_variant_dict["updated_at"]),
        )

    async def set_list(
        self,
        product_variants: list[ProductVariant],
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> None:

        key = self._make_key_list(
            product_id=product_id,
            offset=offset,
            limit=limit,
        )

        data = [
            self._product_variant_to_dict(product_variant)
            for product_variant in product_variants
        ]

        await self.redis.set(
            key,
            json.dumps(data),
            ex=CACHE_TTL_PRODUCT_VARIANTS_LIST
        )

    async def get_list(
        self,
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ProductVariant] | None:

        key = self._make_key_list(
            product_id=product_id,
            offset=offset,
            limit=limit,
        )

        cached = await self.redis.get(key)

        if not cached:
            return None

        product_variant_dicts = json.loads(cached)

        return [
            self._dict_to_product_variant(product_variant)
            for product_variant in product_variant_dicts
        ]

    async def invalidate_list(
        self,
    ) -> None:

        keys_to_delete = []

        async for key in self.redis.scan_iter("product_variants:list:*"):
            keys_to_delete.append(key)

        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)
