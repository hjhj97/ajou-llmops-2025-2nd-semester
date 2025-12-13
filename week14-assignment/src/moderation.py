"""
출력 모더레이션 모듈
detoxify 또는 휴리스틱 기반으로 유해성을 판단합니다.
"""

# detoxify 사용 가능 여부 확인
# 안정성을 위해 휴리스틱 모드 사용
DEToxic = None
print("[moderation] 휴리스틱 모드 사용")


# 휴리스틱용 금칙어 사전
BAD_WORDS = {
    '욕설': ['바보', '멍청', 'XXX', 'idiot', 'stupid', '병신', '개새', '씨발', 'fuck'],
    '자해': ['자해', '죽고', '스스로 해치', 'kill myself', '자살'],
    '증오': ['혐오', '증오', 'hate you', '죽어', '최악']
}


def heuristic_toxicity(text: str) -> float:
    """휴리스틱 기반 유해성 점수 계산 (0~1)
    
    Args:
        text: 검사할 텍스트
        
    Returns:
        유해성 점수 (0.0 ~ 1.0)
    """
    text_l = text.lower()
    score = 0.0
    
    for cat, words in BAD_WORDS.items():
        for w in words:
            if w.lower() in text_l:
                score += 0.4
    
    return min(score, 1.0)


def classify_toxicity(text: str) -> float:
    """텍스트의 유해성 점수를 반환합니다.
    
    detoxify가 사용 가능하면 모델 기반, 아니면 휴리스틱 사용
    
    Args:
        text: 검사할 텍스트
        
    Returns:
        유해성 점수 (0.0 ~ 1.0)
    """
    if DEToxic is not None:
        try:
            result = DEToxic.predict(text)
            return float(result.get('toxicity', 0.0))
        except Exception:
            return heuristic_toxicity(text)
    else:
        return heuristic_toxicity(text)


if __name__ == "__main__":
    # 테스트
    safe = "안녕하세요. 오늘 날씨가 참 좋네요!"
    toxic = "너는 죽어 마땅해. 최악의 사람이야. Fuck you. 바보야."
    
    print("안전한 텍스트 점수:", classify_toxicity(safe))
    print("유해한 텍스트 점수:", classify_toxicity(toxic))

