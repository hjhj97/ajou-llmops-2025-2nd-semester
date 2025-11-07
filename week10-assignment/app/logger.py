"""LLM 호출 로그 관리."""

from __future__ import annotations

import csv
import os
from pathlib import Path
from threading import Lock
from typing import Dict, Optional


LOG_PATH = Path(os.getenv("LLM_LOG_PATH", "week10-assignment/logs/llm_responses.csv"))
_CSV_HEADER = [
    "timestamp",
    "prompt",
    "prompt_version",
    "model",
    "latency_ms",
    "total_tokens",
]
_lock = Lock()


def ensure_log_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def log_llm_call(record: Dict[str, Optional[str]]) -> None:
    """LLM 호출 정보를 CSV로 저장한다."""

    ensure_log_dir(LOG_PATH)

    with _lock:
        file_exists = LOG_PATH.exists()
        with LOG_PATH.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=_CSV_HEADER)
            if not file_exists:
                writer.writeheader()
            writer.writerow({key: record.get(key) for key in _CSV_HEADER})

