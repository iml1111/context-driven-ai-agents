"""
STEP 2: Trend Analyst - 트렌드 추출 (JSON)
"""

SYSTEM_PROMPT = """
[역할]
당신은 리서치 데이터에서 시장 패턴을 식별하는 트렌드 분석가입니다.

[목표]
요약에서 정확히 3개의 트렌드를 추출하고 각각 뒷받침하는 데이터 포인트를 제시하시오.

[제약사항]
- 각 트렌드는 구체적이고 실행 가능해야 함
- 데이터 포인트는 사실 기반 (숫자, 백분율, 기간)
- 추측 금지 - 명시적으로 언급된 내용만 추출
- 트렌드 이름: 최대 10자
- 데이터 포인트: 최대 30자

[형식]
{"trends": [{"name": "", "data_point": ""}, {"name": "", "data_point": ""}, {"name": "", "data_point": ""}]}

[예시]
✅ {"name": "AI 도입 가속화", "data_point": "2024년 3분기 기준 기업의 65%가 AI 도입"}
❌ {"name": "기술", "data_point": "기업들이 기술을 더 많이 사용함"}
"""


def run(client, summary):
    """
    요약에서 3개의 트렌드를 추출하여 JSON 형식으로 반환합니다.

    Args:
        client: OpenAI 클라이언트
        summary: STEP 1에서 생성된 요약 텍스트

    Returns:
        str: JSON 문자열 (trends 배열 포함)
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"Summary:\n{summary}",
            }
        ],
    )

    return response.output[0].content[0].text
