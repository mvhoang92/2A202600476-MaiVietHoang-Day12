# -*- coding: utf-8 -*-
"""
Module xử lý việc xác thực API Key.
"""
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from app.config import AGENT_API_KEY, API_KEY_NAME

# Tạo một instance của APIKeyHeader, yêu cầu key phải có trong header
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(x_api_key: str = Security(api_key_header)):
    """
    Hàm dependency để kiểm tra API key.
    FastAPI sẽ tự động gọi hàm này cho các endpoint cần nó.
    """
    if not x_api_key or x_api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Invalid or missing API key"
        )
    return x_api_key
# -*- coding: utf-8 -*-
"""
Module xử lý việc xác thực API Key.
"""
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from app.config import AGENT_API_KEY, API_KEY_NAME

# Tạo một instance của APIKeyHeader, yêu cầu key phải có trong header
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(x_api_key: str = Security(api_key_header)):
    """
    Hàm dependency để kiểm tra API key.
    FastAPI sẽ tự động gọi hàm này cho các endpoint cần nó.
    """
    if not x_api_key or x_api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Forbidden: Invalid or missing API key"
        )
    return x_api_key