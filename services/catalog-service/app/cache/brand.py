import json
import uuid
from datetime import datetime

import redis.asyncio as redis

from app.cache.constants import CACHE_TTL_BRANDS_LIST
from app.db.models.brand import Brand


class BrandCache:

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    @staticmethod
    def _make_list_key(
        offset: int,
        limit: int,
    ) -> str:
        parts = ["brands:list"]

        parts.extend([f"off={offset}", f"lim={limit}"])

        return ":".join(parts)

    @staticmethod
    def _brand_to_dict(brand: Brand) -> dict:
        return {
            "id": str(brand.id),
            "name": brand.name,
            "slug": brand.slug,
            "created_at": brand.created_at.isoformat(),
            "updated_at": brand.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_brand(
        brand_dict: dict
    ) -> Brand:
        return Brand(
            id=uuid.UUID(brand_dict["id"]),
            name=brand_dict["name"],
            slug=brand_dict["slug"],
            created_at=datetime.fromisoformat(brand_dict["created_at"]),
            updated_at=datetime.fromisoformat(brand_dict["updated_at"])
        )

    async def set_list(
        self,
        brands: list[Brand],
        offset: int,
        limit: int,
    ) -> None:
        key = self._make_list_key(
            offset=offset,
            limit=limit,
        )

        data = [
            self._brand_to_dict(brand)
            for brand in brands
        ]

        await self.redis.set(
            key,
            json.dumps(data),
            ex=CACHE_TTL_BRANDS_LIST
        )

    async def get_list(
        self,
        offset: int,
        limit: int,
    ) -> list[Brand] | None:

        key = self._make_list_key(
            offset=offset,
            limit=limit
        )

        cached = await self.redis.get(key)

        if not cached:
            return None

        data = json.loads(cached)

        return [
            self._dict_to_brand(brand) 
            for brand in data
        ] 

    async def invalidate_list(
        self
    ) -> None:

        keys_to_delete = []

        async for key in self.redis.scan_iter("brands:list:*"):
            keys_to_delete.append(key)

        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)


