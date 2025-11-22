"""
STEP 1: Market Analyst - PDF 요약
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
    SYSTEM_PROMPT = """
You are a Market Analyst.
Summarize the key findings of the PDF in 5–7 sentences.
Focus only on factual, objective information.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SYSTEM_PROMPT,
        input=[
            {
                "role": "user",
                "content": [{"type": "input_file", "file_id": file_id}],
            }
        ],
    )

    summary = response.output[0].content[0].text
    return summary
