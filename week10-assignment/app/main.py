"""FastAPI 기반 Mini Chatbot API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import logger
from .llm_client import LLMClient, LLMResult, create_llm_client
from .schemas import ChatRequest, ChatResponse


app = FastAPI(
    title="Week10 Mini Chatbot API",
    description="FastAPI + LLMOps 과제를 위한 챗봇 엔드포인트",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_llm_client() -> LLMClient:
    if not hasattr(app.state, "llm_client"):
        app.state.llm_client = create_llm_client()
    return app.state.llm_client


LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, llm_client: LLMClientDep) -> ChatResponse:
    result: LLMResult = llm_client.generate(payload.message, payload.prompt_version)

    timestamp = datetime.now(timezone.utc).isoformat()
    logger.log_llm_call(
        {
            "timestamp": timestamp,
            "prompt": payload.message,
            "prompt_version": payload.prompt_version,
            "model": result.model,
            "latency_ms": str(result.latency_ms),
            "total_tokens": str(result.total_tokens or ""),
        }
    )

    return ChatResponse(
        reply=result.reply,
        model=result.model,
        latency_ms=result.latency_ms,
        prompt_version=payload.prompt_version,
    )


__all__ = ["app"]

