"""
Intent Classifier - Rule-based Routing

[방식]
키워드 매칭과 정규표현식 패턴을 사용하여 intent를 분류합니다.
LLM 호출 없이 순수 로직으로 동작합니다.

[장점]
✅ 즉시 응답: 네트워크 호출 없이 로컬에서 즉시 처리 (~1ms)
✅ 무료: API 비용 0원
✅ 예측 가능: 동일 입력은 항상 동일 결과
✅ 디버깅 용이: 어떤 규칙이 매칭되었는지 명확히 추적
✅ 오프라인 동작: 인터넷 연결 불필요

[단점]
❌ 유연성 부족: 새로운 표현, 동의어 처리 어려움
❌ 유지보수 부담: 새 패턴 추가 시 코드 수정 필요
❌ 확장성 제한: intent 증가 시 규칙 복잡도 급증
❌ Edge case 처리: 애매한 케이스는 놓치기 쉬움

[적합한 사용 사례]
- 사용자 입력 패턴이 명확하고 제한적인 경우
- 비용 최소화가 핵심 요구사항인 경우
- 극도로 낮은 지연이 필요한 경우 (real-time)
- 오프라인 환경 또는 엣지 디바이스 배포

[비용/성능 특성]
- API 비용: $0 (로컬 처리)
- 응답 속도: ~1ms
- 정확도: 명확한 패턴 시 100%, 애매한 경우 낮음
"""

import re
import json


# Intent별 키워드 정의
FAQ_KEYWORDS = [
    "반품", "교환", "배송", "기간", "정책", "사양", "스펙",
    "기능", "가격", "할인", "이벤트", "사용법", "설치",
    "호환", "보증", "품질", "크기", "색상", "재고"
]

ORDER_KEYWORDS = [
    "주문", "조회", "확인", "배송", "추적", "상태",
    "언제", "도착", "발송", "배송지", "수령"
]

HUMAN_KEYWORDS = [
    "환불", "거부", "불만", "긴급", "상담사", "통화",
    "항의", "보상", "클레임", "문제", "해결", "답변 없"
]


def classify_by_pattern(user_message):
    """
    정규표현식 패턴으로 명확한 케이스 먼저 분류

    Returns:
        str or None: intent 또는 None (패턴 매칭 실패)
    """
    # 패턴 1: 주문번호 포함 (ORD-로 시작하는 패턴)
    if re.search(r'ORD-\d+', user_message):
        return "order"

    # 패턴 2: "상담사"와 "연결/통화" 조합
    if re.search(r'상담사.*(연결|통화|전화)', user_message):
        return "human"

    # 패턴 3: "환불" + "거부/안 됨" 조합
    if re.search(r'환불.*(거부|안.?됨|불가)', user_message):
        return "human"

    return None


def classify_by_keywords(user_message):
    """
    키워드 점수 기반 분류

    Returns:
        str: intent ("faq", "order", "human")
    """
    # 각 intent별 키워드 매칭 점수 계산
    faq_score = sum(1 for kw in FAQ_KEYWORDS if kw in user_message)
    order_score = sum(1 for kw in ORDER_KEYWORDS if kw in user_message)
    human_score = sum(1 for kw in HUMAN_KEYWORDS if kw in user_message)

    # 가장 높은 점수의 intent 선택
    max_score = max(faq_score, order_score, human_score)

    # 점수가 0이면 (아무 키워드도 매칭 안됨) → human (안전한 선택)
    if max_score == 0:
        return "human"

    # 점수가 같으면 우선순위: human > order > faq (안전한 순서)
    if human_score == max_score:
        return "human"
    elif order_score == max_score:
        return "order"
    else:
        return "faq"


def run(client, user_message):
    """
    규칙 기반으로 사용자 메시지를 분석하고 인텐트를 분류합니다.

    분류 전략:
    1. 명확한 패턴 매칭 (정규표현식) - 높은 신뢰도
    2. 키워드 점수 기반 분류 - 일반적인 케이스
    3. Fallback: 애매한 경우 "human" - 안전한 선택

    Args:
        client: OpenAI 클라이언트 (사용 안함, 인터페이스 호환성 유지)
        user_message: 사용자 입력 메시지

    Returns:
        str: JSON 문자열 {"intent": "faq"|"order"|"human"}
    """
    # STEP 1: 명확한 패턴 먼저 체크
    intent = classify_by_pattern(user_message)

    # STEP 2: 패턴 매칭 실패 시 키워드 기반 분류
    if intent is None:
        intent = classify_by_keywords(user_message)

    # JSON 형식으로 반환 (다른 router들과 동일한 인터페이스)
    return json.dumps({"intent": intent}, ensure_ascii=False)
