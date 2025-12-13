"""
RAG 안전 라벨 필터 모듈
문서 메타데이터의 안전 라벨과 PII 플래그를 기반으로 필터링합니다.
"""

from typing import List, Dict


def filter_safe_docs(docs: List[Dict]) -> List[Dict]:
    """안전한 문서만 필터링합니다.
    
    safety_label='safe'이고 pii_flag=False인 문서만 반환
    
    Args:
        docs: 문서 리스트 (각 문서는 dict)
              필수 필드: safety_label, pii_flag
    
    Returns:
        필터링된 안전한 문서 리스트
    """
    safe_docs = []
    
    for doc in docs:
        safety_label = doc.get('safety_label', 'unknown')
        pii_flag = doc.get('pii_flag', True)  # 기본값은 안전하지 않다고 가정
        
        # safety_label이 'safe'이고 pii_flag가 False인 경우만 포함
        if safety_label == 'safe' and not pii_flag:
            safe_docs.append(doc)
    
    return safe_docs


def load_rag_corpus(filepath: str) -> List[Dict]:
    """JSONL 파일에서 RAG 문서를 로드합니다.
    
    Args:
        filepath: JSONL 파일 경로
        
    Returns:
        문서 리스트
    """
    import json
    docs = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    docs.append(json.loads(line))
    except FileNotFoundError:
        print(f"[rag_filter] 파일을 찾을 수 없습니다: {filepath}")
        return []
    
    return docs


def search_safe_docs(query: str, corpus: List[Dict], top_k: int = 3) -> List[Dict]:
    """쿼리에 대해 안전한 문서를 검색합니다.
    
    간단한 키워드 매칭 기반 검색 (실제로는 벡터 검색 등 사용)
    
    Args:
        query: 검색 쿼리
        corpus: 전체 문서 코퍼스
        top_k: 반환할 문서 수
        
    Returns:
        검색된 안전한 문서 리스트
    """
    # 먼저 안전한 문서만 필터링
    safe_corpus = filter_safe_docs(corpus)
    
    if not safe_corpus:
        return []
    
    # 간단한 키워드 매칭 (실제로는 더 정교한 방법 사용)
    query_lower = query.lower()
    scored_docs = []
    
    for doc in safe_corpus:
        text = doc.get('text', '')
        score = 0
        
        # 단순 키워드 포함 여부로 점수 계산
        for word in query_lower.split():
            if word in text.lower():
                score += 1
        
        scored_docs.append((score, doc))
    
    # 점수 기준 정렬 후 상위 k개 반환
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_k]]


if __name__ == "__main__":
    # 테스트
    test_docs = [
        {
            'id': 1,
            'text': 'RAG는 검색과 생성을 결합한 구조입니다.',
            'safety_label': 'safe',
            'pii_flag': False
        },
        {
            'id': 2,
            'text': '이 문서는 혐오 표현을 포함합니다.',
            'safety_label': 'block',
            'pii_flag': False
        },
        {
            'id': 3,
            'text': '연락처는 010-9999-8888 입니다.',
            'safety_label': 'review',
            'pii_flag': True
        },
    ]
    
    safe_docs = filter_safe_docs(test_docs)
    print(f"전체 문서: {len(test_docs)}개")
    print(f"안전한 문서: {len(safe_docs)}개")
    print(f"안전한 문서 ID: {[d['id'] for d in safe_docs]}")

