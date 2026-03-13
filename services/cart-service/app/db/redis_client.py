import redis.asyncio as redis
from app.core.config import cart_settings

redis_client: redis.Redis = None


async def get_redis_client() -> redis.Redis:
    return redis_client


async def connect_redis():
    global redis_client
    redis_client = redis.from_url(
        cart_settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )


async def disconnect_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
