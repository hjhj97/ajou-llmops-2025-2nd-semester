# MVG+Cost: Minimal Viable Guard + Cost-Aware LLM Service

**Week 14 Assignment**: 안전 레이어와 비용 추적 기능을 갖춘 간이 LLM 파이프라인 구현

---

## 📋 프로젝트 개요

본 프로젝트는 LLM 서비스의 **안전성(Security & Safety)**과 **비용 효율성(Cost Optimization)**을 동시에 확보하기 위한 Minimal Viable Guard 시스템입니다.

### 주요 기능

- ✅ **3개의 안전 레이어**

  - PII 마스킹 (전화번호, 이메일, 주민번호)
  - 출력 모더레이션 (유해 콘텐츠 차단)
  - RAG 안전 라벨 필터 (안전한 문서만 검색)

- ✅ **비용 추적 및 로깅**

  - 요청당 토큰 수 및 비용 계산
  - CSV 로그 자동 기록
  - 월간 비용 추정 및 시나리오 비교

- ✅ **성능 분석**
  - p50/p95/p99 비용 및 지연 통계
  - 차단율, PII 검출율 분석
  - 비용 절감 잠재력 분석

---

## 🏗 프로젝트 구조

```
week14-assignment/
├─ README.md              # 본 파일
├─ REPORT.md              # 분석 리포트 (1-2페이지)
├─ requirements.txt       # 의존성 패키지
│
├─ src/                   # 핵심 모듈
│  ├─ __init__.py
│  ├─ pii_mask.py         # PII 마스킹 함수
│  ├─ moderation.py       # 출력 모더레이션
│  ├─ rag_filter.py       # RAG 안전 필터
│  ├─ tokenizer.py        # 토큰 카운팅 (tiktoken/폴백)
│  ├─ cost.py             # 비용 계산 유틸
│  └─ pipeline.py         # 전체 파이프라인 통합
│
├─ data/                  # 입력 데이터
│  ├─ prompts.csv         # 테스트 프롬프트 (40건)
│  └─ rag_corpus.jsonl    # RAG 문서 코퍼스 (15개)
│
├─ logs/                  # 실행 로그 (자동 생성)
│  ├─ access_cost_log.csv         # 요청 로그
│  ├─ summary_metrics.json        # 요약 지표
│  └─ scenario_comparison.csv     # 시나리오 비교
│
├─ plots/                 # 시각화 (자동 생성)
│  └─ *.png
│
├─ run_pipeline_simple.py # 파이프라인 실행 스크립트
├─ analyze_simple.py      # 분석 스크립트
└─ analyze.ipynb          # Jupyter 노트북 (선택)
```

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt
```

**최소 요구사항**:

- Python 3.8+
- pandas
- matplotlib (선택, 그래프 생성 시)

**선택 사항**:

- `tiktoken`: 정확한 토큰 카운팅 (없으면 폴백 사용)
- `detoxify`: ML 기반 유해성 판단 (없으면 휴리스틱 사용)

### 2. 파이프라인 실행

```bash
# 전체 파이프라인 실행 (40건 처리)
python run_pipeline_simple.py
```

**출력 예시**:

```
프롬프트 수: 40개
파이프라인 실행 중...
  처리 완료: 10/40
  처리 완료: 20/40
  처리 완료: 30/40
  처리 완료: 40/40

=== 요약 통계 ===
차단된 요청: 2개 (5.0%)
PII 발견: 5개 (12.5%)
총 비용: $0.003078
평균 지연: 0.0ms

로그 저장: logs/access_cost_log.csv
```

### 3. 분석 실행

```bash
# 로그 분석 및 지표 산출
python analyze_simple.py
```

**생성 파일**:

- `logs/summary_metrics.json`: 요약 지표
- `logs/scenario_comparison.csv`: 시나리오별 월간 비용

### 4. 리포트 확인

```bash
# 분석 리포트 읽기
cat REPORT.md
```

---

## 📊 CSV 로그 스키마

### access_cost_log.csv

| 컬럼             | 설명             | 예시                   |
| ---------------- | ---------------- | ---------------------- |
| `ts`             | 타임스탬프 (UTC) | `2024-12-04T12:34:56Z` |
| `route`          | API 라우트       | `/chat`                |
| `prompt_tok`     | 프롬프트 토큰 수 | `42`                   |
| `completion_tok` | 응답 토큰 수     | `80`                   |
| `price_per_1k`   | 1000 토큰당 가격 | `0.002`                |
| `request_cost`   | 요청 비용 (USD)  | `0.000077`             |
| `cached`         | 캐시 사용 여부   | `0` or `1`             |
| `latency_ms`     | 지연 시간 (ms)   | `0`                    |
| `pii_hits`       | 발견된 PII 타입  | `phone\|email`         |
| `blocked`        | 차단 여부        | `0` or `1`             |

---

## 🔒 안전 레이어 상세

### 1. PII 마스킹 (`src/pii_mask.py`)

**지원 패턴**:

- 한국 전화번호: `010-1234-5678` → `010-1234-****`
- 이메일: `user.name@test.com` → `us***@test.com`
- 주민등록번호: `990101-1234567` → `990101-*******`

**사용 예시**:

```python
from src.pii_mask import mask_basic_all

text = "제 전화번호는 010-1234-5678입니다."
masked, hits = mask_basic_all(text)
print(masked)  # "제 전화번호는 010-1234-****입니다."
print(hits)    # ["phone"]
```

### 2. 출력 모더레이션 (`src/moderation.py`)

**동작 방식**:

- `detoxify` 사용 가능 시: ML 기반 유해성 점수 (0~1)
- 미사용 시: 키워드 휴리스틱 (욕설, 자해, 증오 표현 검출)

**차단 기준**: 유해성 점수 ≥ 0.8

**사용 예시**:

```python
from src.moderation import classify_toxicity

text = "안전한 텍스트입니다."
score = classify_toxicity(text)
print(score)  # 0.0

toxic_text = "너는 바보야. 최악이야."
score = classify_toxicity(toxic_text)
print(score)  # 0.4 (휴리스틱) or 더 정확한 값 (detoxify)
```

### 3. RAG 안전 필터 (`src/rag_filter.py`)

**필터링 기준**:

- `safety_label == 'safe'`
- `pii_flag == False`

**사용 예시**:

```python
from src.rag_filter import filter_safe_docs

docs = [
    {"id": 1, "text": "안전한 문서", "safety_label": "safe", "pii_flag": False},
    {"id": 2, "text": "차단 문서", "safety_label": "block", "pii_flag": False},
]

safe_docs = filter_safe_docs(docs)
print(len(safe_docs))  # 1
```

---

## 💰 비용 계산 방식

### 기본 공식

```
request_cost = (prompt_tok + completion_tok) / 1000 * price_per_1k
effective_cost = request_cost * (1 - cache_hit_rate)
monthly_cost = avg_effective_cost * DAILY_REQ * 30
```

---

## 🧪 테스트 데이터

### prompts.csv (40건)

- 정상 질의: 70% (28건)
- PII 포함: 12.5% (5건)
- 유해 응답 유도: 5% (2건)
- 기타: 12.5% (5건)

### rag_corpus.jsonl (15개 문서)

- `safe`: 10개 (검색 가능)
- `block`: 2개 (차단)
- `review`: 3개 (PII 포함, 차단)

---

## 📈 주요 지표

### 안전 지표

- **차단율**: 5.0% (2/40)
- **PII 검출율**: 12.5% (5/40)

### 비용 지표

- **평균 비용**: $0.000077/요청
- **p50 비용**: $0.000082
- **p95 비용**: $0.000112

### 월간 비용 (2000 req/day 기준)

- **기본**: $4.62
- **최적 (캐시 50%)**: $2.31
- **절감 잠재력**: 50%

---

## 🔧 커스터마이징

### 1. 비용 파라미터 변경

`run_pipeline_simple.py` 수정:

```python
result = process_request(
    text,
    expected_len=80,
    price_per_1k=0.003,    # 단가 변경
    cache_hit_rate=0.4,    # 캐시율 변경
)
```

### 2. 안전 임계값 조정

`src/pipeline.py` 수정:

```python
def process_request(
    user_text: str,
    tox_threshold: float = 0.7,  # 기본 0.8 → 0.7로 변경
    ...
):
```

### 3. PII 패턴 추가

`src/pii_mask.py`에 새로운 정규식 추가:

```python
CARD_PAT = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b")

def mask_card(text: str) -> str:
    return CARD_PAT.sub(r"****-****-****-\4", text)
```

---

## 📚 참고 자료

- **Week 13**: Security & Safety Lab (`week13_security_safety_lab.ipynb`)
- **Week 14**: Cost & Autoscale Lab (`week14_cost_autoscale_lab.ipynb`)
- **과제 요구사항**: 본 폴더의 `assignment.md` (별도 제공)
