"""
플레이북 데이터 구조 및 관리

Playbook: 학습된 전략/공식/예시를 구조화된 항목으로 저장
- 각 항목은 category, content를 가짐
- 순차적 ID 부여 (item-001, item-002, ...)
- JSON 저장/로드 기능 제공
"""

import json
from dataclasses import dataclass, asdict
from typing import List
from pathlib import Path


@dataclass
class PlaybookItem:
    """플레이북 개별 항목"""
    id: str
    category: str  # strategy, formula, example
    content: str


class Playbook:
    """플레이북: 학습된 지식을 구조화하여 저장"""

    def __init__(self):
        self.items: List[PlaybookItem] = []
        self._next_id = 1

    def add(self, item: PlaybookItem) -> None:
        """새로운 항목 추가"""
        self.items.append(item)

    def get_all(self) -> List[PlaybookItem]:
        """모든 항목 반환"""
        return self.items

    def generate_id(self) -> str:
        """새 항목 ID 생성 (순차적)"""
        item_id = f"item-{self._next_id:03d}"
        self._next_id += 1
        return item_id

    def format_for_prompt(self) -> str:
        """LLM 프롬프트에 삽입할 형식으로 변환"""
        if not self.items:
            return "현재 플레이북이 비어있습니다."

        formatted = "## 📚 학습된 플레이북\n\n"

        # 카테고리별로 그룹화
        by_category = {}
        for item in self.items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)

        # 카테고리별 출력
        category_names = {
            "strategy": "전략",
            "formula": "공식",
            "example": "예시"
        }

        for cat, items in by_category.items():
            cat_name = category_names.get(cat, cat)
            formatted += f"### {cat_name}\n"
            for item in items:
                formatted += f"- [{item.id}] {item.content}\n"
            formatted += "\n"

        return formatted

    def save(self, filepath: str) -> None:
        """플레이북을 JSON 파일로 저장"""
        data = {
            "items": [asdict(item) for item in self.items],
            "total_count": len(self.items)
        }

        Path(filepath).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load(self, filepath: str) -> None:
        """JSON 파일에서 플레이북 로드"""
        data = json.loads(Path(filepath).read_text(encoding="utf-8"))
        self.items = [PlaybookItem(**item) for item in data["items"]]

        # 다음 ID 계산
        if self.items:
            max_id = max(int(item.id.split("-")[1]) for item in self.items)
            self._next_id = max_id + 1
