# -*- coding: utf-8 -*-
"""
Module quản lý kết nối đến Redis.
Tạo ra một instance duy nhất của Redis client để chia sẻ cho toàn bộ ứng dụng.
"""
import redis
from app.config import REDIS_HOST, REDIS_PORT

# Tạo một instance của Redis client.
# decode_responses=True giúp chúng ta nhận được dữ liệu dạng string thay vì bytes.
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

def get_redis_client():
    """
    Hàm này trả về instance của Redis client đã được khởi tạo.
    Chúng ta có thể dùng nó như một dependency trong tương lai nếu cần.
    """
    return redis_client