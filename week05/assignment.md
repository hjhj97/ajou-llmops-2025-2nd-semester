1. 과제 목표(Why & What)
   핵심 목표: 4–5주차 핵심을 한 번에 체득
   Retrieval 비교: Dense(벡터) vs BM25(키워드) vs Hybrid(융합) vs Hybrid+Re-rank(CE)
   품질 향상 체감: 하이브리드/재순위화가 정답 포함률·상위정밀도를 어떻게 끌어올리는지 수치로 확인
   근거 중심 출력: 최종 답에 근거 스니펫·출처를 함께 표시
   데이터셋(오픈소스, 한국어 권장):
   기본: KorQuAD 2.0 미니셋(문서 500–2,000청크 규모)
   대체 가능: 공개 한국어 코퍼스(법률/금융/행정 등) — 저작권/배포 조건 준수
   도구 스택(무료/오픈 권장):
   Vector DB: Pinecone(프로젝트 멤버 초대로 강사 접근 가능)
   임베딩: BGE-M3(dense+sparse 동시 산출) 또는 multilingual-E5
   BM25: rank-bm25(또는 bm25s)
   리랭커(CE): Jina Reranker v2 Base Multilingual(대안: Cohere Rerank)
2. 수행 내용(How)
   한 개 노트북(rag_assignment.ipynb)로 진행해도 되고, 아래 3개로 나눠도 됩니다.

환경변수: PINECONE_API_KEY, PINECONE_ENV

2.1 데이터 준비(청크·메타)
원본 로드 → 문단/섹션 기반 + 슬라이딩 윈도우 청크
표/리스트/조문 구조 보존(헤더·캡션·셀 라벨 포함)
메타 필드 추가: language=ko, source/url, revision_date(또는 수집일), doc_id, title, section
2.2 임베딩 & 인덱싱(Pinecone)
임베딩(BGE-M3 또는 mE5) → Pinecone 인덱스 생성(metric: cosine/inner-product) → upsert(batch)
Pinecone 콘솔에서 강사 이메일 프로젝트 멤버 초대(필수)
2.3 4가지 검색 조건 구현
Dense 전용: Pinecone top-k
BM25 전용: rank-bm25 색인 후 top-k
Hybrid(융합):
RRF(순위 역수합) 또는 가중합(score = α·dense + (1−α)·bm25, 정규화 필요)
α 프리셋 예: 정확 용어형(α↓) / 의미 확장형(α↑)
Hybrid + Re-rank:
Top-N=100 후보를 Cross-Encoder로 재점수 → Top-k=5~10 확정
문서-청크 중복 제어(문서당 상위 n개 제한) 적용
2.4 평가 & 시각화
평가 쿼리셋(20–50개) 고정
지표: Recall@5/10, MRR@10, NDCG@10, Latency P50/P95
그래프: 4조건(Dense/BM25/Hybrid/Hybrid+Re-rank) 전/후 비교 바/라인 차트
근거 표출: 선택된 Top-k의 스니펫 하이라이트 + 출처(URL/문서ID/개정일)
권장 시작값: Top-N=100 → Top-k=5~10, RRF 기본 k(완화 상수) 60~100, 가중합 α=0.5에서 시작 후 튜닝

3. 제출물·평가(Deliverables & Rubric)
   3.1 제출물(필수)
   코드 노트북:
   단일 rag_assignment.ipynb 또는 아래 3분할
   01_ingest.ipynb(청크/메타)
   02_index_pinecone.ipynb(임베딩/인덱스)
   03_search_eval.ipynb(4조건 구현·리랭크·평가·그래프)
   데이터/설정: 전처리 코퍼스(corpus_chunks.parquet), configs/models.yaml(모델명/파라미터)
   결과물:
   results/metrics.csv(조건×지표)
   results/plots/(전/후 그래프)
   results/qual_examples.md(성공/실패 사례 ≥5, 원인·개선 포인트 포함)
   리포트(PDF, 5–8p):
   데이터/청크·메타 설계, 모델 선택 근거, 하이브리드(α/RRF)·리랭크(N/k) 설계,
   지표/그래프 요약, 오류 분석(약어/표/버전), 개선안(필드 가중·메타 필터·중복 제어)
   Pinecone 초대 증빙: 프로젝트 멤버 초대 스크린샷(강사 이메일/권한 표시)
   3.2 평가 루브릭(100점)
   검색 품질(35): Dense→BM25→Hybrid→Hybrid+Re-rank 개선 폭(Recall/NDCG/MRR)
   설계 타당성(25): α/RRF 근거, N/k 설정, 중복 제어, 청크/메타/필터 합리성
   운영성(15): Pinecone 공유/권한, 인덱스/캐시/지연 인사이트, 폴백 고려
   근거성(15): 스니펫 하이라이트 + 출처/개정일 일관 제시
   리포트 완성도(10): 명료한 구조, 그래프·표 품질, 실패 원인/개선안의 구체성
   최종 체크리스트(간단):

[ ] Pinecone 인덱스/초대 완료 (강사 아주대 이메일)

[ ] 4개 조건 구현

[ ] RRF/가중합 명시

[ ] CE 리랭크(N/k)

[ ] 지표·그래프

[ ] 근거/출처

[ ] 오류 분석

[ ] PDF/CSV/플롯 제출
