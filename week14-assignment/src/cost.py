"""
비용 계산 모듈
토큰 수를 기반으로 요청 비용을 계산합니다.
"""

from typing import Dict


def calculate_cost(
    prompt_tok: int,
    completion_tok: int,
    price_per_1k: float = 0.002
) -> float:
    """요청당 비용을 계산합니다.
    
    Args:
        prompt_tok: 프롬프트 토큰 수
        completion_tok: 완성(응답) 토큰 수
        price_per_1k: 1000 토큰당 가격 (USD)
        
    Returns:
        요청 비용 (USD)
    """
    total_tokens = prompt_tok + completion_tok
    return (total_tokens / 1000.0) * price_per_1k


def calculate_effective_cost(
    request_cost: float,
    cache_hit_rate: float = 0.0
) -> float:
    """캐시를 고려한 실효 비용을 계산합니다.
    
    Args:
        request_cost: 원래 요청 비용
        cache_hit_rate: 캐시 적중률 (0.0 ~ 1.0)
        
    Returns:
        실효 비용 (USD)
    """
    return request_cost * (1 - cache_hit_rate)


def estimate_monthly_cost(
    avg_request_cost: float,
    daily_requests: int,
    days_in_month: int = 30
) -> float:
    """월간 비용을 추정합니다.
    
    Args:
        avg_request_cost: 평균 요청당 비용 (USD)
        daily_requests: 일일 요청 수
        days_in_month: 월 일수 (기본 30일)
        
    Returns:
        월간 총 비용 (USD)
    """
    daily_cost = avg_request_cost * daily_requests
    return daily_cost * days_in_month


def calculate_cost_metrics(
    prompt_tok: int,
    completion_tok: int,
    price_per_1k: float = 0.002,
    cache_hit_rate: float = 0.0
) -> Dict[str, float]:
    """토큰 수로부터 모든 비용 지표를 계산합니다.
    
    Args:
        prompt_tok: 프롬프트 토큰 수
        completion_tok: 완성 토큰 수
        price_per_1k: 1000 토큰당 가격
        cache_hit_rate: 캐시 적중률
        
    Returns:
        비용 지표 딕셔너리
    """
    request_cost = calculate_cost(prompt_tok, completion_tok, price_per_1k)
    eff_cost = calculate_effective_cost(request_cost, cache_hit_rate)
    
    return {
        'request_cost': request_cost,
        'effective_cost': eff_cost,
        'total_tokens': prompt_tok + completion_tok,
        'prompt_tokens': prompt_tok,
        'completion_tokens': completion_tok,
    }


if __name__ == "__main__":
    # 테스트
    prompt_tok = 100
    completion_tok = 50
    price = 0.002
    cache_rate = 0.30
    
    metrics = calculate_cost_metrics(prompt_tok, completion_tok, price, cache_rate)
    print("비용 지표:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.6f}")
    
    monthly = estimate_monthly_cost(metrics['effective_cost'], 2000, 30)
    print(f"\n월간 예상 비용 (2000 req/day): ${monthly:.2f}")

