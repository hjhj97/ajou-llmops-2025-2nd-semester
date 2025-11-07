# Week10 Mini Chatbot & LLMOps 요약

## API 개요
- **엔드포인트**: `POST /chat`
- **요청 스키마**: `{ "message": str, "prompt_version": str }`
- **응답 스키마**: `{ "reply": str, "model": str, "latency_ms": int, "prompt_version": str }`
- **헬스체크**: `GET /health`
- **서버 실행**: `uvicorn week10-assignment.app.main:app --reload`

## 구현 상세
- FastAPI 기반 챗봇 API (모듈: `app/main.py`)
- OpenAI Chat Completions 기반 LLM 호출(환경에 따라 mock 모드 동작, `app/llm_client.py`)
- 호출 로그를 CSV(`logs/llm_responses.csv`)에 저장 (`app/logger.py`)
- 분석 스크립트: `scripts/analyze_logs.py`

## 실험 설정
- **프롬프트 버전**: `v1`(간단 응답), `v2`(분석형 응답)
- **사용 모델**: `mock-llm` (OpenAI API Key 미설정 시 자동)
- **총 호출 수**: 6회 (각 버전 3회)

## 결과 요약 (CSV 기반)
- `v1` 평균 지연시간: **411.67 ms**, 평균 토큰 수: **80.0**
- `v2` 평균 지연시간: **521.0 ms**, 평균 토큰 수: **102.67**
- 모델별 평균 지연시간: mock-llm **466.33 ms**
- 모델별 평균 토큰 수: mock-llm **91.33**

## 재현 방법
1. 필요한 패키지 설치: `pip install -r week10-assignment/requirements.txt`
2. OpenAI 키 설정(선택): `.env` 파일 생성 후 `OPENAI_API_KEY=...`
3. 서버 실행: `uvicorn week10-assignment.app.main:app --reload`
4. 예시 요청:
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message":"LLMOps가 뭐야?","prompt_version":"v1"}'
   ```
5. 로그 분석: `python week10-assignment/scripts/analyze_logs.py`

## 향후 개선 아이디어
- Langfuse 등 외부 Observability 연동
- Prompt 버전 관리 및 A/B 테스트 자동화
- 토큰 사용량 기준 경고 시스템 도입

