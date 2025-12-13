"""
PII 마스킹 모듈
전화번호, 이메일, 주민등록번호 등의 개인정보를 마스킹합니다.
"""

import re
from typing import Tuple, List

# 한국 전화번호 패턴 (010-xxxx-xxxx, 010xxxxxxxx 형식 지원)
PHONE_PAT = re.compile(r"(01[016789]-?\d{3,4}-?)\d{4}")

# 이메일 패턴
EMAIL_PAT = re.compile(r"([A-Za-z0-9._%+-]{2})[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")

# 주민등록번호 패턴 (xxxxxx-xxxxxxx)
RRN_PAT = re.compile(r"\b(\d{6})-(\d{7})\b")


def mask_kr_phone(text: str) -> str:
    """한국 전화번호를 마스킹합니다.
    
    예: 010-1234-5678 -> 010-1234-****
    """
    return PHONE_PAT.sub(r"\1****", text)


def mask_email(text: str) -> str:
    """이메일 주소를 마스킹합니다.
    
    예: user.name@test.com -> us***@test.com
    """
    return EMAIL_PAT.sub(r"\1***\2", text)


def redact_rrn(text: str) -> str:
    """주민등록번호를 마스킹합니다.
    
    예: 990101-1234567 -> 990101-*******
    """
    return RRN_PAT.sub(r"\1-*******", text)


def mask_basic_all(text: str) -> Tuple[str, List[str]]:
    """모든 PII를 마스킹하고 발견된 PII 타입 목록을 반환합니다.
    
    Args:
        text: 원본 텍스트
        
    Returns:
        (마스킹된 텍스트, PII 타입 목록)
        예: ("마스킹된 텍스트", ["phone", "email"])
    """
    before = text
    after = mask_kr_phone(mask_email(redact_rrn(text)))
    
    hits = []
    if before != after:
        if PHONE_PAT.search(before):
            hits.append('phone')
        if EMAIL_PAT.search(before):
            hits.append('email')
        if RRN_PAT.search(before):
            hits.append('rrn')
    
    return after, hits


if __name__ == "__main__":
    # 테스트
    sample = "안녕하세요 제 번호는 010-1234-5678, 메일은 user.name@test.co.kr 입니다. RRN: 990101-1234567"
    masked, hits = mask_basic_all(sample)
    print("[원본] ", sample)
    print("[마스킹]", masked)
    print("[PII hits]", hits)

