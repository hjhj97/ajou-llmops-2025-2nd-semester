"""LLM 호출 유틸리티 모듈."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from dotenv import load_dotenv


try:
    from openai import OpenAI  # type: ignore
except ImportError:  # pragma: no cover - optional 의존성
    OpenAI = None  # type: ignore


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM_PROMPT = (
    "당신은 친절한 한국어 AI 어시스턴트입니다. 질문에 간결하고 정확하게 답변하세요."
)

load_dotenv()


@dataclass
class LLMResult:
    reply: str
    model: str
    latency_ms: int
    total_tokens: Optional[int]


class LLMClient:
    """OpenAI 기반 LLM 호출 래퍼.

    OPENAI_API_KEY가 없으면 간단한 mock 응답을 반환하도록 동작한다.
    """

    def __init__(self, model: str = DEFAULT_MODEL, use_mock: Optional[bool] = None) -> None:
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self._use_mock = use_mock if use_mock is not None else not bool(self.api_key)
        self._client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    @property
    def is_mock(self) -> bool:
        return self._use_mock or self._client is None

    def generate(self, message: str, prompt_version: str) -> LLMResult:
        start = time.perf_counter()

        if not self.is_mock:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"[프롬프트 버전: {prompt_version}]\n"
                            f"사용자 질문: {message}"
                        ),
                    },
                ],
            )

            latency_ms = int((time.perf_counter() - start) * 1000)
            choice = response.choices[0]
            reply = choice.message.content or ""
            total_tokens = getattr(response, "usage", None)
            token_count = getattr(total_tokens, "total_tokens", None)

            return LLMResult(
                reply=reply.strip(),
                model=self.model,
                latency_ms=latency_ms,
                total_tokens=token_count,
            )

        # Mock 동작 (LLM 호출 불가 환경 대비)
        simulated_reply = self._build_mock_reply(message, prompt_version)
        latency_ms = int((time.perf_counter() - start) * 1000)
        token_estimate = len(simulated_reply.split()) + len(message.split())

        return LLMResult(
            reply=simulated_reply,
            model="mock-llm",  # 실제 모델명 대신 표시
            latency_ms=max(latency_ms, 10),
            total_tokens=token_estimate,
        )

    def _build_mock_reply(self, message: str, prompt_version: str) -> str:
        if prompt_version == "v2":
            prefix = "[분석적 설명]"
        else:
            prefix = "[간단 응답]"

        return f"{prefix} 질문 '{message}'에 대해 자세한 답변을 제공할 준비가 되어 있습니다."


def create_llm_client() -> LLMClient:
    use_mock_env = os.getenv("USE_MOCK_LLM")
    use_mock = use_mock_env.lower() == "true" if use_mock_env else None
    return LLMClient(model=DEFAULT_MODEL, use_mock=use_mock)

