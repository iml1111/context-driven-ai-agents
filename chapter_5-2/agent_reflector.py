"""
Reflector 에이전트

역할: 실수 분석 및 핵심 인사이트 추출
- 답변이 틀렸을 때만 호출
- 실수의 원인을 분석하고 일반화된 교훈 추출
"""

import json
from openai import OpenAI


def run(client: OpenAI, task: dict, answer_result: dict, is_correct: bool) -> dict:
    """
    실수를 분석하고 핵심 인사이트 추출

    Args:
        client: OpenAI 클라이언트
        task: 원본 태스크 {question, ground_truth, explanation}
        answer_result: Generator의 답변 {answer, reasoning}
        is_correct: 정답 여부

    Returns:
        {
            "insight": 핵심 학습 내용 (1-2문장),
            "category": strategy/formula/example
        }
    """
    system_prompt = """당신은 실수 분석 전문가입니다.

**역할**:
1. 왜 답변이 틀렸는지 근본 원인 파악
2. 이 실수를 방지하기 위한 일반화된 전략/공식 추출
3. 1-2문장으로 명확하고 재사용 가능한 인사이트 도출

**카테고리**:
- strategy: 문제 해결 접근법 (예: "할인 계산 시 항상 원가 기준으로 계산")
- formula: 수학 공식 (예: "최종가격 = 원가 × (1 + 세율)")
- example: 구체적 예시 (예: "$100의 20% 할인 = $80")

답변 형식(JSON): {"insight": "인사이트 내용", "category": "strategy|formula|example"}
"""

    user_prompt = f"""
질문: {task['question']}
LLM 답변: {answer_result['answer']}
LLM 추론: {answer_result.get('reasoning', 'N/A')}
정답: {task['ground_truth']}
설명: {task['explanation']}

이 실수에서 얻을 수 있는 핵심 인사이트는 무엇인가요?
"""

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
