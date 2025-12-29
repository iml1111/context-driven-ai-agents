"""
STEP 1: Market Analyst - PDF 요약
"""

SYSTEM_PROMPT = """
[역할]
당신은 리서치 리포트 문서에서 핵심 인사이트를 추출하는 분석가입니다.

[목표]
PDF의 핵심 내용을 5-7문장으로 요약하시오.

[제약사항]
- 사실에 기반한 객관적 정보만 포함
- 추측이나 주관적 의견 금지
- 가능한 경우 구체적인 데이터 포인트 포함
- 각 문장은 하나의 고유한 인사이트를 전달
- 언어: 한국어

[출력]
평문 요약 (5-7문장, 서식 없음)

[예시]
✅ "매출이 전년 대비 15% 증가했으며, 주요 성장 동력은 엔터프라이즈 부문 확장이었습니다"
❌ "회사가 잘 되고 있는 것 같고 앞으로 더 성장할 수도 있을 것 같습니다"
"""


def run(client, file_id):
    """
    PDF 파일을 분석하여 5-7문장의 요약을 생성합니다.

    Args:
        client: OpenAI 클라이언트
        file_id: 업로드된 PDF 파일 ID

    Returns:
        str: 요약 텍스트
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [{"type": "input_file", "file_id": file_id}],
            }
        ],
    )

    return response.output[0].content[0].text
