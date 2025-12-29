"""
Chapter 13: Report - 평가 리포트 생성

단일 버전 리포트 및 A/B 비교 리포트를 생성합니다.
"""

from pydantic import BaseModel

from evaluators.calibration import CalibrationResult


# ============================================================
# 데이터 모델
# ============================================================


class CaseResult(BaseModel):
    """케이스별 평가 결과"""

    case_id: int
    claim: str
    ground_truth: str
    predicted: str
    is_correct: bool
    confidence: float
    checklist_score: int  # 1-5
    evidence_score: int  # 1-5


class EvalReport(BaseModel):
    """종합 평가 리포트"""

    version_name: str  # 버전 이름 (Ver 1 - Baseline, Ver 2 - Improved)

    # 요약 지표
    total_cases: int
    accuracy: float  # L1: 정확도 (0.0 ~ 1.0)
    avg_checklist_score: float  # L2: 평균 체크리스트 점수 (1-5)
    avg_evidence_score: float  # L3: 평균 근거 점수 (1-5)
    calibration: CalibrationResult  # L4: Calibration 분석

    # 상세 결과
    case_results: list[CaseResult]


# ============================================================
# 리포트 생성
# ============================================================


def generate_report(
    version_name: str,
    case_results: list[CaseResult],
    calibration: CalibrationResult,
) -> EvalReport:
    """
    종합 평가 리포트 생성

    Args:
        version_name: 버전 이름
        case_results: 케이스별 평가 결과
        calibration: Calibration 분석 결과

    Returns:
        EvalReport: 종합 평가 리포트
    """
    total = len(case_results)

    # L1: 정확도
    correct_count = sum(1 for r in case_results if r.is_correct)
    accuracy = correct_count / total if total > 0 else 0.0

    # L2: 평균 체크리스트 점수
    avg_checklist = (
        sum(r.checklist_score for r in case_results) / total if total > 0 else 0.0
    )

    # L3: 평균 근거 점수
    avg_evidence = (
        sum(r.evidence_score for r in case_results) / total if total > 0 else 0.0
    )

    return EvalReport(
        version_name=version_name,
        total_cases=total,
        accuracy=round(accuracy, 4),
        avg_checklist_score=round(avg_checklist, 2),
        avg_evidence_score=round(avg_evidence, 2),
        calibration=calibration,
        case_results=case_results,
    )


# ============================================================
# 리포트 출력
# ============================================================


def print_comparison_report(v1_report: EvalReport, v2_report: EvalReport) -> None:
    """A/B 비교 리포트 출력"""
    print(f"\n{'='*60}")
    print(f"📊 A/B 성능 비교: Ver 1 vs Ver 2")
    print(f"{'='*60}")

    # Ver 1 요약
    v1_correct = sum(1 for r in v1_report.case_results if r.is_correct)
    print(f"\n[{v1_report.version_name}]")
    print(f"  정확도: {v1_report.accuracy:.1%} ({v1_correct}/{v1_report.total_cases})")
    print(f"  체크리스트 품질: {v1_report.avg_checklist_score:.1f}/5")
    print(f"  근거 충분성: {v1_report.avg_evidence_score:.1f}/5")
    print(f"  Calibration ECE: {v1_report.calibration.expected_calibration_error:.4f}")

    # Ver 2 요약
    v2_correct = sum(1 for r in v2_report.case_results if r.is_correct)
    print(f"\n[{v2_report.version_name}]")
    print(f"  정확도: {v2_report.accuracy:.1%} ({v2_correct}/{v2_report.total_cases})")
    print(f"  체크리스트 품질: {v2_report.avg_checklist_score:.1f}/5")
    print(f"  근거 충분성: {v2_report.avg_evidence_score:.1f}/5")
    print(f"  Calibration ECE: {v2_report.calibration.expected_calibration_error:.4f}")

    # 개선 효과
    print(f"\n[개선 효과]")

    acc_diff = (v2_report.accuracy - v1_report.accuracy) * 100
    checklist_diff = v2_report.avg_checklist_score - v1_report.avg_checklist_score
    evidence_diff = v2_report.avg_evidence_score - v1_report.avg_evidence_score
    ece_diff = v2_report.calibration.expected_calibration_error - v1_report.calibration.expected_calibration_error

    def format_diff(diff: float, unit: str = "", reverse: bool = False) -> str:
        """차이값 포맷팅 (reverse=True면 낮을수록 좋음)"""
        if reverse:
            if diff < 0:
                return f"\033[92m{diff:+.2f}{unit} (개선)\033[0m"  # 녹색
            elif diff > 0:
                return f"\033[91m{diff:+.2f}{unit} (악화)\033[0m"  # 빨강
        else:
            if diff > 0:
                return f"\033[92m{diff:+.2f}{unit} (개선)\033[0m"  # 녹색
            elif diff < 0:
                return f"\033[91m{diff:+.2f}{unit} (악화)\033[0m"  # 빨강
        return f"{diff:+.2f}{unit}"

    print(f"  정확도: {format_diff(acc_diff, '%p')}")
    print(f"  체크리스트: {format_diff(checklist_diff, '점')}")
    print(f"  근거: {format_diff(evidence_diff, '점')}")
    print(f"  Calibration: {format_diff(ece_diff, '', reverse=True)}")

    # 케이스별 비교 (불일치 케이스)
    print(f"\n[케이스별 비교 - 불일치 항목]")
    has_diff = False
    for r1, r2 in zip(v1_report.case_results, v2_report.case_results):
        if r1.is_correct != r2.is_correct:
            has_diff = True
            v1_status = "✅" if r1.is_correct else "❌"
            v2_status = "✅" if r2.is_correct else "❌"
            print(f"  Case {r1.case_id}: V1 {v1_status} → V2 {v2_status}")
            print(f"    \"{r1.claim[:40]}...\"")
            print(f"    정답: {r1.ground_truth}")

    if not has_diff:
        print("  (모든 케이스에서 V1과 V2의 정오답이 동일)")


# ============================================================
# 테스트용 실행
# ============================================================

if __name__ == "__main__":
    from evaluators.calibration import CalibrationResult

    # 테스트 데이터
    test_cases = [
        CaseResult(
            case_id=1,
            claim="대한민국의 수도는 서울이다",
            ground_truth="TRUE",
            predicted="TRUE",
            is_correct=True,
            confidence=0.95,
            checklist_score=5,
            evidence_score=4,
        ),
        CaseResult(
            case_id=2,
            claim="만리장성은 우주에서 보인다",
            ground_truth="FALSE",
            predicted="TRUE",
            is_correct=False,
            confidence=0.80,
            checklist_score=4,
            evidence_score=3,
        ),
    ]

    calibration = CalibrationResult(
        expected_calibration_error=0.12,
        overconfident_count=1,
        underconfident_count=0,
        total_cases=2,
        bins=[],
    )

    report = generate_report("Ver 1 - Baseline (gpt-4o)", test_cases, calibration)
    print(f"✅ 리포트 생성 완료: {report.version_name} ({report.total_cases}개 케이스)")
