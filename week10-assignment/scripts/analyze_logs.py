"""LLM 호출 로그를 분석하여 간단한 통계를 출력한다."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def analyze(log_path: Path) -> None:
    if not log_path.exists():
        raise FileNotFoundError(f"로그 파일을 찾을 수 없습니다: {log_path}")

    df = pd.read_csv(log_path)
    if df.empty:
        print("로그 데이터가 비어 있습니다.")
        return

    # 숫자형으로 변환
    df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce")
    if "total_tokens" in df.columns:
        df["total_tokens"] = pd.to_numeric(df["total_tokens"], errors="coerce")

    print("=== 프롬프트 버전별 통계 ===")
    version_stats = (
        df.groupby("prompt_version")
        .agg(
            호출수=("prompt_version", "count"),
            평균지연_ms=("latency_ms", "mean"),
            평균토큰수=("total_tokens", "mean"),
        )
        .round(2)
    )
    print(version_stats)

    print("\n=== 모델별 통계 ===")
    model_stats = (
        df.groupby("model")
        .agg(
            호출수=("model", "count"),
            평균지연_ms=("latency_ms", "mean"),
            평균토큰수=("total_tokens", "mean"),
        )
        .round(2)
    )
    print(model_stats)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LLM 로그 분석 스크립트")
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("week10-assignment/logs/llm_responses.csv"),
        help="분석할 로그 CSV 경로",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    analyze(args.log_path)


if __name__ == "__main__":
    main()

