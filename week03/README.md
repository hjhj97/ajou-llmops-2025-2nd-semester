# Week03 - 뉴스 요약 태스크 (News Summary Task)

이 프로젝트는 **뉴스 기사 요약** 태스크를 위한 프롬프트 엔지니어링과 평가 시스템을 구현합니다. Langfuse를 활용한 프롬프트 버전 관리, LLM-as-a-judge 평가, 그리고 데이터셋 기반 성능 측정을 포함합니다.

## 🎯 프로젝트 개요

### 주요 기능

- **뉴스 기사 요약**: 10개의 한국어 뉴스 기사를 입력으로 받아 구조화된 요약 생성
- **프롬프트 버전 관리**: V0.0.1 (간단 요약)과 V0.0.2 (구조화 요약) 두 가지 버전
- **LLM-as-a-judge 평가**: 원문과 요약을 비교하여 0~1 스케일로 품질 평가
- **Langfuse 연동**: 트레이싱, 데이터셋 관리, 평가 결과 저장

### 평가 지표

1. **구조적 완성도** (30% 가중치): 예상 섹션 포함 여부
2. **요약 품질** (70% 가중치): 핵심 정보 보존도, 정확성, 압축도, 객관성
3. **종합 점수**: 구조적 완성도 × 0.3 + 요약 품질 × 0.7

## 📁 프로젝트 구조

```
week03/
├── datasets/
│   ├── news/                    # 뉴스 기사 원본 파일들
│   │   ├── news_01.txt
│   │   ├── news_02.txt
│   │   └── ... (news_10.txt)
│   ├── week03_news_summary_demo.jsonl  # 데이터셋 백업 파일
│   └── week03_meeting_minutes_demo.jsonl
├── prompts/                     # Prompty 파일들
│   ├── meeting_minutes_v0.1.prompty
│   └── meeting_minutes_v0.2.prompty
├── prompt_eval_and_version_news_summary.ipynb  # 메인 노트북
└── README.md                   # 이 파일
```

## 🚀 사용법

### 1. 환경 설정

`.env` 파일에 다음 변수들을 설정하세요:

```env
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
OPENAI_API_KEY=your_openai_api_key
```

### 2. 의존성 설치

```bash
pip install langfuse python-dotenv openai requests
```

### 3. 노트북 실행

`prompt_eval_and_version_news_summary.ipynb` 노트북을 실행하여:

1. **데이터셋 생성**: 10개의 뉴스 기사를 Langfuse 데이터셋으로 업로드
2. **프롬프트 평가**: 두 가지 프롬프트 버전에 대한 자동 평가 실행
3. **결과 확인**: Langfuse 대시보드에서 상세한 평가 결과 확인

### 4. 실행 결과 예시

```
🔍 Evaluating V0.0.1 (Simple Summary)...
Processing item 1/10...
  - Structure: 0.000, Quality: 0.850, Overall: 0.595
Processing item 2/10...
  - Structure: 0.000, Quality: 0.900, Overall: 0.630
...

🔍 Evaluating V0.0.2 (Structured Summary)...
Processing item 1/10...
  - Structure: 1.000, Quality: 0.900, Overall: 0.930
Processing item 2/10...
  - Structure: 1.000, Quality: 0.900, Overall: 0.930
...
```

## 📊 프롬프트 버전 비교

### V0.0.1 - 간단 요약

- **목적**: 핵심 정보만을 간결하게 요약
- **형식**: 120단어 이내의 단일 문단
- **특징**: 5W1H 중심의 사실 전달

### V0.0.2 - 구조화 요약

- **목적**: 체계적이고 읽기 쉬운 구조화된 요약
- **형식**: Markdown 구조 (Headline, Summary, Key Points, Implications, Quotes)
- **특징**: 300단어 이내, 섹션별 정리

## 🔍 평가 시스템

### LLM-as-a-judge 평가 기준

1. **핵심 정보 보존도** (30%): 중요한 사실, 인물, 시간, 장소, 숫자 보존
2. **요약 정확성** (25%): 원문과의 일치성, 왜곡 없음
3. **구조적 완성도** (20%): 논리적 구성, 가독성
4. **정보 압축도** (15%): 핵심만의 효율적 압축
5. **객관성** (10%): 중립적, 객관적 서술

### 성능 지표

- **section_coverage**: 구조적 완성도 점수
- **summary_quality**: LLM 품질 평가 점수
- **overall_score**: 종합 평가 점수

## 📈 결과 분석

Langfuse 대시보드에서 다음을 확인할 수 있습니다:

1. **실행별 성능 비교**: V0.0.1 vs V0.0.2
2. **개별 뉴스 기사별 점수**: 어떤 기사에서 성능 차이가 큰지
3. **평가 지표별 분석**: 구조성 vs 품질 평가 비교
4. **트레이스 상세 정보**: 각 요약 생성 과정과 평가 과정

## 🛠️ 기술 스택

- **Langfuse**: 프롬프트 관리, 트레이싱, 평가
- **OpenAI GPT-4o-mini**: 뉴스 요약 생성 및 품질 평가
- **Jupyter Notebook**: 실험 및 분석 환경
- **Python**: 메인 개발 언어

## 📝 참고사항

- 모든 뉴스 기사는 한국어로 작성됨
- 평가는 한국어 기준으로 수행됨
- 프롬프트는 한국어 출력을 요구함
- 평가 결과는 0.0~1.0 스케일로 정규화됨

## 🔗 관련 링크

- [Langfuse Documentation](https://langfuse.com/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Prompty Format Specification](https://prompty.dev/)

---

**개발자**: LLMOPS 수업 프로젝트  
**업데이트**: 2025년 9월  
**버전**: 1.0.0
