"""
BaseAgent: 모든 에이전트의 추상 기반 클래스
클래스 기반 아키텍처로 확장성 있는 에이전트 구조 정의.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from openai import OpenAI

from protocol import AgentCard, AgentRole, DebateMessage, Message

if TYPE_CHECKING:
    from context_manager import ContextManager


class BaseAgent(ABC):
    """
    모든 토론 에이전트의 추상 기반 클래스

    Attributes:
        client: OpenAI 클라이언트
        role: 에이전트 역할
        agent_card: 에이전트의 자기소개 카드
        context_manager: 컨텍스트 관리자 (파일 I/O)
        system_prompt: 시스템 프롬프트
    """

    def __init__(
        self,
        client: OpenAI,
        role: AgentRole,
        context_manager: "ContextManager",
    ) -> None:
        self.client = client
        self.role = role
        self.context_manager = context_manager
        self.system_prompt: str = ""
        self.agent_card: AgentCard = self._create_agent_card()

    @abstractmethod
    def _create_agent_card(self) -> AgentCard:
        """
        에이전트 카드 생성 (서브클래스에서 구현)

        Returns:
            AgentCard: 에이전트 자기소개 정보
        """
        pass

    @abstractmethod
    def handle_message(self, message: Message) -> DebateMessage:
        """
        들어온 메시지 처리 → 새 메시지 반환

        Args:
            message: 수신한 메시지 (판사의 질문 또는 상대 발언)

        Returns:
            DebateMessage: 처리 결과 메시지
        """
        pass

    def get_private_context(self) -> str:
        """에이전트의 비공개 컨텍스트 조회"""
        return self.context_manager.read_private(self.role)

    def get_main_context(self) -> str:
        """공유 토론 히스토리 조회"""
        return self.context_manager.read_main()

    def update_private_context(self, content: str) -> None:
        """
        비공개 컨텍스트 업데이트 (추가)

        Args:
            content: 추가할 내용 (전략, 메모 등)
        """
        self.context_manager.append_private(self.role, content)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role={self.role.value})"
