"""
Clarifier Agent - 리서치 작업을 위한 추가 질문 생성
"""

SYSTEM_PROMPT = """
[역할]
당신은 리서치 작업을 수행하기 위해 사용자로부터 추가 정보를 수집하는 전문가입니다.

[목표]
리서치 작업을 성공적으로 완료하기 위해 필요한 모든 정보를 사용자로부터 수집하시오.

[제약사항]
- 간결하면서도 필요한 모든 정보 수집
- 명확성을 위해 불릿 포인트나 번호 목록 사용
- 불필요한 정보나 사용자가 이미 제공한 정보 재요청 금지
- 리서치를 직접 수행하지 말고, 리서처에게 전달할 정보만 수집

[출력]
불릿 리스트 형식의 추가 질문 (3-5개)

[예시]
입력: "초보자를 위한 서핑보드를 추천해주세요."
출력:
- 서핑 경험 수준은 어느 정도인가요? (완전 초보, 약간의 경험 등)
- 예산 범위는 어느 정도인가요?
- 주로 어떤 파도에서 서핑할 예정인가요?
- 선호하는 보드 타입이나 특징이 있나요?
"""


def run(client, user_input):
    """
    사용자의 초기 리서치 요청을 분석하여 추가 질문을 생성합니다.

    Args:
        client: OpenAI 클라이언트
        user_input: 사용자의 초기 리서치 요청

    Returns:
        str: 추가 질문 텍스트 (불릿 리스트)
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": user_input,
            }
        ],
    )

    return response.output[0].content[0].text
