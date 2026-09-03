import json
import uuid
from datetime import datetime

import redis.asyncio as redis

from app.cache.constants import CACHE_TTL_PRODUCT_IMAGES_LIST
from app.db.models.product_image import ProductImage


class ProductImageCache:

    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client

    @staticmethod
    def _make_key_list(
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> str:
        parts = ["product_images:list"]

        parts.append(f"prod={product_id}")
        parts.extend([f"off={offset}", f"lim={limit}"])


        return ":".join(parts)

    @staticmethod
    def _product_image_to_dict(
        product_image: ProductImage,
    ) -> dict:
        return {
            "id": str(product_image.id),
            "product_id": str(product_image.product_id),
            "url": product_image.url,
            "alt_text": product_image.alt_text,
            "sort_order": str(product_image.sort_order),
            "created_at": product_image.created_at.isoformat(),
            "updated_at": product_image.updated_at.isoformat(),
        }

    @staticmethod
    def _dict_to_product_image(
        product_image_dict: dict,
    ) -> ProductImage:
        return ProductImage(
            id=uuid.UUID(product_image_dict["id"]),
            product_id=uuid.UUID(product_image_dict["product_id"]),
            url=product_image_dict["url"],
            alt_text=product_image_dict["alt_text"],
            sort_order=int(product_image_dict["sort_order"]),
            created_at=datetime.fromisoformat(product_image_dict["created_at"]),
            updated_at=datetime.fromisoformat(product_image_dict["updated_at"]),
        )

    async def set_list(
        self,
        product_images: list[ProductImage],
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> None:
        
        key = self._make_key_list(
            product_id=product_id,
            offset=offset,
            limit=limit,
        )

        product_image_dicts = [
            self._product_image_to_dict(product_image)
            for product_image in product_images
        ]

        await self.redis.set(
            key,
            json.dumps(product_image_dicts), 
            ex=CACHE_TTL_PRODUCT_IMAGES_LIST,
        )

    async def get_list(
        self,
        product_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> list[ProductImage] | None:

        key = self._make_key_list(
            product_id=product_id,
            offset=offset,
            limit=limit,
        )

        product_image_cached = await self.redis.get(key)

        if not product_image_cached:
            return None

        product_image_dicts = json.loads(product_image_cached)

        return [
            self._dict_to_product_image(product_image)
            for product_image in product_image_dicts
        ]

    async def invalidate_list(
        self,
    ) -> None:
        keys_to_delete = []

        async for key in self.redis.scan_iter("product_images:list:*"):
            keys_to_delete.append(key)
        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)