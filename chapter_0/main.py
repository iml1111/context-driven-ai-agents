"""
Chapter 0: Fact-Check Agent
특정 정보에 대해 True/False 팩트 체크를 수행하는 에이전트

워크플로우: Plan → Analysis
- Plan: 팩트체크를 위한 체크리스트 생성
- Analysis: 체크리스트 기반 분석 (web_search 활용)
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 팩트체크 대상 정보
CLAIM = "대한민국의 수도는 서울이다"

# ============================================================
# STEP 1: Plan - 체크리스트 생성
# ============================================================

PLAN_PROMPT = """당신은 팩트체크 전문가입니다.

[목표]
주어진 정보를 검증하기 위한 체크리스트를 생성하세요.

[규칙]
- 3~5개의 검증 포인트 생성
- 각 포인트는 구체적이고 검증 가능해야 함
- 불릿 리스트 형식 (- 포인트)

[출력 형식]
- 검증 포인트 1
- 검증 포인트 2
- 검증 포인트 3
"""


def plan(claim: str) -> str:
    """팩트체크를 위한 체크리스트 생성"""
    response = client.responses.create(
        model="gpt-5.2",
        instructions=PLAN_PROMPT,
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": f"검증할 정보: {claim}"}],
            }
        ],
    )
    return response.output[0].content[0].text


# ============================================================
# STEP 2: Analysis - 체크리스트 기반 분석
# ============================================================

ANALYSIS_PROMPT = """당신은 팩트체크 전문가입니다.

[목표]
체크리스트를 기반으로 주어진 정보를 검증하세요.
필요시 web_search를 사용하여 최신 정보를 확인하세요.

[출력 형식 - JSON]
{
  "verdict": "TRUE 또는 FALSE 또는 PARTIALLY_TRUE 또는 UNVERIFIABLE",
  "confidence": 0.0~1.0 사이의 신뢰도 수치,
  "evidence": "검증 근거 요약 (2~3문장)",
  "checklist_results": [
    {"point": "검증 포인트", "result": "확인 결과"}
  ]
}
"""


def analyze(claim: str, checklist: str) -> str:
    """체크리스트 기반 분석 수행 (web_search 활용)"""
    response = client.responses.create(
        model="gpt-5.2",
        instructions=ANALYSIS_PROMPT,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"검증할 정보: {claim}\n\n체크리스트:\n{checklist}",
                    }
                ],
            }
        ],
        tools=[{"type": "web_search"}],
    )
    return response.output_text


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Chapter 0: Fact-Check Agent")
    print("=" * 60)

    print(f"\n📝 검증할 정보:\n{CLAIM}")

    # STEP 1: Plan
    print("\n" + "=" * 60)
    print("📋 STEP 1: 체크리스트 생성 중...")
    checklist = plan(CLAIM)
    print("✅ 체크리스트 완료")
    print("\n" + checklist)

    # STEP 2: Analysis
    print("\n" + "=" * 60)
    print("🔍 STEP 2: 분석 중... (web_search 활용)")
    result = analyze(CLAIM, checklist)
    print("✅ 분석 완료")

    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 팩트체크 결과:")
    print(result)

    print("\n" + "=" * 60)
    print("🎉 팩트체크 완료!")
