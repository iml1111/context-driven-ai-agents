import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- 회의 메모 (입력 데이터) --------
MEETING_MEMO = """
오늘 전체 스탠드업에서 여러 얘기가 나왔는데, 로그인 속도가 아침 시간대(8–9시)에만 유독 느리다는 불만이 계속 접수된다고 했고 민수가 "캐시"를 한번 붙여보면 어떻겠냐고 했지만, 바로 적용하기엔 위험 부담이 있으니 우선 로그 샘플을 더 모으자고도 했음. 소라는 지난주에 랜딩 페이지 실험을 준비해왔는데, 디자인 팀이 배너 시안을 아직 확정 못 했고도 해서 11/20 (수)쯤 A/B를 켤 수 있을 것 같다고 함. 혹시 트래픽이 모자라면 사내 블로그에 하나 올려서 유입을 조금 보태자고 했고, 거기에 들어갈 카피는 톤앤매너를 B2B로 맞추자고 지후가 의견 냄(지후가 마케팅이랑도 얘기해본다고 했던 듯). 아, 그리고 어제부터 가격 페이지에 '에센셜/프로/비즈니스' 3단 구성을 검토 중인데, 구체 가격표는 다음 주로 넘기기로 했고, 다만 B2B 톤으로 문구 정리하는 건 미리 손보면 좋겠다고 했음. 다음 회의는 11/22(금) 오전 10시에 하자고 대충 합의했는데, 민수가 그 시간에 외부 미팅이 있을 수도 있다 해서 확정은 아닌 상태. 마지막으로 고객지원 쪽에서 케이스 3건 정도 더 들어오면 우선순위를 다시 보자고 했고, 배포는 이번 주 내로는 안 하는 걸로 분위기가 기울었음(버그 한두 개 더 묶자는 얘기도 있었고). 아, 그리고 로그인 이슈는 혹시 CDN 설정 때문에 그런 건 아닌지도 한번 체크해보자고 누가 얘기했는데 정확히 누가 말했는지는 기억 안 남.
"""

print("=" * 60)
print("📋 Exercise 1 - Before (간단한 프롬프트)")
print("=" * 60)
print("회의 메모:")
print(MEETING_MEMO.strip())
print("=" * 60)

# -------- Before: 간단한 프롬프트 --------
print("\n🔍 LLM 호출 중...")

PROMPT_BEFORE = """
회의 내용을 간단히 요약하고 액션 아이템을 알려줘.
가능하면 책임자와 마감도 넣어줘.
결과는 JSON 형식으로 반환해줘.
"""

resp = client.chat.completions.create(
    model="gpt-5.1",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": PROMPT_BEFORE},
        {"role": "user", "content": MEETING_MEMO},
    ],
)

result = resp.choices[0].message.content

print("✅ 응답 완료")
print("\n" + "=" * 60)
print("📄 결과 (JSON):")
print("=" * 60)
print(json.dumps(json.loads(result), ensure_ascii=False, indent=2))
