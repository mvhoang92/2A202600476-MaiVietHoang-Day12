"""
Production AI Agent — Final Lab Day 12
"""
import time
import logging
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit, redis_client
from app.cost_guard import check_and_record_cost

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
    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))

# ─────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    global _request_count
    start = time.time()
    _request_count += 1
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(json.dumps({
        "event": "request",
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "ms": duration,
    }))
    return response

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class AskResponse(BaseModel):
    question: str
    answer: str
    source: str  # Added to show cache status
    timestamp: str

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.post("/ask", response_model=AskResponse)
async def ask_agent(
    body: AskRequest,
    _key: str = Depends(verify_api_key),
):
    # 1. Rate Limiting
    check_rate_limit(_key[:8])

    # 2. Caching (check Redis)
    cache_key = f"cache:v1:{body.question}"
    if redis_client:
        try:
            cached_answer = redis_client.get(cache_key)
            if cached_answer:
                return AskResponse(
                    question=body.question,
                    answer=cached_answer,
                    source="cache",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
        except Exception as e:
            logger.error(f"Cache error: {e}")

    # 3. Budget Check & LLM Call
    input_tokens = len(body.question.split()) * 2
    check_and_record_cost(input_tokens, 0)
    
    answer = llm_ask(body.question)
    
    output_tokens = len(answer.split()) * 2
    check_and_record_cost(0, output_tokens)

    # 4. Save to Cache
    if redis_client:
        try:
            redis_client.setex(cache_key, 3600, answer) # 1 hour TTL
        except Exception as e:
            logger.error(f"Failed to set cache: {e}")

    return AskResponse(
        question=body.question,
        answer=answer,
        source="live_llm",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

@app.get("/health")
def health():
    return {"status": "ok", "uptime_sec": round(time.time() - START_TIME, 1)}

@app.get("/ready")
def ready():
    if not _is_ready:
        from fastapi import HTTPException
        raise HTTPException(503, "Not ready")
    return {"status": "ready"}
