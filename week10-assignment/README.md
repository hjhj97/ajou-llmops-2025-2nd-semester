# Week10 Mini Chatbot API & LLMOps

이 리포지토리는 FastAPI 기반 LLM 챗봇 API와 호출 로그 분석을 위한 예제 프로젝트입니다. 9주차(서빙)와 10주차(로깅/분석) 핵심 내용을 한 번에 연습할 수 있도록 구성했습니다.

## 1. 프로젝트 구조

- `app/`
  - `main.py`: FastAPI 엔트리포인트 및 엔드포인트 정의
  - `schemas.py`: 요청/응답 Pydantic 모델
  - `llm_client.py`: OpenAI(or mock) LLM 호출 클라이언트
  - `logger.py`: CSV 기반 LLM 호출 로깅 유틸리티
- `logs/llm_responses.csv`: 샘플 호출 로그(직접 사용 시 자동 생성 및 append)
- `scripts/`
  - `send_requests.py`: 서버에 요청을 보내 로그를 쌓는 도우미 스크립트
  - `analyze_logs.py`: 축적된 로그로 간단한 통계를 계산
- `REPORT.md`: 과제 요약 및 실험 결과
- `requirements.txt`: 실행에 필요한 의존성 목록

## 2. 사전 준비

1. **의존성 설치**
   ```bash
   pip install -r week10-assignment/requirements.txt
   ```

2. **환경 변수 설정(선택)**
   - `.env` 파일 또는 쉘에서 `OPENAI_API_KEY`를 설정하면 실제 OpenAI API를 사용합니다.
   - 키가 없으면 자동으로 mock 모드가 동작하며, `USE_MOCK_LLM=true`로 강제 mock도 가능합니다.

## 3. 서버 실행

```bash
uvicorn week10-assignment.app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 정상 실행되면 `http://localhost:8000/docs`에서 Swagger UI를 확인할 수 있습니다.

## 4. API 사용 예시

- **Health Check**
  ```bash
  curl http://localhost:8000/health
  ```

- **챗봇 요청**
  ```bash
  curl -X POST "http://localhost:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"LLMOps가 뭐야?","prompt_version":"v1"}'
  ```

응답 예시:

```json
{
  "reply": "[간단 응답] 질문 'LLMOps가 뭐야?'에 대해 자세한 답변을 제공할 준비가 되어 있습니다.",
  "model": "mock-llm",
  "latency_ms": 123,
  "prompt_version": "v1"
}
```

## 5. 로그 수집 & 테스트 자동화

`scripts/send_requests.py`는 다양한 프롬프트 버전을 한 번에 호출해 로그를 쌓는 예제입니다.

```bash
python week10-assignment/scripts/send_requests.py
```

실행 시 6개의 요청을 병렬로 보내고, 결과는 `logs/llm_responses.csv`에 누적됩니다.

## 6. 로그 분석

`analyze_logs.py`로 간단한 통계(프롬프트 버전별/모델별 평균 지연시간 및 토큰 수)를 출력할 수 있습니다.

```bash
python week10-assignment/scripts/analyze_logs.py --log-path week10-assignment/logs/llm_responses.csv
```

샘플 출력:

```
=== 프롬프트 버전별 통계 ===
              호출수  평균지연_ms  평균토큰수
prompt_version
v1                3     411.67      80.00
v2                3     521.00     102.67

=== 모델별 통계 ===
          호출수  평균지연_ms  평균토큰수
model
mock-llm      6     466.33      91.33
```

## 7. 트러블슈팅

- Postman에서 `422 Unprocessable Content`가 발생하면 Body 탭에서 **raw + JSON** 형식을 선택했는지 확인하세요.
- OpenAI Key 사용 시 속도가 느리거나 에러가 나면 키 값과 인터넷 연결을 점검하세요.

## 8. 확장 아이디어

- Langfuse 같은 Observability 플랫폼 연동
- 프롬프트 버전 관리 및 A/B 테스트 자동화
- 토큰 사용량, 지연시간에 대한 알람/모니터링 대시보드 구축

---
