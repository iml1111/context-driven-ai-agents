"""
Intent Classifier - LLM-based Routing

[방식]
LLM(GPT-5.1)에게 사용자 입력을 분석하여 intent 분류를 위임합니다.

[장점]
✅ 유연성: 새로운 표현, 동의어, 문맥을 자동으로 이해
✅ 유지보수: 키워드 규칙 없이 자연어 지시사항으로 동작 정의
✅ 확장성: 새로운 intent 추가 시 프롬프트만 수정
✅ 복잡한 케이스 처리: 애매한 경우, 다의적 표현도 문맥 기반 판단

[단점]
❌ 비용: API 호출당 비용 발생 (~$0.0001/request)
❌ 지연: 네트워크 RTT + LLM 추론 시간 (~200-500ms)
❌ 예측 불가능성: 동일 입력도 간혹 다른 결과 (낮은 temperature에서는 거의 일관적)
❌ 디버깅 어려움: 왜 특정 intent로 분류했는지 추적 어려움

[적합한 사용 사례]
- 사용자 입력이 매우 다양하고 예측 불가능한 경우
- 비용보다 정확도와 유연성이 중요한 경우
- 빠른 프로토타이핑 및 실험 단계
- 규칙 기반으로 커버하기 어려운 복잡한 도메인

[비용/성능 특성]
- API 비용: ~$0.0001/request (gpt-5.1 기준)
- 응답 속도: ~200-500ms
- 정확도: 명확한 프롬프트 시 ~95%+
"""

SYSTEM_PROMPT = """
[역할]
당신은 고객 문의를 분류하는 인텐트 분류기입니다.

[목표]
사용자 메시지를 분석하여 다음 3가지 인텐트 중 하나로 분류하시오:
- faq: 제품 관련 일반 질문
- order: 주문 조회 요청
- human: 복잡한 문제로 상담사 연결 필요

[분류 기준]
- faq: "반품 정책", "배송 기간", "제품 사양" 등 일반적인 질문
- order: "주문 확인", "배송 조회", "주문번호 ORD-" 포함 시
- human: "환불 거부", "불만", "긴급", "복잡한 문제" 등

[제약사항]
- 반드시 3가지 인텐트 중 하나만 선택
- 애매한 경우 human으로 분류 (안전한 선택)
- 추측 금지 - 메시지 내용만 기반으로 판단

[출력]
JSON 형식: {"intent": "faq"|"order"|"human"}

[예시]
입력: "반품 정책이 어떻게 되나요?"
출력: {"intent": "faq"}

입력: "주문번호 ORD-12345 배송 조회해주세요"
출력: {"intent": "order"}

입력: "환불 거부당했는데 이해가 안 갑니다"
출력: {"intent": "human"}
"""


def run(client, user_message):
    """
    LLM을 사용하여 사용자 메시지를 분석하고 인텐트를 분류합니다.

    Args:
        client: OpenAI 클라이언트
        user_message: 사용자 입력 메시지

    Returns:
        str: JSON 문자열 {"intent": "faq"|"order"|"human"}
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": user_message,
            }
        ],
    )

    return response.output[0].content[0].text
