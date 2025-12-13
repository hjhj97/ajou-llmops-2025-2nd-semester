"""
토크나이저 모듈
tiktoken을 사용하거나 폴백 추정기를 사용하여 토큰 수를 계산합니다.
"""

import math
from typing import Callable

ENC_NAME = "cl100k_base"  # GPT-4/4o 계열 인코더


def get_tokenizer() -> tuple[Callable[[str], int], bool]:
    """토크나이저 함수를 반환합니다.
    
    Returns:
        (토큰 카운트 함수, tiktoken 사용 여부)
    """
    try:
        import tiktoken
        enc = tiktoken.get_encoding(ENC_NAME)
        
        def _count(text: str) -> int:
            if text is None:
                text = ""
            return len(enc.encode(text))
        
        print(f"[tokenizer] tiktoken 사용: {ENC_NAME}")
        return _count, True
        
    except Exception as e:
        print("[tokenizer] tiktoken 미사용 — 폴백 추정기 사용 (문자수/4)")
        
        def _fallback(text: str) -> int:
            if text is None:
                text = ""
            return max(1, math.ceil(len(text) / 4))
        
        return _fallback, False


# 전역 토크나이저 인스턴스
count_tokens, USING_TIKTOKEN = get_tokenizer()


if __name__ == "__main__":
    # 테스트
    test_text = "안녕하세요. 이것은 테스트 문장입니다. Hello, this is a test sentence."
    token_count = count_tokens(test_text)
    print(f"텍스트: {test_text}")
    print(f"토큰 수: {token_count}")
    print(f"tiktoken 사용: {USING_TIKTOKEN}")

