"""Pydantic 모델 정의."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 입력 메시지")
    prompt_version: str = Field(..., description="프롬프트 버전 식별자")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="LLM 응답 텍스트")
    model: str = Field(..., description="사용된 LLM 모델명")
    latency_ms: int = Field(..., description="응답까지 걸린 시간(ms)")
    prompt_version: str = Field(..., description="처리된 프롬프트 버전")

