"""
Chapter 13: Fact-Checker Ver 1 (Baseline)

chapter_0의 원본 프롬프트를 그대로 사용하는 Baseline 버전입니다.
모델: gpt-4o
"""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================
# 데이터 모델
# ============================================================


class ChecklistItem(BaseModel):
    """체크리스트 항목"""

    point: str  # 검증 포인트
    result: str = ""  # 확인 결과


class FactCheckResult(BaseModel):
    """팩트체크 최종 결과"""

    verdict: str  # TRUE, FALSE, PARTIALLY_TRUE, UNVERIFIABLE
    confidence: float  # 0.0 ~ 1.0
    evidence: str  # 검증 근거 요약
    checklist: list[ChecklistItem]  # 체크리스트 + 결과


# ============================================================
# Ver 1: Baseline (chapter_0 원본 프롬프트)
# ============================================================


class FactCheckerV1:
    """
    Ver 1: Baseline - chapter_0 원본 프롬프트 + gpt-4o

    chapter_0의 프롬프트를 그대로 사용하여 성능 기준선을 설정합니다.
    """

    MODEL = "gpt-4o"

    # chapter_0 원본 PLAN_PROMPT
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

    # chapter_0 원본 ANALYSIS_PROMPT
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

    def __init__(self):
        self.client = client

    def _plan(self, claim: str) -> list[ChecklistItem]:
        """STEP 1: 체크리스트 생성"""
        response = self.client.responses.create(
            model=self.MODEL,
            instructions=self.PLAN_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": f"검증할 정보: {claim}"}
                    ],
                }
            ],
        )

        # 텍스트에서 체크리스트 파싱 (- 포인트 형식)
        text = response.output_text
        checklist = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                point = line[1:].strip()
                if point:
                    checklist.append(ChecklistItem(point=point))

        return checklist

    def _analyze(self, claim: str, checklist: list[ChecklistItem]) -> FactCheckResult:
        """STEP 2: 체크리스트 기반 분석 (web_search 활용)"""
        checklist_text = "\n".join([f"- {item.point}" for item in checklist])

        response = self.client.responses.create(
            model=self.MODEL,
            instructions=self.ANALYSIS_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"검증할 정보: {claim}\n\n체크리스트:\n{checklist_text}",
                        }
                    ],
                }
            ],
            tools=[{"type": "web_search"}],
        )

        # JSON 파싱
        result_text = response.output_text

        # JSON 블록 추출 (```json ... ``` 또는 { ... })
        json_match = re.search(r"```json\s*(.*?)\s*```", result_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # JSON 블록이 없으면 전체 텍스트에서 { } 찾기
            json_match = re.search(r"\{.*\}", result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # 파싱 실패 시 기본값 반환
                return FactCheckResult(
                    verdict="UNVERIFIABLE",
                    confidence=0.0,
                    evidence="분석 결과를 파싱할 수 없습니다.",
                    checklist=checklist,
                )

        try:
            data = json.loads(json_str)

            # 체크리스트 결과 병합
            checklist_results = data.get("checklist_results", [])
            updated_checklist = []
            for i, item in enumerate(checklist):
                result = ""
                if i < len(checklist_results):
                    result = checklist_results[i].get("result", "")
                updated_checklist.append(
                    ChecklistItem(point=item.point, result=result)
                )

            return FactCheckResult(
                verdict=data.get("verdict", "UNVERIFIABLE"),
                confidence=float(data.get("confidence", 0.0)),
                evidence=data.get("evidence", ""),
                checklist=updated_checklist,
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return FactCheckResult(
                verdict="UNVERIFIABLE",
                confidence=0.0,
                evidence=f"JSON 파싱 오류: {str(e)}",
                checklist=checklist,
            )

    def run(self, claim: str) -> FactCheckResult:
        """
        팩트체크 실행

        Args:
            claim: 검증할 주장

        Returns:
            FactCheckResult: 팩트체크 결과
        """
        # STEP 1: Plan (체크리스트 생성)
        checklist = self._plan(claim)

        # STEP 2: Analysis (web_search + 검증)
        result = self._analyze(claim, checklist)

        return result


# ============================================================
# 테스트용 실행
# ============================================================

if __name__ == "__main__":
    print("Fact-Checker Ver 1 (Baseline)")
    agent = FactCheckerV1()

    # 테스트 케이스
    claim = "대한민국의 수도는 서울이다"
    print(f"\n검증할 정보: {claim}")

    print("\n📋 STEP 1: 체크리스트 생성 중...")
    result = agent.run(claim)

    print(f"\n✅ 결과:")
    print(f"  Verdict: {result.verdict}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Evidence: {result.evidence}")
    print(f"\n체크리스트:")
    for item in result.checklist:
        print(f"  - {item.point}")
        if item.result:
            print(f"    → {item.result}")
