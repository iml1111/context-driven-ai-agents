"""
Generator 에이전트

역할: 현재 플레이북을 참고하여 질문에 답변
- 플레이북이 비어있으면 지식 없이 답변
- 플레이북 항목이 있으면 해당 전략/공식을 활용
"""

import json
from openai import OpenAI
from playbook import Playbook


def run(client: OpenAI, playbook: Playbook, question: str) -> dict:
    """
    현재 플레이북을 사용하여 질문에 답변

    Args:
        client: OpenAI 클라이언트
        playbook: 현재 플레이북
        question: 사용자 질문

    Returns:
        {
            "answer": 답변 (숫자 또는 $표시 금액),
            "reasoning": 추론 과정
        }
    """
    # 플레이북을 프롬프트에 포함
    playbook_text = playbook.format_for_prompt()

    system_prompt = f"""당신은 수학 및 재무 계산 전문가입니다.

{playbook_text}

**지침**:
1. 위 플레이북에 관련 전략/공식이 있다면 반드시 활용하세요
2. 정확한 계산 결과만 답변하세요 (설명 불필요)
3. 금액은 $기호 포함, 숫자는 그대로 반환
4. 답변 형식(JSON): {{"answer": "결과값", "reasoning": "간단한 계산 과정"}}
"""

    user_prompt = f"질문: {question}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
    return result
