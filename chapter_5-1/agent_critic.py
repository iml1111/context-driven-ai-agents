"""
Critic 에이전트: 블로그 글 품질 평가 및 개선 제안

역할:
- 블로그 글의 품질을 4가지 기준으로 점수화 (1-10)
- 구체적인 개선 제안 제공
- 종료 조건 판단 (평균 8점 이상 = OK)
"""

import json
from pydantic import BaseModel

SYSTEM_PROMPT = """
당신은 전문 블로그 에디터이자 품질 평가자입니다.

[역할]
- 블로그 글의 품질을 객관적으로 평가합니다.
- 구체적이고 실행 가능한 개선 제안을 제공합니다.

[평가 기준]
1. 명확성 (clarity): 주제가 명확하고 이해하기 쉬운가? (1-10점)
2. 구조 (structure): 도입-본문-결론 구조가 잘 갖춰졌는가? (1-10점)
3. 완전성 (completeness): 주제를 충분히 다뤘는가? (1-10점)
4. 실용성 (practicality): 구체적인 예시/조언이 있는가? (1-10점)

[출력 형식]
반드시 다음 JSON 형식으로만 출력하세요:
{
  "clarity": 점수(1-10),
  "structure": 점수(1-10),
  "completeness": 점수(1-10),
  "practicality": 점수(1-10),
  "suggestions": [
    "구체적인 개선 제안 1",
    "구체적인 개선 제안 2",
    ...
  ]
}

[평가 원칙]
- 엄격하게 평가하되, 건설적으로 제안하세요.
- 각 점수에 대한 근거를 suggestions에 포함하세요.
- 평균 8점 이상이면 충분히 좋은 품질입니다.
"""


class CritiqueScore(BaseModel):
    """Critic 평가 결과 스키마"""
    clarity: int  # 명확성 (1-10)
    structure: int  # 구조 (1-10)
    completeness: int  # 완전성 (1-10)
    practicality: int  # 실용성 (1-10)
    suggestions: list[str]  # 개선 제안 리스트

    @property
    def average(self) -> float:
        """평균 점수 계산"""
        return (self.clarity + self.structure + self.completeness + self.practicality) / 4

    @property
    def status(self) -> str:
        """종료 조건 판단: 평균 8.0 이상이면 OK"""
        return "OK" if self.average >= 8.0 else "NEED_REVISE"

    def format_feedback(self) -> str:
        """Critic 피드백을 Producer가 이해할 수 있는 형식으로 변환"""
        feedback = f"""
[이전 버전의 평가]
📊 점수:
  - 명확성: {self.clarity}/10
  - 구조: {self.structure}/10
  - 완전성: {self.completeness}/10
  - 실용성: {self.practicality}/10
  평균: {self.average:.1f}/10

💡 개선 제안:
"""
        for i, suggestion in enumerate(self.suggestions, 1):
            feedback += f"  {i}. {suggestion}\n"

        feedback += "\n위 피드백을 반영하여 블로그 글을 개선해주세요."
        return feedback


def run(client, topic: str, blog_post: str) -> CritiqueScore:
    """
    블로그 글 품질 평가

    Args:
        client: OpenAI 클라이언트
        topic: 원래 주제
        blog_post: 평가할 블로그 글

    Returns:
        CritiqueScore: 평가 결과 (점수 + 제안)
    """
    user_prompt = f"""
주제: {topic}

다음 블로그 글을 평가해주세요:

{blog_post}
"""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )

    # JSON 파싱 및 Pydantic 모델로 변환
    critique_dict = json.loads(response.choices[0].message.content.strip())
    return CritiqueScore(**critique_dict)
