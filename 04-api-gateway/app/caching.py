# -*- coding: utf-8 -*-
"""
Module xử lý việc lưu và truy xuất bộ nhớ đệm (Caching) bằng Redis.
"""
from app.redis_client import redis_client

# Thời gian cache sẽ được lưu lại (tính bằng giây). 3600 giây = 1 giờ.
CACHE_EXPIRATION_SECONDS = 3600

def get_from_cache(key: str):
    """Lấy dữ liệu từ cache Redis nếu có."""
    return redis_client.get(key)

def save_to_cache(key: str, value: str):
    """
    Lưu dữ liệu vào cache Redis với thời gian hết hạn.
    `ex=CACHE_EXPIRATION_SECONDS` sẽ tự động xóa key này sau 1 giờ.
    """
    redis_client.set(key, value, ex=CACHE_EXPIRATION_SECONDS)