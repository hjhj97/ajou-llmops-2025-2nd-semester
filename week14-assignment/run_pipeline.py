"""
파이프라인 실행 스크립트
prompts.csv의 모든 요청을 처리하고 로그를 생성합니다.
"""

import sys
from pathlib import Path
import pandas as pd

# src 모듈 임포트를 위한 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import process_request, append_log
from src.rag_filter import load_rag_corpus


def main():
    """메인 실행 함수"""
    # 경로 설정
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    logs_dir = base_dir / "logs"
    
    prompts_path = data_dir / "prompts.csv"
    corpus_path = data_dir / "rag_corpus.jsonl"
    log_path = logs_dir / "access_cost_log.csv"
    
    # 로그 디렉토리 생성
    logs_dir.mkdir(exist_ok=True)
    
    # 기존 로그 파일 삭제 (새로 생성)
    if log_path.exists():
        log_path.unlink()
        print(f"기존 로그 파일 삭제: {log_path}")
    
    # 데이터 로드
    print(f"\n데이터 로딩...")
    df = pd.read_csv(prompts_path)
    print(f"프롬프트 수: {len(df)}개")
    
    rag_corpus = load_rag_corpus(corpus_path)
    print(f"RAG 문서 수: {len(rag_corpus)}개")
    
    # 파이프라인 실행
    print(f"\n파이프라인 실행 중...")
    results = []
    
    for idx, row in df.iterrows():
        prompt_id = row['id']
        prompt = row['prompt']
        expected_len = int(row['expected_completion_len'])
        
        # 요청 처리
        result = process_request(
            user_text=prompt,
            expected_completion_len=expected_len,
            rag_corpus=rag_corpus,
            tox_threshold=0.8,
            price_per_1k=0.002,
            cache_hit_rate=0.0,  # 첫 실행은 캐시 없음
            route="/chat"
        )
        
        # 로그 저장
        append_log(log_path, result)
        results.append(result)
        
        # 진행상황 표시
        if (idx + 1) % 10 == 0:
            print(f"  처리 완료: {idx + 1}/{len(df)}")
    
    print(f"\n완료! 총 {len(results)}개 요청 처리")
    
    # 요약 통계
    blocked_count = sum(1 for r in results if r['blocked'])
    pii_count = sum(1 for r in results if r['pii_hits'])
    total_cost = sum(r['request_cost'] for r in results)
    avg_latency = sum(r['latency_ms'] for r in results) / len(results)
    
    print(f"\n=== 요약 통계 ===")
    print(f"차단된 요청: {blocked_count}개 ({blocked_count/len(results)*100:.1f}%)")
    print(f"PII 발견: {pii_count}개 ({pii_count/len(results)*100:.1f}%)")
    print(f"총 비용: ${total_cost:.6f}")
    print(f"평균 지연: {avg_latency:.1f}ms")
    print(f"\n로그 저장: {log_path}")


if __name__ == "__main__":
    main()

