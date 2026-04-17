# -*- coding: utf-8 -*-
"""
Agent đơn giản để demo Dockerfile cơ bản.
"""
import os
import time

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from utils.mock_llm import ask
from fastapi.responses import JSONResponse

app = FastAPI(title="Agent Basic Docker")
START_TIME = time.time()


# 1. Define the request body model using Pydantic
class QuestionRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"message": "Agent is running in a Docker container!"}


# 2. Update the endpoint to use the Pydantic model
@app.post("/ask")
async def ask_agent(request: QuestionRequest):
    answer = ask(request.question)
    return JSONResponse(content={"answer": answer}, media_type="application/json; charset=utf-8")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "container": True,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app="app:app", host="0.0.0.0", port=port)