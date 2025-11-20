from typing import Optional, Any
import json
import redis.asyncio as redis
from app.core.config import settings

# Initialize Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: Any, expire: int = 300) -> bool:
    """Set value in cache with expiration"""
    try:
        client = await get_redis()
        await client.setex(
            key,
            expire,
            json.dumps(value)
        )
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    try:
        client = await get_redis()
        await client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


async def cache_clear_pattern(pattern: str) -> bool:
    """Clear all keys matching pattern"""
    try:
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
        return True
    except Exception as e:
        print(f"Cache clear error: {e}")
        return False
