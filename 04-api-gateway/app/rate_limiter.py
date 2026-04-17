# -*- coding: utf-8 -*-
"""
Module xử lý việc giới hạn tần suất truy cập (Rate Limiting) bằng Redis.
"""
import time
from fastapi import HTTPException

from app.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD_SECONDS
from app.redis_client import redis_client

async def rate_limiter(key: str = "static_key"):
    """
    Hàm dependency để giới hạn tần suất sử dụng thuật toán sliding window với Redis.
    """
    now = time.time()
    # Tạo một key riêng cho rate limiting trong Redis
    redis_key = f"rate_limit:{key}"
    
    # Bắt đầu một "pipeline" để gom nhiều lệnh Redis thành một lượt gửi đi,
    # giúp đảm bảo tính nhất quán (atomic).
    p = redis_client.pipeline()
    
    # 1. Xóa tất cả các request cũ (có timestamp nhỏ hơn thời điểm bắt đầu cửa sổ)
    window_start = now - RATE_LIMIT_PERIOD_SECONDS
    p.zremrangebyscore(redis_key, 0, window_start)
    
    # 2. Thêm request hiện tại vào set. Timestamp được dùng cho cả score và value.
    p.zadd(redis_key, {now: now})
    
    # 3. Đếm số lượng request còn lại trong cửa sổ
    p.zcard(redis_key)
    
    # Thực thi tất cả các lệnh trong pipeline
    results = p.execute()
    
    # Lấy kết quả của lệnh zcard (lệnh thứ 3)
    current_count = results[2]
    
    if current_count > RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429, # Too Many Requests
            detail=f"Rate limit exceeded: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_PERIOD_SECONDS} seconds"
        )