"""
Chapter 13: Evaluators - L4: Confidence Calibration

모델의 confidence가 실제 정확도와 얼마나 일치하는지 분석합니다.
Well-calibrated 모델: confidence=0.9인 예측의 90%가 실제로 정답

ECE (Expected Calibration Error):
- 낮을수록 좋음 (0에 가까울수록 잘 보정됨)
- 높을수록 과신(overconfident) 또는 과소신(underconfident)
"""

from pydantic import BaseModel


class CalibrationResult(BaseModel):
    """Calibration 분석 결과"""

    expected_calibration_error: float  # ECE (0에 가까울수록 좋음)
    overconfident_count: int  # 과신: 높은 confidence + 오답
    underconfident_count: int  # 과소신: 낮은 confidence + 정답
    total_cases: int
    bins: list[dict]  # 구간별 상세 정보


class CalibrationAnalyzer:
    """
    L4: Confidence Calibration 분석기

    모델의 confidence가 실제 정확도와 얼마나 일치하는지 분석합니다.
    """

    def __init__(self, num_bins: int = 5):
        """
        Args:
            num_bins: 구간 수 (기본값: 5)
        """
        self.num_bins = num_bins

    def analyze(self, results: list[tuple[float, bool]]) -> CalibrationResult:
        """
        Calibration 분석

        Args:
            results: (confidence, is_correct) 튜플 리스트

        Returns:
            CalibrationResult: Calibration 분석 결과
        """
        if not results:
            return CalibrationResult(
                expected_calibration_error=0.0,
                overconfident_count=0,
                underconfident_count=0,
                total_cases=0,
                bins=[],
            )

        # 구간 설정 (0.0-0.2, 0.2-0.4, ..., 0.8-1.0)
        bin_boundaries = [i / self.num_bins for i in range(self.num_bins + 1)]
        bins_data = []

        for i in range(self.num_bins):
            lower = bin_boundaries[i]
            upper = bin_boundaries[i + 1]

            # 해당 구간에 속하는 결과 필터링
            bin_results = [
                (conf, correct)
                for conf, correct in results
                if lower <= conf < upper or (i == self.num_bins - 1 and conf == upper)
            ]

            if bin_results:
                avg_confidence = sum(conf for conf, _ in bin_results) / len(bin_results)
                accuracy = sum(1 for _, correct in bin_results if correct) / len(
                    bin_results
                )
                count = len(bin_results)
            else:
                avg_confidence = (lower + upper) / 2
                accuracy = 0.0
                count = 0

            bins_data.append(
                {
                    "range": f"{lower:.1f}-{upper:.1f}",
                    "count": count,
                    "avg_confidence": round(avg_confidence, 3),
                    "accuracy": round(accuracy, 3),
                    "gap": round(abs(avg_confidence - accuracy), 3),
                }
            )

        # ECE (Expected Calibration Error) 계산
        # ECE = sum(|accuracy - confidence| * n_samples) / total_samples
        total = len(results)
        ece = 0.0
        for bin_info in bins_data:
            if bin_info["count"] > 0:
                gap = abs(bin_info["accuracy"] - bin_info["avg_confidence"])
                ece += gap * bin_info["count"] / total

        # 과신/과소신 카운트
        overconfident = 0  # 높은 confidence (>0.7) + 오답
        underconfident = 0  # 낮은 confidence (<0.5) + 정답

        for confidence, is_correct in results:
            if confidence > 0.7 and not is_correct:
                overconfident += 1
            elif confidence < 0.5 and is_correct:
                underconfident += 1

        return CalibrationResult(
            expected_calibration_error=round(ece, 4),
            overconfident_count=overconfident,
            underconfident_count=underconfident,
            total_cases=total,
            bins=bins_data,
        )


if __name__ == "__main__":
    # 테스트 데이터
    test_results = [
        (0.95, True),  # 높은 confidence, 정답 -> Good
        (0.90, True),
        (0.85, False),  # 높은 confidence, 오답 -> Overconfident
        (0.80, True),
        (0.75, True),
        (0.60, True),
        (0.55, False),
        (0.40, True),  # 낮은 confidence, 정답 -> Underconfident
        (0.30, False),
        (0.20, False),
    ]

    print("L4: Confidence Calibration 테스트")
    print("=" * 60)

    analyzer = CalibrationAnalyzer()
    result = analyzer.analyze(test_results)

    # ECE 해석
    ece = result.expected_calibration_error
    if ece < 0.05:
        ece_status = "매우 좋음 (Well-calibrated)"
    elif ece < 0.10:
        ece_status = "좋음"
    elif ece < 0.15:
        ece_status = "보통"
    else:
        ece_status = "개선 필요 (Miscalibrated)"

    print(f"ECE (Expected Calibration Error): {ece:.4f} - {ece_status}")
    print(f"총 케이스: {result.total_cases}")
    print(f"과신 (높은 confidence + 오답): {result.overconfident_count}")
    print(f"과소신 (낮은 confidence + 정답): {result.underconfident_count}")

    print("\n구간별 상세:")
    print(f"{'구간':<12} {'샘플':<8} {'평균 Conf':<12} {'실제 정확도':<12} {'Gap':<8}")
    print("-" * 52)
    for bin_info in result.bins:
        print(
            f"{bin_info['range']:<12} "
            f"{bin_info['count']:<8} "
            f"{bin_info['avg_confidence']:<12.3f} "
            f"{bin_info['accuracy']:<12.3f} "
            f"{bin_info['gap']:<8.3f}"
        )
