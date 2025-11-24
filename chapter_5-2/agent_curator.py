"""
Curator 에이전트

역할: 새로운 플레이북 항목 제안
- Reflector의 인사이트를 기반으로 플레이북에 추가할 항목 생성
- 중복 체크: 기존 항목과 유사하면 추가하지 않음
- 단순화 버전: ADD 연산만 지원 (AMEND, DEPRECATE 생략)
"""

import json
from difflib import SequenceMatcher
from openai import OpenAI
from playbook import Playbook, PlaybookItem


def is_similar(text1: str, text2: str, threshold: float = 0.7) -> bool:
    """
    두 텍스트의 유사도 계산 (단순 문자열 매칭)

    Args:
        text1: 첫 번째 텍스트
        text2: 두 번째 텍스트
        threshold: 유사도 임계값 (0.0 ~ 1.0)

    Returns:
        유사도가 임계값 이상이면 True
    """
    ratio = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    return ratio >= threshold


def run(client: OpenAI, playbook: Playbook, reflection: dict) -> list:
    """
    Reflector의 인사이트를 기반으로 새 플레이북 항목 제안

    Args:
        client: OpenAI 클라이언트
        playbook: 현재 플레이북
        reflection: Reflector의 분석 결과 {insight, category}

    Returns:
        List[PlaybookItem]: 추가할 항목 (0-1개)
    """
    insight = reflection["insight"]
    category = reflection["category"]

    # 중복 체크: 기존 항목과 유사한지 확인
    for existing_item in playbook.get_all():
        if is_similar(insight, existing_item.content, threshold=0.7):
            # 유사한 항목이 이미 존재하면 추가하지 않음
            return []

    # LLM을 사용하여 인사이트를 더 명확하고 재사용 가능하게 다듬기
    system_prompt = """당신은 플레이북 항목을 작성하는 전문가입니다.

**역할**:
1. 주어진 인사이트를 명확하고 재사용 가능한 형태로 다듬기
2. 1-2문장으로 간결하게 작성
3. 구체적이고 실용적인 조언 형태로 변환

답변 형식(JSON): {"refined_insight": "다듬어진 인사이트"}
"""

    user_prompt = f"""
원본 인사이트: {insight}
카테고리: {category}

이 인사이트를 플레이북 항목으로 다듬어주세요.
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
    refined_insight = result["refined_insight"]

    # 새 항목 생성
    new_item = PlaybookItem(
        id=playbook.generate_id(),
        category=category,
        content=refined_insight
    )

    return [new_item]
