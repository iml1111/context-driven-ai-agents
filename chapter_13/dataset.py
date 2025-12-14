"""
Chapter 13: Dataset - 평가 데이터 모델 및 로더

평가 케이스의 데이터 구조와 JSONL 파일 로딩 기능을 제공합니다.
"""

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class Verdict(str, Enum):
    """팩트체크 판정 결과"""

    TRUE = "TRUE"
    FALSE = "FALSE"
    PARTIALLY_TRUE = "PARTIALLY_TRUE"
    UNVERIFIABLE = "UNVERIFIABLE"


class EvalCase(BaseModel):
    """평가 케이스 단위"""

    claim: str  # 검증할 정보
    ground_truth: Verdict  # 정답 라벨
    difficulty: str = "medium"  # easy/medium/hard
    category: str = "general"  # 카테고리 (상식, 과학, 역사, 건강 등)


def load_dataset(filepath: str = "eval_data.jsonl") -> list[EvalCase]:
    """
    JSONL 파일에서 평가 데이터셋 로드

    Args:
        filepath: JSONL 파일 경로 (기본값: eval_data.jsonl)

    Returns:
        EvalCase 리스트
    """
    # 상대 경로인 경우 현재 파일 기준으로 절대 경로 생성
    if not Path(filepath).is_absolute():
        filepath = Path(__file__).parent / filepath

    cases = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                cases.append(EvalCase(**data))

    return cases


if __name__ == "__main__":
    # 테스트용 실행
    try:
        cases = load_dataset()
        print(f"✅ 데이터셋 로드 완료: {len(cases)}개 케이스")
    except FileNotFoundError:
        print("eval_data.jsonl 파일을 찾을 수 없습니다.")
