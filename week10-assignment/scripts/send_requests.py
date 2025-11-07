"""FastAPI 서버에 다수의 요청을 보내는 도우미 스크립트."""

from __future__ import annotations

import asyncio
from typing import Iterable

import httpx


PROMPTS = [
    ("LLMOps가 뭐야?", "v1"),
    ("프롬프트 엔지니어링 팁 알려줘.", "v1"),
    ("한국어 RAG 구축하려면?", "v1"),
    ("LLMOps 파이프라인의 핵심 단계는?", "v2"),
    ("Latency 최적화 전략 소개해줘.", "v2"),
    ("토큰 사용량 모니터링은 어떻게 해?", "v2"),
]


async def send_request(client: httpx.AsyncClient, message: str, version: str) -> None:
    response = await client.post(
        "/chat",
        json={"message": message, "prompt_version": version},
        timeout=60.0,
    )
    response.raise_for_status()
    data = response.json()
    print(f"[{version}] {message} -> {data['reply']} (latency: {data['latency_ms']}ms)")


async def main(
    prompts: Iterable[tuple[str, str]] = PROMPTS,
    base_url: str = "http://localhost:8000",
) -> None:
    async with httpx.AsyncClient(base_url=base_url) as client:
        tasks = [send_request(client, message, version) for message, version in prompts]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

