"""
Deep Research Agent - 웹 검색 기반 리서치 수행
"""


def run(client, enriched_prompt):
    """
    상세한 리서치 프롬프트를 받아 Deep Research를 수행합니다.

    Args:
        client: OpenAI 클라이언트 (timeout 설정 필수)
        enriched_prompt: Rewriter가 생성한 상세 리서치 프롬프트

    Returns:
        response 객체 (output_text 등 포함)
    """
    response = client.responses.create(
        model="o4-mini-deep-research",
        input=enriched_prompt,
        background=False,  # 실습용: 동기 실행
        tools=[
            {"type": "web_search_preview"},
        ],
    )

    return response
