"""
로그 분석 스크립트 (간소화 버전 - 그래프 없이)
"""

import csv
import json
from pathlib import Path

def main():
    # 로그 파일 읽기
    log_path = Path('logs/access_cost_log.csv')
    print(f"로그 파일 로드: {log_path}\n")
    
    with open(log_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"전체 요청 수: {len(rows)}개\n")
    
    # 데이터 추출
    blocked_list = [int(r['blocked']) for r in rows]
    pii_list = [r['pii_hits'] for r in rows]
    cost_list = [float(r['request_cost']) for r in rows]
    latency_list = [int(r['latency_ms']) for r in rows]
    prompt_tok_list = [int(r['prompt_tok']) for r in rows]
    completion_tok_list = [int(r['completion_tok']) for r in rows]
    
    # 안전 지표
    blocked_count = sum(blocked_list)
    block_rate = blocked_count / len(rows) * 100
    
    pii_count = sum(1 for p in pii_list if p and p.strip())
    pii_rate = pii_count / len(rows) * 100
    
    # 비용 지표
    total_cost = sum(cost_list)
    mean_cost = total_cost / len(cost_list)
    cost_sorted = sorted(cost_list)
    p50_cost = cost_sorted[int(len(cost_sorted) * 0.50)]
    p95_cost = cost_sorted[int(len(cost_sorted) * 0.95)]
    p99_cost = cost_sorted[int(len(cost_sorted) * 0.99)]
    
    # 지연 지표
    mean_latency = sum(latency_list) / len(latency_list)
    latency_sorted = sorted(latency_list)
    p50_latency = latency_sorted[int(len(latency_sorted) * 0.50)]
    p95_latency = latency_sorted[int(len(latency_sorted) * 0.95)]
    
    print("=== 안전 지표 ===")
    print(f"차단된 요청: {blocked_count}개 ({block_rate:.1f}%)")
    print(f"PII 발견: {pii_count}개 ({pii_rate:.1f}%)")
    
    print("\n=== 비용 지표 ===")
    print(f"총 비용: ${total_cost:.6f}")
    print(f"평균 비용: ${mean_cost:.6f}")
    print(f"p50 비용: ${p50_cost:.6f}")
    print(f"p95 비용: ${p95_cost:.6f}")
    print(f"p99 비용: ${p99_cost:.6f}")
    
    print("\n=== 지연 지표 ===")
    print(f"평균 지연: {mean_latency:.2f}ms")
    print(f"p50 지연: {p50_latency:.2f}ms")
    print(f"p95 지연: {p95_latency:.2f}ms")
    
    # 시나리오 분석
    print("\n=== 시나리오 분석 ===")
    DAILY_REQ = 2000
    DAYS_IN_MONTH = 30
    
    scenarios = [
        {"name": "기본 (캐시 0%)", "price": 0.002, "cache": 0.0},
        {"name": "캐시 30%", "price": 0.002, "cache": 0.30},
        {"name": "캐시 50%", "price": 0.002, "cache": 0.50},
        {"name": "저렴한 모델", "price": 0.0015, "cache": 0.0},
        {"name": "저렴한 모델 + 캐시 30%", "price": 0.0015, "cache": 0.30},
    ]
    
    scenario_results = []
    
    print("\n시나리오별 월간 비용 (일 2000건 기준):")
    for scenario in scenarios:
        # 각 요청별 실효 비용 계산
        eff_costs = []
        for i in range(len(rows)):
            total_tokens = prompt_tok_list[i] + completion_tok_list[i]
            raw_cost = (total_tokens / 1000.0) * scenario['price']
            eff_cost = raw_cost * (1 - scenario['cache'])
            eff_costs.append(eff_cost)
        
        avg_eff_cost = sum(eff_costs) / len(eff_costs)
        monthly_cost = avg_eff_cost * DAILY_REQ * DAYS_IN_MONTH
        
        print(f"  {scenario['name']}: ${monthly_cost:.2f}")
        
        scenario_results.append({
            'scenario': scenario['name'],
            'price_per_1k': scenario['price'],
            'cache_rate': scenario['cache'],
            'avg_eff_cost': round(avg_eff_cost, 6),
            'monthly_cost': round(monthly_cost, 2),
        })
    
    # 시나리오 CSV 저장
    with open('logs/scenario_comparison.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['scenario', 'price_per_1k', 'cache_rate', 'avg_eff_cost', 'monthly_cost']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scenario_results)
    
    # 비용 절감 잠재력
    print("\n=== 비용 절감 잠재력 ===")
    base_monthly = scenario_results[0]['monthly_cost']
    best_monthly = min(s['monthly_cost'] for s in scenario_results)
    saving = base_monthly - best_monthly
    saving_pct = (saving / base_monthly) * 100
    
    print(f"기본 시나리오 월간 비용: ${base_monthly:.2f}")
    print(f"최적 시나리오 월간 비용: ${best_monthly:.2f}")
    print(f"절감 가능 금액: ${saving:.2f} ({saving_pct:.1f}%)")
    print(f"연간 절감 가능 금액: ${saving * 12:.2f}")
    
    # 요약 지표 저장
    summary = {
        'total_requests': len(rows),
        'blocked_count': blocked_count,
        'block_rate_pct': round(block_rate, 2),
        'pii_count': pii_count,
        'pii_rate_pct': round(pii_rate, 2),
        'total_cost_usd': round(total_cost, 6),
        'mean_cost_usd': round(mean_cost, 6),
        'p50_cost_usd': round(p50_cost, 6),
        'p95_cost_usd': round(p95_cost, 6),
        'p99_cost_usd': round(p99_cost, 6),
        'mean_latency_ms': round(mean_latency, 2),
        'p50_latency_ms': round(p50_latency, 2),
        'p95_latency_ms': round(p95_latency, 2),
        'base_monthly_cost': round(base_monthly, 2),
        'best_monthly_cost': round(best_monthly, 2),
        'potential_saving': round(saving, 2),
        'saving_pct': round(saving_pct, 1),
    }
    
    with open('logs/summary_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n=== 완료 ===")
    print("  - logs/summary_metrics.json")
    print("  - logs/scenario_comparison.csv")


if __name__ == "__main__":
    main()


