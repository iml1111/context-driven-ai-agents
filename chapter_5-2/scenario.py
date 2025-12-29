"""
Learning & Adaptation 실습을 위한 Mock 시나리오

5개의 수학/재무 계산 태스크로 구성:
- 난이도가 점진적으로 증가
- 공통 패턴을 학습하면 후반 태스크의 정확도 향상
- 각 태스크는 question, ground_truth, explanation 포함
"""

TASKS = [
    {
        "question": "200의 15%를 계산하세요.",
        "ground_truth": "30",
        "explanation": "200 × 0.15 = 30"
    },
    {
        "question": "$150에서 20% 할인한 가격을 계산하세요.",
        "ground_truth": "$120",
        "explanation": "할인 금액 = 150 × 0.20 = 30, 최종 가격 = 150 - 30 = 120"
    },
    {
        "question": "$75에 8% 세금을 포함한 최종 가격을 계산하세요.",
        "ground_truth": "$81",
        "explanation": "세금 금액 = 75 × 0.08 = 6, 최종 가격 = 75 + 6 = 81"
    },
    {
        "question": "100이 30% 증가한 후 20% 감소하면 최종 값은 얼마인가요?",
        "ground_truth": "104",
        "explanation": "증가 후 = 100 × 1.30 = 130, 감소 후 = 130 × 0.80 = 104"
    },
    {
        "question": "$200 상품에 10% 세금을 추가하고, 그 결과에서 15% 할인을 적용하면 최종 가격은?",
        "ground_truth": "$187",
        "explanation": "세금 추가 = 200 × 1.10 = 220, 할인 적용 = 220 × 0.85 = 187"
    }
]


def evaluate(answer: str, ground_truth: str) -> bool:
    """
    답변과 정답 비교 (단순 문자열 매칭)

    Args:
        answer: LLM의 답변
        ground_truth: 정답

    Returns:
        정답 여부
    """
    # 공백 제거 후 비교
    answer_clean = answer.strip().replace(" ", "").replace(",", "")
    truth_clean = ground_truth.strip().replace(" ", "").replace(",", "")

    return answer_clean == truth_clean
