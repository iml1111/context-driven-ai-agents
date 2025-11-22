"""
STEP 3: Documentation Writer - 이메일 작성
"""


def run(client, trends):
    """
    트렌드 JSON을 기반으로 마케팅 팀에게 보낼 이메일을 작성합니다.

    Args:
        client: OpenAI 클라이언트
        trends: STEP 2에서 생성된 JSON 문자열

    Returns:
        str: 이메일 텍스트
    """
    SYSTEM_PROMPT = """
You are an Expert Documentation Writer.
Write a concise email to the marketing team summarizing the following trends.
Tone: business casual and clear.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"Trends JSON:\n{trends}",
            }
        ],
    )

    email = response.output[0].content[0].text
    return email
