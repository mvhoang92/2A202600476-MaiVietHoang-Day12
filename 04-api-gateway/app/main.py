# -*- coding: utf-8 -*-
"""
File chính của API Gateway, kết nối các module và định nghĩa các endpoint.
"""
import sys
import os

# Thêm thư mục gốc của dự án vào sys.path để có thể import `utils`
# Điều này giúp ứng dụng có thể chạy được từ bất kỳ đâu.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Import các module đã được tái cấu trúc ---
from app.auth import get_api_key
from app.rate_limiter import rate_limiter
from app.cost_guard import cost_guard, get_estimated_cost, update_total_cost
from app.caching import get_from_cache, save_to_cache
from utils.mock_llm import ask

# --- Khởi tạo FastAPI ---
app = FastAPI(title="Production-Ready API Gateway")

# --- Định nghĩa Model cho Request Body ---
class QuestionRequest(BaseModel):
    question: str

# --- Định nghĩa các Endpoints ---

@app.get("/health", status_code=200)
async def health_check():
    """Endpoint để kiểm tra server có đang hoạt động không."""
    return {"status": "ok"}

@app.post("/ask", dependencies=[Depends(get_api_key), Depends(rate_limiter), Depends(cost_guard)])
async def ask_agent(req_body: QuestionRequest):
    # 1. Kiểm tra cache trước
    cached_answer = get_from_cache(req_body.question)
    if cached_answer:
        return JSONResponse(
            content={"answer": cached_answer, "source": "cache"},
            media_type="application/json; charset=utf-8"
        )

    # 2. Nếu không có trong cache, gọi AI
    answer = ask(req_body.question)
    
    # 3. Lưu kết quả mới vào cache
    save_to_cache(req_body.question, answer)
    
    # 4. Cập nhật chi phí và lấy tổng chi phí mới từ Redis
    estimated_cost = get_estimated_cost(tokens=150)
    new_total_cost = update_total_cost(estimated_cost)
    
    # 5. Trả về kết quả
    return JSONResponse(
        content={
            "answer": answer, 
            "source": "live_ai",
            "cost_info": f"Estimated cost for this request: ${estimated_cost:.4f}. New total cost: ${new_total_cost:.4f}"
        },
        media_type="application/json; charset=utf-8"
    )

if __name__ == "__main__":
    # Tắt reload=False để chạy ở chế độ ổn định, giúp các tính năng
    # như caching và cost guard hoạt động đúng.
    uvicorn.run(app="app.main:app", host="0.0.0.0", port=8001, reload=False)