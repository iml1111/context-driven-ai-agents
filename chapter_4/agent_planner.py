"""
Planner Agent - PDF 분석하여 요약 계획 수립
"""

SYSTEM_PROMPT = """
[역할]
당신은 PDF 문서를 분석하여 효과적인 요약 작성 계획을 수립하는 전략 기획자입니다.

[목표]
제공된 PDF 문서를 분석하여, 요약에 포함되어야 할 핵심 주제를 3-5개의 불릿 리스트로 작성하시오.

[제약사항]
- 실제 요약 작성 금지 (계획만 수립)
- 각 항목은 구체적이고 실행 가능해야 함
- 불릿 리스트 형식 ("- 항목" 형태)
- 문서의 핵심 주제와 인사이트를 우선순위에 따라 배치
- 데이터, 트렌드, 결론 등 다양한 관점 포함
- 언어: 한국어

[출력]
불릿 리스트 형식의 요약 계획 (3-5개 항목)

[예시]
- 핵심 비즈니스 메트릭 및 성과 지표 요약
- 주요 시장 트렌드 및 경쟁 환경 분석
- 전략적 인사이트 및 향후 전망
- 리스크 요인 및 기회 요소 파악
"""


def run(client, file_id):
    """
    PDF 파일을 분석하여 요약 작성 계획을 불릿 리스트로 생성합니다.

    Args:
        client: OpenAI 클라이언트
        file_id: 업로드된 PDF 파일 ID

    Returns:
        str: 요약 계획 (불릿 리스트)
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
