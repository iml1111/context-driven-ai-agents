"""
Intent Classifier - 사용자 입력을 적절한 모듈로 라우팅
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
    사용자 메시지를 분석하여 인텐트를 분류합니다.

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
