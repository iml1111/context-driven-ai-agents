"""
Chapter 13: Evaluators - L1: Accuracy (Exact Match)

verdict가 ground_truth와 정확히 일치하는지 평가합니다.
"""

from pydantic import BaseModel


class AccuracyResult(BaseModel):
    """정확도 평가 결과"""

    is_correct: bool
    predicted: str  # 예측된 verdict
    expected: str  # 정답 (ground_truth)


class AccuracyEvaluator:
    """
    L1: Exact Match 평가기

    verdict가 ground_truth와 정확히 일치하는지 평가합니다.
    """

    def evaluate(self, predicted_verdict: str, ground_truth: str) -> AccuracyResult:
        """
        정확도 평가

        Args:
            predicted_verdict: 모델이 예측한 verdict
            ground_truth: 정답 라벨

        Returns:
            AccuracyResult: 평가 결과
        """
        # 문자열 정규화 (대문자로 통일)
        predicted_normalized = predicted_verdict.strip().upper()
        expected_normalized = ground_truth.strip().upper()

        # Enum 값 변환 처리 (Verdict.TRUE -> "TRUE")
        if "." in predicted_normalized:
            predicted_normalized = predicted_normalized.split(".")[-1]
        if "." in expected_normalized:
            expected_normalized = expected_normalized.split(".")[-1]

        is_correct = predicted_normalized == expected_normalized

        return AccuracyResult(
            is_correct=is_correct,
            predicted=predicted_normalized,
            expected=expected_normalized,
        )


if __name__ == "__main__":
    # 테스트
    test_cases = [
        ("TRUE", "TRUE"),
        ("FALSE", "TRUE"),
        ("PARTIALLY_TRUE", "PARTIALLY_TRUE"),
        ("UNVERIFIABLE", "FALSE"),
    ]

    print("L1: Accuracy 평가 테스트")
    print("-" * 40)

    evaluator = AccuracyEvaluator()
    results = []

    for predicted, expected in test_cases:
        result = evaluator.evaluate(predicted, expected)
        results.append(result)
        status = "✅" if result.is_correct else "❌"
        print(f"{status} {predicted} vs {expected}")

    correct_count = sum(1 for r in results if r.is_correct)
    print(f"\n정확도: {correct_count / len(results):.1%}")
