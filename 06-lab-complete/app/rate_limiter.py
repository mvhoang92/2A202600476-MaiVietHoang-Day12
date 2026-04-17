import time
import json
from fastapi import HTTPException
from redis.asyncio import Redis
from app.config import settings

class RedisRateLimiter:
    def __init__(self, window_seconds: int = 60):
        self.redis: Redis = None
        self.window_seconds = window_seconds

    async def connect(self):
        if settings.redis_url:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.aclose()

    async def check(self, user_id: str):
        if not self.redis:
            return # Fallback: allow if redis is down

        now = time.time()
        key = f"rate_limit:{user_id}"
        
        # Sliding window using Sorted Set
        async with self.redis.pipeline(transaction=True) as pipe:
            # Remove old timestamps
            pipe.zremrangebyscore(key, 0, now - self.window_seconds)
            # Count remaining
            pipe.zcard(key)
            # Add current
            pipe.zadd(key, {str(now): now})
            # Set expiry for the whole set
            pipe.expire(key, self.window_seconds)
            
            _, count, _, _ = await pipe.execute()

        if count >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
                headers={"Retry-After": str(self.window_seconds)}
            )

redis_limiter = RedisRateLimiter()
