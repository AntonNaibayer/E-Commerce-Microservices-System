import json
import uuid
from datetime import datetime

import redis.asyncio as redis

from app.cache.constants import CACHE_TTL_CATEGORIES_LIST
from app.db.models.category import Category


class CategoryCache:

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    @staticmethod
    def _make_list_key(
        parent_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> str:
        parts = ["categories:list"]

        parts.append(f"pid={parent_id or "all"}")
        parts.append(f"act={"all" if is_active is None else is_active}")
        
        parts.extend([f"off={offset}", f"lim={limit}"])

        return ":".join(parts)

    @staticmethod
    def _category_to_dict(
        category: Category
    ) -> dict:
        return {
            "id": str(category.id),
            "name": category.name,
            "slug": category.slug,
            "parent_id": str(category.id),
            "is_active": str(category.is_active),
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_category(
        category_dict: dict
    ) -> Category:
        return Category(
            id=uuid.UUID(category_dict['id']),
            name=category_dict["name"],
            slug=category_dict["slug"],
            parent_id=uuid.UUID(category_dict["parent_id"]) if category_dict["parent_id"] else None,
            is_active=category_dict["is_active"].lower() == "true",
            created_at=datetime.fromisoformat(category_dict["created_at"]),
            updated_at=datetime.fromisoformat(category_dict["updated_at"]),
        )

    async def set_list(
        self,
        categories: list[Category],
        parent_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> None:
        key = self._make_list_key(
            parent_id=parent_id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )

        data = [
            self._category_to_dict(category)
            for category in categories
        ]

        await self.redis.set(
            key,
            json.dumps(data),
            ex=CACHE_TTL_CATEGORIES_LIST,
        )

    async def get_list(
        self,
        parent_id: uuid.UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit:int = 20,
    ) -> list[Category] | None:
        key = self._make_list_key(
            parent_id=parent_id,
            is_active=is_active,
            offset=offset,
            limit=limit
        )

        cached = await self.redis.get(key)

        if not cached:
            return None

        data = json.loads(cached)

        return [
            self._dict_to_category(category)
            for category in data
        ]

    async def invalidate_list(
        self
    ) -> None:
        keys_to_delete = []

        async for key in self.redis.scan_iter("categories:list:*"):
            keys_to_delete.append(key)
            
        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)