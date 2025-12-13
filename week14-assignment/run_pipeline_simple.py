"""
파이프라인 실행 스크립트 (간소화 버전)
"""

import re
import time
import csv
import json
import math
from datetime import datetime
from pathlib import Path


# === PII 마스킹 ===
PHONE_PAT = re.compile(r"(01[016789]-?\d{3,4}-?)\d{4}")
EMAIL_PAT = re.compile(r"([A-Za-z0-9._%+-]{2})[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")
RRN_PAT = re.compile(r"\b(\d{6})-(\d{7})\b")

def mask_basic_all(text):
    before = text
    after = PHONE_PAT.sub(r"\1****", text)
    after = EMAIL_PAT.sub(r"\1***\2", after)
    after = RRN_PAT.sub(r"\1-*******", after)
    
    hits = []
    if before != after:
        if PHONE_PAT.search(before): hits.append('phone')
        if EMAIL_PAT.search(before): hits.append('email')
        if RRN_PAT.search(before): hits.append('rrn')
    
    return after, hits


# === 모더레이션 ===
BAD_WORDS = ['바보', '멍청', 'idiot', 'stupid', '병신', '개새', '씨발', 'fuck',
             '자해', '죽고', 'kill myself', '자살', '혐오', '증오', 'hate', '죽어', '최악']

def classify_toxicity(text):
    text_l = text.lower()
    score = 0.0
    for w in BAD_WORDS:
        if w.lower() in text_l:
            score += 0.4
    return min(score, 1.0)


# === 토크나이저 (폴백) ===
def count_tokens(text):
    if text is None:
        text = ""
    return max(1, math.ceil(len(text) / 4))


# === 더미 모델 ===
def dummy_model_response(prompt, expected_len=100):
    harmful_keywords = ['욕', '모욕', '증오', '죽어', '혐오']
    
    if any(word in prompt for word in harmful_keywords):
        return "그건 정말 바보 같은 생각이야. 넌 최악이야."
    
    base_response = "여러 관점을 고려해 볼 수 있습니다. "
    while len(base_response) < expected_len:
        base_response += "추가적인 정보를 제공해드리겠습니다. "
    
    return base_response[:expected_len]


# === 파이프라인 ===
def process_request(user_text, expected_len=100):
    t0 = time.time()
    
    # PII 마스킹
    masked_text, pii_hits = mask_basic_all(user_text)
    
    # 더미 응답
    raw_response = dummy_model_response(masked_text, expected_len)
    
    # 모더레이션
    toxicity_score = classify_toxicity(raw_response)
    blocked = toxicity_score >= 0.8
    
    if blocked:
        final_response = "요청하신 내용은 서비스 정책상 제공할 수 없습니다."
    else:
        final_response = raw_response
    
    # 토큰 수 계산
    prompt_tokens = count_tokens(masked_text)
    completion_tokens = count_tokens(raw_response)
    
    # 비용 계산
    price_per_1k = 0.002
    request_cost = (prompt_tokens + completion_tokens) / 1000.0 * price_per_1k
    
    # 지연 시간
    latency_ms = int((time.time() - t0) * 1000)
    
    return {
        'ts': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'route': '/chat',
        'prompt_tok': prompt_tokens,
        'completion_tok': completion_tokens,
        'price_per_1k': price_per_1k,
        'request_cost': request_cost,
        'cached': 0,
        'latency_ms': latency_ms,
        'pii_hits': '|'.join(pii_hits) if pii_hits else '',
        'blocked': int(blocked),
    }


# === 메인 ===
def main():
    base_dir = Path(__file__).parent
    
    # 데이터 로드
    prompts_path = base_dir / "data" / "prompts.csv"
    log_path = base_dir / "logs" / "access_cost_log.csv"
    
    log_path.parent.mkdir(exist_ok=True)
    
    # 기존 로그 삭제
    if log_path.exists():
        log_path.unlink()
    
    print(f"프롬프트 파일: {prompts_path}")
    
    # CSV 읽기
    prompts = []
    with open(prompts_path, 'r', encoding='utf-8') as f:
        import csv
        reader = csv.DictReader(f)
        for row in reader:
            prompts.append({
                'id': int(row['id']),
                'prompt': row['prompt'],
                'expected_len': int(row['expected_completion_len'])
            })
    
    print(f"프롬프트 수: {len(prompts)}개")
    
    # 파이프라인 실행
    print("\n파이프라인 실행 중...")
    results = []
    
    # 로그 파일 헤더 작성
    header = ['ts', 'route', 'prompt_tok', 'completion_tok', 'price_per_1k',
              'request_cost', 'cached', 'latency_ms', 'pii_hits', 'blocked']
    
    with open(log_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        
        for i, p in enumerate(prompts):
            result = process_request(p['prompt'], p['expected_len'])
            writer.writerow(result)
            results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"  처리 완료: {i + 1}/{len(prompts)}")
    
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

