"""
Chapter 13: Agent Workflow Evaluation Pipeline

두 버전의 팩트체커를 동일 데이터셋으로 평가하여 성능 비교합니다.

워크플로우:
1. 데이터셋 로드 (eval_data.jsonl)
2. Ver 1 (gpt-4o, 원본) 평가
3. Ver 2 (gpt-5.1, 개선) 평가
4. A/B 비교 리포트 생성

학습 목표:
- 에이전트 시스템의 비결정적 특성 이해
- 중간 산출물(체크리스트) + 최종 출력(verdict) 다층 평가
- LLM-as-Judge 패턴 구현
- Before/After 성능 비교를 통한 개선 측정
"""

from dataset import EvalCase, load_dataset
from evaluators import (
    AccuracyEvaluator,
    CalibrationAnalyzer,
    ChecklistJudge,
    EvidenceJudge,
)
from fact_checkers import FactCheckerV1, FactCheckerV2
from report import CaseResult, EvalReport, generate_report, print_comparison_report


# ============================================================
# 단일 에이전트 평가
# ============================================================


def evaluate_agent(
    agent,
    dataset: list[EvalCase],
    version_name: str,
    accuracy_evaluator: AccuracyEvaluator,
    checklist_judge: ChecklistJudge,
    evidence_judge: EvidenceJudge,
    calibration_analyzer: CalibrationAnalyzer,
) -> EvalReport:
    """
    단일 에이전트 평가 실행

    Args:
        agent: 팩트체커 에이전트 (V1 또는 V2)
        dataset: 평가 데이터셋
        version_name: 버전 이름
        accuracy_evaluator: L1 정확도 평가기
        checklist_judge: L2 체크리스트 평가기
        evidence_judge: L3 근거 평가기
        calibration_analyzer: L4 Calibration 분석기

    Returns:
        EvalReport: 평가 리포트
    """
    print(f"🔄 {version_name} 평가 시작...")

    case_results = []
    calibration_data = []  # (confidence, is_correct) 튜플

    for i, case in enumerate(dataset, 1):
        print(f"\n📝 Case {i}/{len(dataset)}: {case.claim[:40]}...")

        # 에이전트 실행
        result = agent.run(case.claim)

        # L1: Accuracy 평가
        acc_result = accuracy_evaluator.evaluate(result.verdict, case.ground_truth.value)

        # L2: Checklist Quality 평가
        checklist_score = checklist_judge.evaluate(case.claim, result.checklist)

        # L3: Evidence Quality 평가
        evidence_score = evidence_judge.evaluate(
            claim=case.claim,
            verdict=result.verdict,
            confidence=result.confidence,
            evidence=result.evidence,
            checklist=result.checklist,
        )

        # 결과 저장
        case_results.append(
            CaseResult(
                case_id=i,
                claim=case.claim,
                ground_truth=case.ground_truth.value,
                predicted=acc_result.predicted,
                is_correct=acc_result.is_correct,
                confidence=result.confidence,
                checklist_score=checklist_score.score,
                evidence_score=evidence_score.score,
            )
        )

        # Calibration용 데이터 수집
        calibration_data.append((result.confidence, acc_result.is_correct))

        # 진행 상황 출력
        status = "✅" if acc_result.is_correct else "❌"
        print(f"  {status} {acc_result.predicted} (정답: {case.ground_truth.value})")
        print(f"  📋 Checklist: {checklist_score.score}/5 | 📄 Evidence: {evidence_score.score}/5")

    # L4: Calibration 분석
    calibration = calibration_analyzer.analyze(calibration_data)

    return generate_report(version_name, case_results, calibration)


# ============================================================
# A/B 비교 실행
# ============================================================


def run_ab_comparison():
    """A/B 비교 평가 실행"""
    print("=" * 60)
    print("📊 Chapter 13: Fact-Checker A/B Evaluation")
    print("=" * 60)

    # 데이터셋 로드
    dataset = load_dataset("eval_data.jsonl")
    print(f"\n📁 데이터셋 로드 완료: {len(dataset)}개 케이스")

    # 평가기 초기화
    accuracy_evaluator = AccuracyEvaluator()
    checklist_judge = ChecklistJudge()
    evidence_judge = EvidenceJudge()
    calibration_analyzer = CalibrationAnalyzer()

    # Ver 1 평가 (Baseline)
    v1_agent = FactCheckerV1()
    v1_report = evaluate_agent(
        v1_agent,
        dataset,
        "Ver 1 - Baseline (gpt-4o)",
        accuracy_evaluator,
        checklist_judge,
        evidence_judge,
        calibration_analyzer,
    )

    # Ver 2 평가 (Improved)
    v2_agent = FactCheckerV2()
    v2_report = evaluate_agent(
        v2_agent,
        dataset,
        "Ver 2 - Improved (gpt-5.1)",
        accuracy_evaluator,
        checklist_judge,
        evidence_judge,
        calibration_analyzer,
    )

    # A/B 비교 리포트
    print_comparison_report(v1_report, v2_report)

    print(f"\n{'='*60}")
    print("🎉 A/B 평가 완료!")
    print("=" * 60)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    run_ab_comparison()
