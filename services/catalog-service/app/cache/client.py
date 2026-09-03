import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.Redis(
    host=settings.redis.REDIS_HOST,
    port=settings.redis.REDIS_PORT,
    password=settings.redis.REDIS_PASS,
    db=0,
    decode_responses=True,
)