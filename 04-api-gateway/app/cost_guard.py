# -*- coding: utf-8 -*-
"""
Module xử lý việc theo dõi và giới hạn chi phí (Cost Guard) bằng Redis.
"""
from fastapi import HTTPException

from app.config import BUDGET, AVG_TOKEN_PRICE
from app.redis_client import redis_client

# Tên của key trong Redis để lưu tổng chi phí
TOTAL_COST_KEY = "total_cost"

def get_total_cost():
    """Đọc tổng chi phí từ Redis."""
    cost = redis_client.get(TOTAL_COST_KEY)
    return float(cost) if cost else 0.0

def update_total_cost(cost_to_add):
    """
    Cộng thêm chi phí vào tổng chi phí trong Redis một cách an toàn.
    INCRBYFLOAT là một lệnh "atomic", đảm bảo không có lỗi xảy ra
    khi nhiều request cùng cập nhật chi phí một lúc.
    Hàm này sẽ trả về tổng chi phí mới sau khi đã cộng.
    """
    return redis_client.incrbyfloat(TOTAL_COST_KEY, cost_to_add)

def get_estimated_cost(tokens):
    """Ước tính chi phí dựa trên số token."""
    return (tokens / 1000) * AVG_TOKEN_PRICE

async def cost_guard():
    """
    Hàm dependency để kiểm tra ngân sách.
    """
    total_cost = get_total_cost()
    if total_cost >= BUDGET:
        raise HTTPException(
            status_code=429,  # Too Many Requests
            detail=f"Temporary budget limit exceeded. Current cost: ${total_cost:.2f}, Budget: ${BUDGET:.2f}"
        )