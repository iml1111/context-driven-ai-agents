"""
에이전트 간 통신 구조.
핵심 개념: Message, Part, AgentCard
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


# =============================================================================
# Part 타입: 메시지 내용 구성 요소
# =============================================================================

@dataclass
class TextPart:
    """일반 텍스트 발언"""
    text: str
    kind: Literal["text"] = "text"


@dataclass
class DataPart:
    """구조화된 데이터 (전략, 도구 호출 결과 등)"""
    data: dict[str, Any]
    kind: Literal["data"] = "data"


# Part 유니온 타입
Part = TextPart | DataPart


# =============================================================================
# Agent 역할 정의
# =============================================================================

class AgentRole(str, Enum):
    """에이전트 역할 (파일명 매핑 및 메시지 역할)"""
    JUDGE = "judge"
    DEBATER_PRO = "debater_pro"
    DEBATER_CON = "debater_con"


# =============================================================================
# Message: 에이전트 간 통신 단위
# =============================================================================

@dataclass
class Message:
    """
    에이전트 간 통신의 기본 단위 (A2A 영감)

    Attributes:
        role: 발언자 역할 (judge, debater_pro, debater_con)
        parts: 메시지 내용 (TextPart, DataPart 조합)
        message_id: 고유 식별자
        timestamp: 생성 시간
        metadata: 추가 메타데이터
    """
    role: AgentRole
    parts: list[Part]
    message_id: str = field(default_factory=lambda: str(uuid4())[:8])
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_text(self) -> str:
        """모든 TextPart를 결합하여 반환"""
        texts = [p.text for p in self.parts if isinstance(p, TextPart)]
        return "\n".join(texts)

    def get_data(self) -> dict[str, Any]:
        """모든 DataPart를 병합하여 반환"""
        merged: dict[str, Any] = {}
        for p in self.parts:
            if isinstance(p, DataPart):
                merged.update(p.data)
        return merged

    def to_markdown(self) -> str:
        """Markdown 형식으로 직렬화 (파일 저장용)"""
        role_display = {
            AgentRole.JUDGE: "JUDGE",
            AgentRole.DEBATER_PRO: "PRO",
            AgentRole.DEBATER_CON: "CON",
        }
        time_str = self.timestamp.strftime("%H:%M:%S")
        header = f"### [{time_str}] {role_display[self.role]}"

        content_lines = []
        for part in self.parts:
            if isinstance(part, TextPart):
                content_lines.append(part.text)
            elif isinstance(part, DataPart):
                content_lines.append(f"```json\n{part.data}\n```")

        content = "\n".join(content_lines)
        return f"{header}\n{content}\n"


# =============================================================================
# DebateMessage: 토론 특화 메시지
# =============================================================================

@dataclass
class DebateMessage(Message):
    """
    토론 특화 Message 확장

    Attributes:
        should_continue: 토론 계속 의사
        want_to_speak: 발언 희망 여부 (자유 신청용)
    """
    should_continue: bool = True
    want_to_speak: bool = True

    @classmethod
    def from_message(
        cls,
        message: Message,
        should_continue: bool = True,
        want_to_speak: bool = True
    ) -> "DebateMessage":
        """Message를 DebateMessage로 변환"""
        return cls(
            role=message.role,
            parts=message.parts,
            message_id=message.message_id,
            timestamp=message.timestamp,
            metadata=message.metadata,
            should_continue=should_continue,
            want_to_speak=want_to_speak,
        )


# =============================================================================
# AgentCard: 에이전트 자기소개 (능력 선언)
# =============================================================================

@dataclass
class AgentCard:
    """
    에이전트 자기소개

    Attributes:
        name: 에이전트 이름
        description: 역할 설명
    """
    name: str
    description: str


# =============================================================================
# DebateConfig: 토론 설정
# =============================================================================

@dataclass
class DebateConfig:
    """토론 세션 설정"""
    topic: str
    summary_threshold: int = 10000  # 요약 트리거 문자 수
    max_speaking_turns: int = 20  # 안전장치: 최대 발언 횟수


# =============================================================================
# 유틸리티 함수
# =============================================================================

def create_debate_message(
    role: AgentRole,
    text: str,
    should_continue: bool = True,
    want_to_speak: bool = True,
    **metadata: Any
) -> DebateMessage:
    """토론 메시지 생성 헬퍼 (단순 텍스트용)"""
    return DebateMessage(
        role=role,
        parts=[TextPart(text=text)],
        should_continue=should_continue,
        want_to_speak=want_to_speak,
        metadata=metadata,
    )


def create_debate_message_with_data(
    role: AgentRole,
    text: str,
    data: dict[str, Any],
    should_continue: bool = True,
    want_to_speak: bool = True,
    **metadata: Any
) -> DebateMessage:
    """데이터를 포함한 토론 메시지 생성 헬퍼 (tool_calls 등)"""
    return DebateMessage(
        role=role,
        parts=[TextPart(text=text), DataPart(data=data)],
        should_continue=should_continue,
        want_to_speak=want_to_speak,
        metadata=metadata,
    )
