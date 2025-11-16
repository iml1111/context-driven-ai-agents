import json
import os
from datetime import date
from typing import List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, field_validator

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- 회의 메모 (입력 데이터) --------
MEETING_MEMO = """
오늘 전체 스탠드업에서 여러 얘기가 나왔는데, 로그인 속도가 아침 시간대(8–9시)에만 유독 느리다는 불만이 계속 접수된다고 했고 민수가 "캐시"를 한번 붙여보면 어떻겠냐고 했지만, 바로 적용하기엔 위험 부담이 있으니 우선 로그 샘플을 더 모으자고도 했음. 소라는 지난주에 랜딩 페이지 실험을 준비해왔는데, 디자인 팀이 배너 시안을 아직 확정 못 했고도 해서 11/20 (수)쯤 A/B를 켤 수 있을 것 같다고 함. 혹시 트래픽이 모자라면 사내 블로그에 하나 올려서 유입을 조금 보태자고 했고, 거기에 들어갈 카피는 톤앤매너를 B2B로 맞추자고 지후가 의견 냄(지후가 마케팅이랑도 얘기해본다고 했던 듯). 아, 그리고 어제부터 가격 페이지에 '에센셜/프로/비즈니스' 3단 구성을 검토 중인데, 구체 가격표는 다음 주로 넘기기로 했고, 다만 B2B 톤으로 문구 정리하는 건 미리 손보면 좋겠다고 했음. 다음 회의는 11/22(금) 오전 10시에 하자고 대충 합의했는데, 민수가 그 시간에 외부 미팅이 있을 수도 있다 해서 확정은 아닌 상태. 마지막으로 고객지원 쪽에서 케이스 3건 정도 더 들어오면 우선순위를 다시 보자고 했고, 배포는 이번 주 내로는 안 하는 걸로 분위기가 기울었음(버그 한두 개 더 묶자는 얘기도 있었고). 아, 그리고 로그인 이슈는 혹시 CDN 설정 때문에 그런 건 아닌지도 한번 체크해보자고 누가 얘기했는데 정확히 누가 말했는지는 기억 안 남.
"""

# -------- Pydantic 스키마 정의 --------
class Evidence(BaseModel):
    quote: str


class Action(BaseModel):
    task: str
    owner: str
    due: Optional[date]
    evidence: Evidence


class Output(BaseModel):
    title: str
    summary: str = Field(max_length=120)
    actions: List[Action]
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("actions")
    @classmethod
    def exactly_3_actions(cls, v):
        if len(v) != 3:
            raise ValueError("actions must contain exactly 3 items")
        return v


print("=" * 60)
print("📋 Exercise 1 - After (구조화된 프롬프트 + 검증)")
print("=" * 60)
print("회의 메모:")
print(MEETING_MEMO.strip())
print("=" * 60)

# -------- After: 구조화된 프롬프트 --------
print("\n🔍 LLM 호출 중...")

PROMPT_AFTER = """
[Goal]
장문 회의 메모에서 액션 3개 추출하여 JSON으로 반환하시오.(소유자/기한/근거 포함)

[Constraints]
한국어, summary ≤ 120자, 추측 금지, 누락은 null, JSON only

[Format]
{"title":"","summary":"","actions":[{"task":"","owner":"","due":null,"evidence":{"quote":""}}],"confidence":0.0}

[Evidence]
각 액션은 입력 텍스트에서 짧은 인용(quote) 1개 포함

[Examples]
✅ 소유자/기한/인용 포함, 불확실 due는 null
❌ 소유자 임의 추정, 서문·설명 섞임
"""

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": PROMPT_AFTER},
        {"role": "user", "content": MEETING_MEMO},
    ],
)

result = resp.choices[0].message.content
data = json.loads(result)

print("✅ 응답 완료")
print("\n" + "=" * 60)
print("📄 결과 (JSON):")
print("=" * 60)
print(json.dumps(data, ensure_ascii=False, indent=2))

# -------- Pydantic 검증 --------
print("\n" + "=" * 60)
print("🔍 Pydantic 스키마 검증 중...")
print("=" * 60)

Output.model_validate(data)

print("✅ 검증 통과!")

