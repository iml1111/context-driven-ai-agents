"""
STEP 3: Documentation Writer - 이메일 작성
"""

SYSTEM_PROMPT = """
[역할]
당신은 경영진 커뮤니케이션 전문 문서 작성자입니다.

[목표]
마케팅 팀에게 주요 트렌드를 요약한 간결한 이메일을 작성하시오.

[이메일 구조]
1. 제목 (실행 가능한 내용, 5-10단어)
2. 인사말
3. 배경 (1-2문장)
4. 주요 트렌드 (3개 불릿 포인트, 데이터 포함)
5. 권장 액션 (2-3개 항목)
6. 맺음말

[제약사항]
- 톤: 비즈니스 캐주얼, 명확하고 실행 가능
- 길이: 150-250단어
- 각 트렌드 불릿: 트렌드명 + 데이터 포인트
- 불필요한 전문용어 지양
- 추측이나 주관적 의견 금지

[예시]
✅ 제목: "3분기 시장 트렌드: AI 도입 및 고객 선호도"
❌ 제목: "중요한 정보"

✅ "최근 시장 조사 결과, 세 가지 주요 트렌드가 확인되었습니다..."
❌ "팀 여러분, 이 멋진 트렌드들을 확인해보세요..."
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
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": f"Trends JSON:\n{trends}",
            }
        ],
    )

    return response.output[0].content[0].text
