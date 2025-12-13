"""
전체 파이프라인 통합 모듈
입력 마스킹 → RAG 검색 → 모델 응답 → 출력 모더레이션 → 비용 계산 → 로깅
"""

import time
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .pii_mask import mask_basic_all
from .moderation import classify_toxicity
from .rag_filter import filter_safe_docs, search_safe_docs
from .tokenizer import count_tokens
from .cost import calculate_cost_metrics


# 정책 거부 메시지
POLICY_REFUSAL = (
    "요청하신 내용은 서비스 정책상 제공할 수 없습니다. "
    "안전한 도움이 필요하시다면 전문가 상담 또는 공식 채널을 이용해 주세요."
)


def dummy_model_response(prompt: str, expected_len: int = 100) -> str:
    """더미 모델 응답을 생성합니다.
    
    실제 LLM 호출 대신 간단한 규칙 기반 응답을 생성
    
    Args:
        prompt: 입력 프롬프트
        expected_len: 예상 응답 길이 (문자 수)
        
    Returns:
        더미 응답 텍스트
    """
    # 특정 키워드에 대해 유해한 응답 시뮬레이션
    harmful_keywords = ['욕', '모욕', '증오', '죽어', '혐오']
    
    if any(word in prompt for word in harmful_keywords):
        return "그건 정말 바보 같은 생각이야. 넌 최악이야. (시뮬레이션된 유해 응답)"
    
    # 일반적인 안전한 응답
    base_response = "여러 관점을 고려해 볼 수 있습니다. "
    
    # expected_len에 맞춰 응답 길이 조정
    while len(base_response) < expected_len:
        base_response += "추가적인 정보를 제공해드리겠습니다. "
    
    return base_response[:expected_len]


def process_request(
    user_text: str,
    expected_completion_len: int = 100,
    rag_corpus: Optional[List[Dict]] = None,
    tox_threshold: float = 0.8,
    price_per_1k: float = 0.002,
    cache_hit_rate: float = 0.0,
    route: str = "/chat"
) -> Dict:
    """요청을 처리하는 전체 파이프라인
    
    Args:
        user_text: 사용자 입력 텍스트
        expected_completion_len: 예상 응답 길이
        rag_corpus: RAG 문서 코퍼스 (선택)
        tox_threshold: 유해성 차단 임계값
        price_per_1k: 1000 토큰당 가격
        cache_hit_rate: 캐시 적중률
        route: API 라우트 (로깅용)
        
    Returns:
        처리 결과 딕셔너리
    """
    t0 = time.time()
    
    # 1) 입력 PII 마스킹
    masked_text, pii_hits = mask_basic_all(user_text)
    
    # 2) RAG 검색 (선택)
    rag_context = ""
    if rag_corpus:
        safe_docs = search_safe_docs(masked_text, rag_corpus, top_k=2)
        if safe_docs:
            rag_context = "\n".join([doc.get('text', '') for doc in safe_docs])
    
    # 3) 프롬프트 구성 (RAG 컨텍스트 포함)
    final_prompt = masked_text
    if rag_context:
        final_prompt = f"[Context]\n{rag_context}\n\n[Query]\n{masked_text}"
    
    # 4) 더미 모델 응답 생성
    raw_response = dummy_model_response(final_prompt, expected_completion_len)
    
    # 5) 출력 모더레이션
    toxicity_score = classify_toxicity(raw_response)
    blocked = toxicity_score >= tox_threshold
    final_response = POLICY_REFUSAL if blocked else raw_response
    
    # 6) 토큰 수 계산
    prompt_tokens = count_tokens(final_prompt)
    completion_tokens = count_tokens(raw_response)
    
    # 7) 비용 계산
    cost_metrics = calculate_cost_metrics(
        prompt_tokens,
        completion_tokens,
        price_per_1k,
        cache_hit_rate
    )
    
    # 8) 지연 시간 계산
    latency_ms = int((time.time() - t0) * 1000)
    
    # 9) 결과 반환
    return {
        'ts': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'route': route,
        'input_raw': user_text,
        'input_masked': masked_text,
        'pii_hits': pii_hits,
        'rag_used': bool(rag_context),
        'raw_response': raw_response,
        'toxicity': toxicity_score,
        'blocked': blocked,
        'final_response': final_response,
        'prompt_tok': prompt_tokens,
        'completion_tok': completion_tokens,
        'price_per_1k': price_per_1k,
        'request_cost': cost_metrics['request_cost'],
        'cached': cache_hit_rate > 0,
        'latency_ms': latency_ms,
    }


def append_log(log_path: Path, result: Dict):
    """결과를 CSV 로그에 추가합니다.
    
    Args:
        log_path: 로그 파일 경로
        result: process_request 결과 딕셔너리
    """
    # CSV 헤더
    header = [
        'ts', 'route', 'prompt_tok', 'completion_tok', 'price_per_1k',
        'request_cost', 'cached', 'latency_ms', 'pii_hits', 'blocked'
    ]
    
    # PII hits를 파이프로 구분된 문자열로 변환
    pii_str = '|'.join(result['pii_hits']) if result['pii_hits'] else ''
    
    row = [
        result['ts'],
        result['route'],
        result['prompt_tok'],
        result['completion_tok'],
        result['price_per_1k'],
        round(result['request_cost'], 6),
        int(result['cached']),
        result['latency_ms'],
        pii_str,
        int(result['blocked']),
    ]
    
    # 파일이 없으면 헤더 작성
    new_file = not log_path.exists()
    
    with open(log_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(header)
        writer.writerow(row)


if __name__ == "__main__":
    # 테스트
    from pathlib import Path
    
    # 테스트용 RAG 코퍼스
    test_corpus = [
        {
            'id': 1,
            'text': 'RAG는 검색 증강 생성(Retrieval-Augmented Generation)의 약자입니다.',
            'safety_label': 'safe',
            'pii_flag': False
        },
        {
            'id': 2,
            'text': '개인정보: 010-1234-5678',
            'safety_label': 'review',
            'pii_flag': True
        },
    ]
    
    # 테스트 케이스
    test_cases = [
        "RAG에 대해 설명해주세요.",
        "제 전화번호는 010-9999-8888입니다. 연락 부탁드려요.",
        "너는 정말 멍청해. 욕하고 싶어.",
    ]
    
    log_path = Path("../logs/test_log.csv")
    log_path.parent.mkdir(exist_ok=True)
    
    for text in test_cases:
        result = process_request(
            text,
            expected_completion_len=80,
            rag_corpus=test_corpus,
            tox_threshold=0.8
        )
        
        print(f"\n[요청] {text}")
        print(f"[PII] {result['pii_hits']}")
        print(f"[차단] {result['blocked']} (toxicity: {result['toxicity']:.2f})")
        print(f"[비용] ${result['request_cost']:.6f}")
        print(f"[지연] {result['latency_ms']}ms")
        
        append_log(log_path, result)
    
    print(f"\n로그 저장: {log_path}")

