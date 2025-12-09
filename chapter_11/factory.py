"""
DebateFactory: 의존성 주입 컨테이너 (Composition Root)

모든 토론 시스템 객체를 생성하고 의존성을 관리하는 팩토리.
main.py에서 이 팩토리를 통해 모든 객체를 조립한다.
"""

from pathlib import Path

from openai import OpenAI

from agent_debater import DebaterAgent
from agent_judge import JudgeAgent
from context_manager import ContextManager
from orchestrator import DebateOrchestrator
from protocol import DebateConfig


class DebateFactory:
    """
    토론 시스템 객체 생성 팩토리 (DI Container)

    모든 의존성을 중앙에서 관리하고 객체를 생성.
    - ContextManager는 싱글톤으로 관리 (모든 에이전트가 공유)
    - 각 에이전트는 필요 시마다 새로 생성

    Attributes:
        client: OpenAI 클라이언트
        config: 토론 설정
        memory_dir: 메모리 파일 디렉토리
        output_dir: 출력 파일 디렉토리
    """

    def __init__(
        self,
        client: OpenAI,
        config: DebateConfig,
        memory_dir: Path,
        output_dir: Path,
    ) -> None:
        self.client = client
        self.config = config
        self.memory_dir = memory_dir
        self.output_dir = output_dir

        # 싱글톤 캐시 (같은 ContextManager 재사용)
        self._context_manager: ContextManager | None = None

    def create_context_manager(self) -> ContextManager:
        """
        ContextManager 생성 (싱글톤)

        모든 에이전트가 동일한 ContextManager를 공유해야 하므로
        최초 호출 시에만 생성하고 이후에는 캐시된 인스턴스 반환.
        """
        if self._context_manager is None:
            self._context_manager = ContextManager(
                memory_dir=self.memory_dir,
                output_dir=self.output_dir,
                client=self.client,
                config=self.config,
            )
        return self._context_manager

    def create_judge_agent(self) -> JudgeAgent:
        """JudgeAgent 생성"""
        return JudgeAgent(
            client=self.client,
            context_manager=self.create_context_manager(),
        )

    def create_debater_pro(self) -> DebaterAgent:
        """Debater PRO 생성"""
        return DebaterAgent(
            client=self.client,
            context_manager=self.create_context_manager(),
            position="PRO",
            topic=self.config.topic,
        )

    def create_debater_con(self) -> DebaterAgent:
        """Debater CON 생성"""
        return DebaterAgent(
            client=self.client,
            context_manager=self.create_context_manager(),
            position="CON",
            topic=self.config.topic,
        )

    def create_orchestrator(self) -> DebateOrchestrator:
        """
        전체 Orchestrator 생성 (모든 의존성 조립)

        Factory의 핵심 메서드. 모든 의존성을 생성하고
        Orchestrator에 주입하여 완전히 조립된 객체 반환.
        """
        return DebateOrchestrator(
            client=self.client,
            config=self.config,
            context_manager=self.create_context_manager(),
            judge=self.create_judge_agent(),
            debater_pro=self.create_debater_pro(),
            debater_con=self.create_debater_con(),
        )
