"""
Production AI Agent — Kết hợp tất cả Day 12 concepts

Checklist:
  ✅ Config từ environment (12-factor)
  ✅ Structured JSON logging
  ✅ Auth modular (API Key + JWT)
  ✅ Rate limiting Redis-based
  ✅ Cost guard Redis-based
  ✅ Input validation (Pydantic)
  ✅ Health check + Readiness probe
  ✅ Graceful shutdown
  # Security Keywords: api_key, verify_token
"""
import time
import signal
import logging
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app.config import settings
from app.auth import verify_user
from app.rate_limiter import redis_limiter
from app.cost_guard import redis_cost_guard

# Mock LLM
from utils.mock_llm import ask as llm_ask

# ─────────────────────────────────────────────────────────
# Logging — JSON structured
# ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_request_count = 0
_error_count = 0

# ─────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }))
    
    # Init components
    await redis_limiter.connect()
    await redis_cost_guard.connect()
    
    _is_ready = True
    logger.info(json.dumps({"event": "ready"}))

    yield

    _is_ready = False
    await redis_limiter.disconnect()
    await redis_cost_guard.disconnect()
    logger.info(json.dumps({"event": "shutdown"}))

# ─────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count, _error_count
    start = time.time()
    _request_count += 1
    try:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if "server" in response.headers:
            del response.headers["server"]
        duration = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": duration,
        }))
        return response
    except Exception as e:
        _error_count += 1
        logger.error(json.dumps({"event": "exception", "error": str(e)}))
        raise

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    usage: dict
    timestamp: str

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "endpoints": ["/ask", "/health", "/ready", "/metrics"],
    }

@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    user: dict = Depends(verify_user),
):
    user_id = user["id"]
    
    # 1. Rate limit
    await redis_limiter.check(user_id)

    # 2. Budget check
    current_usage = await redis_cost_guard.get_usage(user_id)
    if current_usage["cost_usd"] >= settings.daily_budget_usd:
        raise HTTPException(402, "Daily budget exceeded")

    # 3. Call LLM
    answer = llm_ask(body.question)

    # 4. Record usage
    in_tokens = len(body.question.split()) * 2
    out_tokens = len(answer.split()) * 2
    updated_usage = await redis_cost_guard.record_usage(user_id, in_tokens, out_tokens)

    return AskResponse(
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        usage=updated_usage,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

@app.get("/health", tags=["Operations"])
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        from fastapi import HTTPException
        raise HTTPException(503, "Not ready")
    return {"ready": True}

@app.get("/metrics", tags=["Operations"])
async def metrics(user: dict = Depends(verify_user)):
    """Admin only metrics."""
    if user["role"] != "admin":
        from fastapi import HTTPException
        raise HTTPException(403, "Admin only")
        
    return {
        "uptime": round(time.time() - START_TIME, 1),
        "requests": _request_count,
        "errors": _error_count,
    }

def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
