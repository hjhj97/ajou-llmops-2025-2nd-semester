"""
로그 분석 스크립트
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI 없이 실행
import matplotlib.pyplot as plt
import json
from pathlib import Path

# 한글 폰트 설정
try:
    plt.rcParams['font.family'] = 'AppleGothic'
except:
    pass
plt.rcParams['axes.unicode_minus'] = False

def main():
    # 경로 설정
    log_path = Path('logs/access_cost_log.csv')
    plots_dir = Path('plots')
    plots_dir.mkdir(exist_ok=True)
    
    # 데이터 로드
    print(f"로그 파일 로드: {log_path}")
    df = pd.read_csv(log_path)
    print(f"전체 요청 수: {len(df)}개\n")
    
    # === 기본 통계 ===
    blocked_count = df['blocked'].sum()
    block_rate = blocked_count / len(df) * 100
    
    pii_count = (df['pii_hits'].fillna('') != '').sum()
    pii_rate = pii_count / len(df) * 100
    
    total_cost = df['request_cost'].sum()
    mean_cost = df['request_cost'].mean()
    p50_cost = df['request_cost'].quantile(0.50)
    p95_cost = df['request_cost'].quantile(0.95)
    p99_cost = df['request_cost'].quantile(0.99)
    
    mean_latency = df['latency_ms'].mean()
    p50_latency = df['latency_ms'].quantile(0.50)
    p95_latency = df['latency_ms'].quantile(0.95)
    
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
    
    # === 시각화 ===
    print("\n=== 그래프 생성 중 ===")
    
    # 1) 차단율 바 차트
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ['허용', '차단']
    counts = [len(df) - blocked_count, blocked_count]
    colors = ['#2ecc71', '#e74c3c']
    ax.bar(categories, counts, color=colors)
    ax.set_ylabel('요청 수')
    ax.set_title('요청 차단 현황')
    for i, v in enumerate(counts):
        ax.text(i, v + 0.5, str(int(v)), ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(plots_dir / 'blocked_status.png', dpi=150)
    plt.close()
    print("  - blocked_status.png 저장")
    
    # 2) 비용 분포 히스토그램
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df['request_cost'], bins=20, edgecolor='black', alpha=0.7)
    ax.axvline(mean_cost, color='red', linestyle='--', label=f'평균: ${mean_cost:.6f}')
    ax.axvline(p50_cost, color='blue', linestyle='--', label=f'p50: ${p50_cost:.6f}')
    ax.axvline(p95_cost, color='orange', linestyle='--', label=f'p95: ${p95_cost:.6f}')
    ax.set_xlabel('요청당 비용 (USD)')
    ax.set_ylabel('빈도')
    ax.set_title('요청당 비용 분포')
    ax.legend()
    plt.tight_layout()
    plt.savefig(plots_dir / 'cost_distribution.png', dpi=150)
    plt.close()
    print("  - cost_distribution.png 저장")
    
    # 3) Top-10 비용이 높은 요청
    top10 = df.nlargest(10, 'request_cost').reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(range(len(top10)), top10['request_cost'])
    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels([f"요청 {i+1}" for i in range(len(top10))])
    ax.set_xlabel('비용 (USD)')
    ax.set_title('Top-10 비용이 높은 요청')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(plots_dir / 'top10_expensive.png', dpi=150)
    plt.close()
    print("  - top10_expensive.png 저장")
    
    # === 시나리오 비교 ===
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
    
    results = []
    for scenario in scenarios:
        total_tokens = df['prompt_tok'] + df['completion_tok']
        raw_cost = (total_tokens / 1000.0) * scenario['price']
        eff_cost = raw_cost * (1 - scenario['cache'])
        
        avg_eff_cost = eff_cost.mean()
        monthly_cost = avg_eff_cost * DAILY_REQ * DAYS_IN_MONTH
        
        results.append({
            'scenario': scenario['name'],
            'price_per_1k': scenario['price'],
            'cache_rate': scenario['cache'],
            'avg_eff_cost': avg_eff_cost,
            'monthly_cost': monthly_cost,
        })
    
    scenario_df = pd.DataFrame(results)
    print("\n시나리오별 월간 비용 (일 2000건 기준):")
    for _, row in scenario_df.iterrows():
        print(f"  {row['scenario']}: ${row['monthly_cost']:.2f}")
    
    # 시나리오 CSV 저장
    scenario_df.to_csv('logs/scenario_comparison.csv', index=False)
    
    # 시나리오 바 차트
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(scenario_df['scenario'], scenario_df['monthly_cost'])
    ax.set_ylabel('월간 비용 (USD)')
    ax.set_title(f'시나리오별 월간 비용 추정 (일 {DAILY_REQ}건 기준)')
    ax.tick_params(axis='x', rotation=15)
    for i, v in enumerate(scenario_df['monthly_cost']):
        ax.text(i, v + 0.5, f'${v:.2f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(plots_dir / 'scenario_comparison.png', dpi=150)
    plt.close()
    print("  - scenario_comparison.png 저장")
    
    # === 비용 절감 잠재력 ===
    print("\n=== 비용 절감 잠재력 ===")
    base_monthly = scenario_df.iloc[0]['monthly_cost']
    best_monthly = scenario_df['monthly_cost'].min()
    saving = base_monthly - best_monthly
    saving_pct = (saving / base_monthly) * 100
    
    print(f"기본 시나리오 월간 비용: ${base_monthly:.2f}")
    print(f"최적 시나리오 월간 비용: ${best_monthly:.2f}")
    print(f"절감 가능 금액: ${saving:.2f} ({saving_pct:.1f}%)")
    print(f"연간 절감 가능 금액: ${saving * 12:.2f}")
    
    # === 요약 지표 저장 ===
    summary = {
        'total_requests': len(df),
        'blocked_count': int(blocked_count),
        'block_rate_pct': round(block_rate, 2),
        'pii_count': int(pii_count),
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
    
    with open('logs/summary_metrics.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n=== 완료 ===")
    print("  - logs/summary_metrics.json")
    print("  - logs/scenario_comparison.csv")
    print("  - plots/*.png (4개)")


if __name__ == "__main__":
    main()


