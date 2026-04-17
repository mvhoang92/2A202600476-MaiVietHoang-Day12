import time
from redis.asyncio import Redis
from app.config import settings

class RedisCostGuard:
    def __init__(self):
        self.redis: Redis = None
        # Reference prices
        self.PRICE_INPUT = 0.00015 / 1000  # $0.15 / 1M tokens
        self.PRICE_OUTPUT = 0.0006 / 1000  # $0.60 / 1M tokens

    async def connect(self):
        if settings.redis_url:
            self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self):
        if self.redis:
            await self.redis.aclose()

    def _get_day_key(self, user_id: str):
        today = time.strftime("%Y-%m-%d")
        return f"usage:{user_id}:{today}"

    async def get_usage(self, user_id: str) -> dict:
        if not self.redis:
            return {"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0}

        key = self._get_day_key(user_id)
        data = await self.redis.hgetall(key)
        return {
            "cost_usd": float(data.get("cost_usd", 0.0)),
            "input_tokens": int(data.get("input_tokens", 0)),
            "output_tokens": int(data.get("output_tokens", 0)),
        }

    async def record_usage(self, user_id: str, input_tokens: int, output_tokens: int):
        if not self.redis:
            return {"cost_usd": -1}

        cost = (input_tokens * self.PRICE_INPUT) + (output_tokens * self.PRICE_OUTPUT)
        key = self._get_day_key(user_id)
        
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.hincrby(key, "input_tokens", input_tokens)
            pipe.hincrby(key, "output_tokens", output_tokens)
            pipe.hincrbyfloat(key, "cost_usd", cost)
            pipe.expire(key, 86400 * 2) # Keep for 2 days
            results = await pipe.execute()
        
        return {
            "input_tokens": results[0],
            "output_tokens": results[1],
            "cost_usd": round(results[2], 6),
            "budget_usd": settings.daily_budget_usd
        }

redis_cost_guard = RedisCostGuard()
