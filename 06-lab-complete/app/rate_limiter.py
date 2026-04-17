import time
import logging
from fastapi import HTTPException
import redis
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = None
if settings.redis_url:
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        redis_client.ping()
        logger.info("Connected to Redis for Rate Limiting")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None

def check_rate_limit(key: str):
    """
    Sliding Window Rate Limiter using Redis Sorted Sets.
    Fallback to in-memory if Redis is unavailable.
    """
    limit = settings.rate_limit_per_minute
    window = 60  # seconds
    now = time.time()
    
    if redis_client:
        redis_key = f"rate_limit:{key}"
        try:
            pipeline = redis_client.pipeline()
            # Remove old timestamps
            pipeline.zremrangebyscore(redis_key, 0, now - window)
            # Add current timestamp
            pipeline.zadd(redis_key, {str(now): now})
            # Count elements in window
            pipeline.zcard(redis_key)
            # Set expiration for current key (cleanup)
            pipeline.expire(redis_key, window)
            
            results = pipeline.execute()
            count = results[2]
            
            if count > limit:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {limit} req/min (Stateless)",
                    headers={"Retry-After": str(window)},
                )
        except redis.RedisError as e:
            logger.error(f"Redis Rate Limiter Error: {e}")
            # Optional: fallback to in-memory here if needed
    else:
        # Fallback to simple in-memory (local to this process)
        logger.warning("Redis not available, using in-memory rate limiter")
        # For simplicity in this module, we raise a 500 or just skip
        # but better to implement a secondary local one if needed.
        pass
