"""
Chapter 13: Evaluators - L2 & L3: LLM-as-Judge

LLM을 사용하여 체크리스트 품질(L2)과 근거 충분성(L3)을 평가합니다.
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================
# 데이터 모델
# ============================================================


class JudgeScore(BaseModel):
    """LLM Judge 평가 결과"""

    score: int = Field(ge=1, le=5, description="1-5점")
    reasoning: str = Field(description="평가 근거")


# ============================================================
# L2: 체크리스트 품질 평가
# ============================================================


class ChecklistJudge:
    """
    L2: 체크리스트 품질 평가 (LLM-as-Judge)

    평가 기준:
    1. 구체성: 검증 포인트가 구체적이고 명확한가?
    2. 포괄성: 주장을 검증하기 위한 주요 측면을 모두 다루는가?
    3. 검증가능성: 각 포인트가 실제로 검증 가능한가?
    4. 관련성: 모든 포인트가 주장과 직접적으로 관련있는가?
    """

    MODEL = "gpt-5.1"

    PROMPT = """당신은 팩트체크 체크리스트 품질 평가 전문가입니다.

[평가 기준]
1. 구체성: 검증 포인트가 구체적이고 명확한가?
2. 포괄성: 주장을 검증하기 위한 주요 측면을 모두 다루는가?
3. 검증가능성: 각 포인트가 실제로 검증 가능한가?
4. 관련성: 모든 포인트가 주장과 직접적으로 관련있는가?

[입력]
- 검증할 주장: {claim}
- 생성된 체크리스트:
{checklist}

[점수 기준]
- 5: 매우 우수 (모든 기준 충족, 전문가 수준)
- 4: 우수 (대부분 기준 충족, 약간의 개선 여지)
- 3: 보통 (일부 개선 필요, 기본적인 수준)
- 2: 미흡 (상당한 개선 필요, 핵심 누락)
- 1: 매우 미흡 (전면 재작성 필요)

[출력 형식]
JSON 형식으로 출력:
{{"score": 1-5, "reasoning": "평가 근거"}}
"""

    def __init__(self):
        self.client = client

    def evaluate(self, claim: str, checklist: list) -> JudgeScore:
        """체크리스트 품질 평가"""
        # 체크리스트 포맷팅
        checklist_text = ""
        for item in checklist:
            if hasattr(item, "point"):
                point = item.point
                source_type = getattr(item, "source_type", "")
                if source_type:
                    checklist_text += f"- {point} (출처 유형: {source_type})\n"
                else:
                    checklist_text += f"- {point}\n"
            else:
                checklist_text += f"- {item}\n"

        prompt = self.PROMPT.format(claim=claim, checklist=checklist_text)

        response = self.client.responses.create(
            model=self.MODEL,
            instructions=prompt,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "위 체크리스트를 평가해주세요. JSON 형식으로 응답하세요."}
                    ],
                }
            ],
            text={"format": {"type": "json_object"}},
        )

        data = json.loads(response.output_text)
        return JudgeScore(**data)


# ============================================================
# L3: 근거 충분성 평가
# ============================================================


class EvidenceJudge:
    """
    L3: 근거 충분성 평가 (LLM-as-Judge)

    평가 기준:
    1. 충분성: 결론을 뒷받침하기에 충분한 근거인가?
    2. 신뢰성: 근거가 신뢰할 수 있는 출처에서 왔는가?
    3. 논리성: 근거에서 결론으로의 논리적 연결이 타당한가?
    4. 명확성: 근거가 명확하고 이해하기 쉬운가?
    """

    MODEL = "gpt-5.1"

    PROMPT = """당신은 팩트체크 근거 품질 평가 전문가입니다.

[평가 기준]
1. 충분성: 결론을 뒷받침하기에 충분한 근거인가?
2. 신뢰성: 근거가 신뢰할 수 있는 출처에서 왔는가?
3. 논리성: 근거에서 결론으로의 논리적 연결이 타당한가?
4. 명확성: 근거가 명확하고 이해하기 쉬운가?

[입력]
- 검증할 주장: {claim}
- 판정: {verdict}
- 신뢰도: {confidence}
- 제시된 근거: {evidence}
- 체크리스트 검증 결과:
{checklist_results}

[점수 기준]
- 5: 매우 우수 (충분하고 신뢰할 수 있는 근거, 논리적 연결 완벽)
- 4: 우수 (대체로 충분한 근거, 약간의 보완 필요)
- 3: 보통 (기본적인 근거 제시, 추가 검증 권장)
- 2: 미흡 (근거 불충분, 출처 불명확)
- 1: 매우 미흡 (근거 없음 또는 논리적 비약)

[출력 형식]
JSON 형식으로 출력:
{{"score": 1-5, "reasoning": "평가 근거"}}
"""

    def __init__(self):
        self.client = client

    def evaluate(
        self,
        claim: str,
        verdict: str,
        confidence: float,
        evidence: str,
        checklist: list,
    ) -> JudgeScore:
        """근거 충분성 평가"""
        # 체크리스트 결과 포맷팅
        checklist_text = ""
        for item in checklist:
            if hasattr(item, "point"):
                point = item.point
                result = getattr(item, "result", "")
                checklist_text += f"- {point}\n"
                if result:
                    checklist_text += f"  → {result}\n"
            else:
                checklist_text += f"- {item}\n"

        prompt = self.PROMPT.format(
            claim=claim,
            verdict=verdict,
            confidence=confidence,
            evidence=evidence,
            checklist_results=checklist_text,
        )

        response = self.client.responses.create(
            model=self.MODEL,
            instructions=prompt,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "위 근거를 평가해주세요. JSON 형식으로 응답하세요."}
                    ],
                }
            ],
            text={"format": {"type": "json_object"}},
        )

        data = json.loads(response.output_text)
        return JudgeScore(**data)


# ============================================================
# 테스트용 실행
# ============================================================

if __name__ == "__main__":
    print("LLM-as-Judge 테스트")
    print("=" * 60)

    # 테스트 데이터
    claim = "대한민국의 수도는 서울이다"
    checklist = [
        {"point": "대한민국 헌법에서 수도 규정 확인", "source_type": "official"},
        {"point": "정부 공식 문서에서 서울 수도 명시 확인", "source_type": "official"},
        {"point": "국제기구의 대한민국 수도 정보 확인", "source_type": "database"},
    ]

    # L2: 체크리스트 품질 평가
    print("\n📋 L2: 체크리스트 품질 평가")
    checklist_judge = ChecklistJudge()

    class MockItem:
        def __init__(self, d):
            self.point = d["point"]
            self.source_type = d.get("source_type", "")

    mock_checklist = [MockItem(c) for c in checklist]
    result = checklist_judge.evaluate(claim, mock_checklist)
    print(f"  점수: {result.score}/5")
    print(f"  근거: {result.reasoning}")

    # L3: 근거 충분성 평가
    print("\n📄 L3: 근거 충분성 평가")
    evidence_judge = EvidenceJudge()
    result = evidence_judge.evaluate(
        claim=claim,
        verdict="TRUE",
        confidence=0.95,
        evidence="대한민국 헌법 제1조에 따르면 대한민국의 수도는 서울입니다.",
        checklist=mock_checklist,
    )
    print(f"  점수: {result.score}/5")
    print(f"  근거: {result.reasoning}")
