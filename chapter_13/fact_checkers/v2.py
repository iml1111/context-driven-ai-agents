"""
Chapter 13: Fact-Checker Ver 2 (Improved)

4가지 개선 사항이 적용된 버전입니다:
1. Structured Output: JSON 출력 강제
2. 명시적 CoT: 체크리스트 항목별 검증 근거 명시
3. Confidence 가이드라인: 신뢰도 판단 기준 명시
4. UNVERIFIABLE 인식: 검증 불가 케이스 처리 강화

모델: gpt-5.1
"""

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================
# 데이터 모델
# ============================================================


class ChecklistItemV2(BaseModel):
    """개선된 체크리스트 항목"""

    point: str = Field(description="검증 포인트")
    source_type: str = Field(
        description="필요한 출처 유형: official/academic/news/database"
    )
    result: str = Field(default="", description="확인 결과")
    source_found: str = Field(default="", description="실제 찾은 출처")


class FactCheckResultV2(BaseModel):
    """팩트체크 최종 결과 (개선된 버전)"""

    verdict: str
    confidence: float
    confidence_reasoning: str
    evidence: str
    checklist: list[ChecklistItemV2]


# ============================================================
# Ver 2: Improved (개선된 프롬프트 + JSON Output)
# ============================================================


class FactCheckerV2:
    """
    Ver 2: Improved - 개선된 프롬프트 + gpt-5.1 + JSON Output

    개선 사항:
    1. JSON 출력으로 파싱 안정성 향상
    2. 명시적 Confidence 가이드라인
    3. UNVERIFIABLE 케이스 인식 강화
    4. 출처 유형 명시로 체크리스트 품질 향상
    """

    MODEL = "gpt-5.1"

    PLAN_PROMPT = """당신은 팩트체크 전문가입니다.

[목표]
주어진 주장을 검증하기 위한 체계적인 체크리스트를 생성하세요.

[체크리스트 작성 규칙]
1. 3~5개의 검증 포인트를 생성하세요
2. 각 포인트는 반드시 검증 가능해야 합니다:
   - 공식 문서, 학술 자료, 신뢰할 수 있는 뉴스에서 확인 가능
   - 주관적 판단이 아닌 객관적 사실 확인
3. 각 포인트에 필요한 출처 유형을 명시하세요:
   - official: 정부/기관 공식 문서
   - academic: 학술 논문, 연구 자료
   - news: 신뢰할 수 있는 언론 보도
   - database: 통계청, 위키피디아 등 데이터베이스

[출력 형식]
JSON 형식으로 출력:
{
  "checklist": [
    {"point": "검증 포인트", "source_type": "official|academic|news|database"},
    ...
  ]
}
"""

    ANALYSIS_PROMPT = """당신은 팩트체크 전문가입니다.

[목표]
체크리스트의 각 항목을 web_search로 검증하고 최종 판정을 내리세요.

[검증 프로세스]
1. 각 체크리스트 항목에 대해:
   a. web_search로 관련 정보 검색
   b. 찾은 출처와 내용을 기록
   c. 해당 포인트의 검증 결과 판단

2. 종합 판정:
   - TRUE: 모든 핵심 포인트가 확인됨
   - FALSE: 핵심 포인트가 사실과 다름
   - PARTIALLY_TRUE: 일부만 사실이거나 맥락에 따라 다름
   - UNVERIFIABLE: 신뢰할 수 있는 출처를 찾을 수 없음

[신뢰도(confidence) 판단 기준]
- 0.9~1.0: 공식 문서 또는 3개 이상의 신뢰할 수 있는 출처에서 일관된 정보
- 0.7~0.9: 2개 이상의 출처에서 확인, 일부 불확실성 존재
- 0.5~0.7: 출처가 제한적이거나 정보가 상충됨
- 0.3~0.5: 출처 신뢰도가 낮거나 간접적인 증거만 존재
- 0.0~0.3: 검증이 거의 불가능, 추측에 가까움

[UNVERIFIABLE 판단 기준]
다음 경우 UNVERIFIABLE로 판정:
- 관련 정보를 전혀 찾을 수 없음
- 찾은 출처들의 정보가 심하게 상충됨
- 주장이 미래 예측이거나 주관적 의견임

[출력 형식]
JSON 형식으로 출력:
{
  "verdict": "TRUE|FALSE|PARTIALLY_TRUE|UNVERIFIABLE",
  "confidence": 0.0~1.0,
  "confidence_reasoning": "신뢰도 판단 근거",
  "evidence": "검증 근거 요약",
  "checklist_results": [
    {"result": "검증 결과", "source_found": "찾은 출처"},
    ...
  ]
}
"""

    def __init__(self):
        self.client = client

    def _plan(self, claim: str) -> list[ChecklistItemV2]:
        """STEP 1: 체크리스트 생성"""
        response = self.client.responses.create(
            model=self.MODEL,
            instructions=self.PLAN_PROMPT,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": f"검증할 정보: {claim}\n\nJSON 형식으로 응답하세요."}
                    ],
                }
            ],
            text={"format": {"type": "json_object"}},
        )

        data = json.loads(response.output_text)
        return [ChecklistItemV2(**item) for item in data["checklist"]]

    def _analyze(
        self, claim: str, checklist: list[ChecklistItemV2]
    ) -> FactCheckResultV2:
        """STEP 2: 체크리스트 기반 분석 (web_search)"""
        checklist_text = "\n".join(
            [f"- {item.point} (출처 유형: {item.source_type})" for item in checklist]
        )

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

        # web_search와 JSON mode는 함께 사용 불가 → 텍스트에서 JSON 추출
        text = response.output_text

        # ```json``` 코드블록 우선 탐색
        code_block = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if code_block:
            data = json.loads(code_block.group(1))
        else:
            json_match = re.search(r'\{[\s\S]*\}', text)
            data = json.loads(json_match.group()) if json_match else {}

        # 체크리스트 결과 병합
        updated_checklist = []
        checklist_results = data.get("checklist_results", [])
        for i, item in enumerate(checklist):
            result = ""
            source_found = ""
            if i < len(checklist_results):
                cr = checklist_results[i]
                result = cr.get("result", "")
                source_found = cr.get("source_found", "")
            updated_checklist.append(
                ChecklistItemV2(
                    point=item.point,
                    source_type=item.source_type,
                    result=result,
                    source_found=source_found,
                )
            )

        return FactCheckResultV2(
            verdict=data["verdict"],
            confidence=data["confidence"],
            confidence_reasoning=data["confidence_reasoning"],
            evidence=data["evidence"],
            checklist=updated_checklist,
        )

    def run(self, claim: str) -> FactCheckResultV2:
        """팩트체크 실행"""
        checklist = self._plan(claim)
        result = self._analyze(claim, checklist)
        return result


# ============================================================
# 테스트용 실행
# ============================================================

if __name__ == "__main__":
    print("Fact-Checker Ver 2 (Improved)")
    agent = FactCheckerV2()

    claim = "대한민국의 수도는 서울이다"
    print(f"\n검증할 정보: {claim}")

    print("\n📋 STEP 1: 체크리스트 생성 중...")
    result = agent.run(claim)

    print(f"\n✅ 결과:")
    print(f"  Verdict: {result.verdict}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Confidence Reasoning: {result.confidence_reasoning}")
    print(f"  Evidence: {result.evidence}")
    print(f"\n체크리스트:")
    for item in result.checklist:
        print(f"  - {item.point} ({item.source_type})")
        if item.result:
            print(f"    → {item.result}")
        if item.source_found:
            print(f"    출처: {item.source_found}")
