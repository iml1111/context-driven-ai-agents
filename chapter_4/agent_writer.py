"""
Writer Agent - Planner의 계획에 따라 PDF 요약 작성
"""

SYSTEM_PROMPT = """
[역할]
당신은 제공된 계획에 따라 PDF 문서를 요약하는 전문 작성자입니다.

[목표]
Planner가 제공한 요약 계획의 각 항목을 충실히 반영하여, PDF 문서의 핵심 내용을 5-7문장으로 요약하시오.

[제약사항]
- 계획의 모든 항목을 순서대로 반영할 것
- 사실에 기반한 객관적 정보만 포함
- 추측이나 주관적 의견 금지
- 가능한 경우 구체적인 데이터 포인트 포함
- 각 문장은 하나의 고유한 인사이트를 전달
- 언어: 한국어

[출력]
평문 요약 (5-7문장, 서식 없음)

[예시]
✅ "2024년 1분기 매출은 전년 대비 15% 증가한 120억 원을 기록했습니다. 주요 성장 동력은 엔터프라이즈 부문의 신규 계약 확대였습니다."
❌ "회사가 잘 되고 있는 것 같고 앞으로도 성장할 것으로 예상됩니다."
"""


def run(client, file_id, plan):
    """
    Planner의 계획과 PDF 파일을 기반으로 최종 요약을 작성합니다.

    Args:
        client: OpenAI 클라이언트
        file_id: 업로드된 PDF 파일 ID
        plan: Planner가 생성한 요약 계획 (불릿 리스트)

    Returns:
        str: 최종 요약 텍스트
    """
    response = client.responses.create(
        model="gpt-5.1",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": file_id},
                    {
                        "type": "input_text",
                        "text": f"요약 계획:\n{plan}\n\n위 계획에 따라 PDF 문서를 요약해주세요.",
                    },
                ],
            }
        ],
    )

    return response.output[0].content[0].text
