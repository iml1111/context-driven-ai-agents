"""
Order Module - 주문 조회 (Mock DB 연동)
"""

SYSTEM_PROMPT = """
[역할]
당신은 주문 정보를 조회하고 고객에게 안내하는 주문 관리 전문가입니다.

[목표]
주문 데이터를 기반으로 고객에게 현재 주문 상태를 친절하게 안내하시오.

[제약사항]
- 톤: 친절하고 명확
- 길이: 3-5문장
- 주문 상태, 배송지, 예상 도착일 포함
- 추가 문의는 고객센터 안내
- 언어: 한국어

[출력]
평문 안내 메시지 (주문 정보 기반)

[예시]
주문 데이터: {{"order_id": "ORD-12345", "status": "배송 중", "address": "서울시 강남구", "estimated_delivery": "2024-01-25"}}

답변: "주문번호 ORD-12345는 현재 배송 중입니다. 배송지는 서울시 강남구이며, 2024년 1월 25일 도착 예정입니다. 추가 문의사항이 있으시면 고객센터(1588-XXXX)로 연락 부탁드립니다."
"""


def _mock_get_order(order_id):
    """
    Mock 함수: 실제로는 DB 조회를 수행
    교육 목적으로 하드코딩된 데이터 반환

    Args:
        order_id: 주문 번호 (예: "ORD-12345")

    Returns:
        dict: 주문 정보 (status, address, estimated_delivery)
    """
    mock_orders = {
        "ORD-12345": {
            "order_id": "ORD-12345",
            "status": "배송 중",
            "address": "서울시 강남구 테헤란로 123",
            "estimated_delivery": "2024-01-25",
        },
        "ORD-67890": {
            "order_id": "ORD-67890",
            "status": "배송 완료",
            "address": "부산시 해운대구 센텀로 456",
            "estimated_delivery": "2024-01-20",
        },
    }
    return mock_orders.get(
        order_id,
        {
            "order_id": order_id,
            "status": "조회 불가",
            "address": "정보 없음",
            "estimated_delivery": "정보 없음",
        },
    )


def run(client, user_message):
    """
    사용자 메시지에서 주문번호를 추출하여 주문 정보를 조회하고 안내합니다.

    Args:
        client: OpenAI 클라이언트
        user_message: 사용자 메시지 (주문번호 포함)

    Returns:
        str: 주문 조회 결과 안내 메시지
    """
    # 간단한 주문번호 추출 (실제로는 더 정교한 파싱 필요)
    order_id = None
    if "ORD-" in user_message:
        parts = user_message.split("ORD-")
        if len(parts) > 1:
            order_id = "ORD-" + parts[1].split()[0]

    if not order_id:
        return "주문번호를 찾을 수 없습니다. 주문번호는 'ORD-'로 시작합니다. (예: ORD-12345)"

    # Mock DB 조회
    order_data = _mock_get_order(order_id)

    # LLM으로 안내 메시지 생성
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"주문 데이터: {order_data}\n\n이 정보를 바탕으로 고객에게 안내 메시지를 작성해주세요.",
            }
        ],
    )

    return response.output[0].content[0].text
