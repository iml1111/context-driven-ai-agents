"""
STEP 2: Trend Analyst - 트렌드 추출 (JSON)
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
    SYSTEM_PROMPT = """
You are a Trend Analyst.
Based on the following summary, extract 3 trends.
For each trend, provide a short name and one supporting data point.

Return JSON ONLY in the following format:
{
  "trends": [
    { "name": "", "data_point": "" },
    { "name": "", "data_point": "" },
    { "name": "", "data_point": "" }
  ]
}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"Summary:\n{summary}",
            }
        ],
    )

    trends_json = response.output[0].content[0].text
    return trends_json
