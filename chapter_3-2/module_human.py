"""
Human Escalation Module - 상담사 연결 (Mock 티켓 시스템)
"""

import random

SYSTEM_PROMPT = """
[역할]
당신은 복잡한 문제를 상담사에게 연결하는 에스컬레이션 전문가입니다.

[목표]
고객에게 상담사 연결 절차를 안내하고 티켓 번호를 제공하시오.

[제약사항]
- 톤: 공감하고 안심시키는 톤
- 길이: 3-4문장
- 티켓 번호, 예상 대기 시간, 연락 방법 포함
- 고객의 불편함에 대한 공감 표현
- 언어: 한국어

[출력]
평문 안내 메시지 (티켓 정보 포함)

[예시]
티켓 데이터: {{"ticket_id": "TKT-98765", "estimated_wait": "10분"}}

답변: "불편을 드려 죄송합니다. 귀하의 문의는 티켓 번호 TKT-98765로 등록되었으며, 전문 상담사가 약 10분 내에 연락드릴 예정입니다. 긴급한 경우 고객센터(1588-XXXX)로 직접 연락 주시면 즉시 도움드리겠습니다."
"""


def _mock_escalate_to_human():
    """
    Mock 함수: 실제로는 티켓 시스템에 등록
    교육 목적으로 랜덤 티켓 번호 생성

    Returns:
        dict: 티켓 정보 (ticket_id, estimated_wait)
    """
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    estimated_wait = random.choice(["5분", "10분", "15분", "20분"])

    return {
        "ticket_id": ticket_id,
        "estimated_wait": estimated_wait,
    }


def run(client, user_message):
    """
    상담사 연결을 위한 티켓을 생성하고 안내 메시지를 반환합니다.

    Args:
        client: OpenAI 클라이언트
        user_message: 사용자 메시지 (에스컬레이션 사유)

    Returns:
        str: 상담사 연결 안내 메시지
    """
    # Mock 티켓 생성
    ticket_data = _mock_escalate_to_human()

    # LLM으로 안내 메시지 생성
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"티켓 데이터: {ticket_data}\n\n고객 문의: {user_message}\n\n이 정보를 바탕으로 상담사 연결 안내 메시지를 작성해주세요.",
            }
        ],
    )

    return response.output[0].content[0].text
