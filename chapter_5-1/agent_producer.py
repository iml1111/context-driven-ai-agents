"""
Producer 에이전트: 블로그 글 생성 및 개선

역할:
- 주어진 주제에 대한 블로그 글 작성
- Critic 피드백을 반영한 개선안 생성
"""

SYSTEM_PROMPT = """
당신은 전문 블로그 작성자입니다.

[역할]
- 주어진 주제에 대해 명확하고 매력적인 블로그 글을 작성합니다.
- 독자가 쉽게 이해하고 실천할 수 있는 내용을 제공합니다.

[목표]
- 도입부: 주제를 소개하고 독자의 관심을 끕니다.
- 본문: 핵심 내용을 3-5개 포인트로 구체적으로 설명합니다.
- 결론: 핵심 메시지를 요약하고 독자에게 행동을 촉구합니다.

[제약사항]
- 길이: 500-800자 (한글 기준)
- 구조: 도입부-본문-결론의 명확한 3단 구성
- 스타일: 친근하고 실용적인 어조
- 예시: 구체적인 사례나 예시를 최소 2개 이상 포함

[출력]
- 블로그 글만 출력하세요. 추가 설명이나 메타 정보는 불필요합니다.
"""


def run(client, topic: str, critique: str | None = None) -> str:
    """
    블로그 글 생성 또는 개선

    Args:
        client: OpenAI 클라이언트
        topic: 블로그 주제
        critique: Critic 피드백 (개선 시 사용, 선택적)

    Returns:
        str: 생성된 블로그 글
    """
    if critique:
        # 개선 모드: Critic 피드백 반영
        user_prompt = f"""
주제: {topic}

다음은 이전 버전의 블로그 글입니다. Critic의 피드백을 반영하여 개선해주세요.

{critique}
"""
    else:
        # 초기 생성 모드
        user_prompt = f"""
주제: {topic}

위 주제로 블로그 글을 작성해주세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()
