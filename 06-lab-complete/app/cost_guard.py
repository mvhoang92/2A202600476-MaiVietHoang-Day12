import time
import logging
import json
import os
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

# Note: In a real multi-server production environment, 
# _daily_cost should also be in Redis. We'll implement it with Redis support.
import redis
redis_client = None
if settings.redis_url:
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    except:
        pass

def check_and_record_cost(input_tokens: int, output_tokens: int):
    today = time.strftime("%Y-%m-%d")
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    # Chặn ngay lập tức nếu budget được set là 0 (để test)
    if settings.daily_budget_usd <= 0:
        raise HTTPException(503, f"Daily budget exhausted ($0.0). Try tomorrow.")

    if redis_client:
        redis_key = f"daily_cost:{today}"
        try:
            current_cost = float(redis_client.get(redis_key) or 0.0)
            if current_cost >= settings.daily_budget_usd:
                raise HTTPException(503, f"Daily budget exhausted (${settings.daily_budget_usd}). Try tomorrow.")
            
            new_cost = redis_client.incrbyfloat(redis_key, cost)
            redis_client.expire(redis_key, 172800)
            return new_cost
        except redis.RedisError as e:
            logger.error(f"Redis Cost Guard Error: {e}")
            return 0.0
    else:
        # Fallback local if no redis
        logger.warning(f"Cost Guard using local logic (No Redis). Cost: {cost}")
        return cost
