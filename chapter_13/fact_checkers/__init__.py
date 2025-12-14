"""
Chapter 13: Fact-Checkers - 팩트체커 모듈

두 버전의 팩트체커를 제공합니다:
- V1: Baseline (gpt-4o, 원본 프롬프트)
- V2: Improved (gpt-5.1, 개선된 프롬프트 + Structured Output)
"""

from .v1 import ChecklistItem, FactCheckResult, FactCheckerV1
from .v2 import ChecklistItemV2, FactCheckResultV2, FactCheckerV2

__all__ = [
    # V1: Baseline
    "FactCheckerV1",
    "FactCheckResult",
    "ChecklistItem",
    # V2: Improved
    "FactCheckerV2",
    "FactCheckResultV2",
    "ChecklistItemV2",
]
