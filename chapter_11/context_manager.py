"""
ContextManager: 파일 기반 메모리 관리

.md 파일을 메모리 스토리지로 사용하여 실시간 개발자 가시성 제공.
자동 요약 기능으로 컨텍스트 윈도우 최적화.
"""

from datetime import datetime
from pathlib import Path

from openai import OpenAI

from protocol import AgentRole, DebateConfig, Message

# =============================================================================
# 템플릿 상수
# =============================================================================

MAIN_HEADER_TEMPLATE = """\
# Debate: {topic}

**Started**: {timestamp}

---
"""

SUMMARY_SECTION_TEMPLATE = """\

## [요약: 이전 논의]
{summary}

---
"""

PRIVATE_CONTEXT_HEADER_TEMPLATE = """\
# Private Context: {agent_type}

**Role**: {role_description}

---

## Strategy Notes

"""


class ContextManager:
    """
    파일 기반 컨텍스트 관리자

    - Main Context: 공유 토론 히스토리 (debate_history.md)
    - Private Context: 에이전트별 비공개 메모 (agent_*.md)

    Attributes:
        memory_dir: 메모리 파일 디렉토리
        output_dir: 출력 파일 디렉토리
        client: OpenAI 클라이언트 (요약용)
        config: 토론 설정
    """

    # 파일명 매핑
    MAIN_FILE = "debate_history.md"
    PRIVATE_FILES = {
        AgentRole.JUDGE: "judge_context.md",
        AgentRole.DEBATER_PRO: "debater_pro_context.md",
        AgentRole.DEBATER_CON: "debater_con_context.md",
    }

    def __init__(
        self,
        memory_dir: Path,
        output_dir: Path,
        client: OpenAI,
        config: DebateConfig,
    ) -> None:
        self.memory_dir = memory_dir
        self.output_dir = output_dir
        self.client = client
        self.config = config
        # 디렉토리 생성
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Main Context (공유 토론 히스토리)
    # =========================================================================

    def read_main(self) -> str:
        """공유 토론 히스토리 읽기"""
        path = self.memory_dir / self.MAIN_FILE
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def append_main(self, message: Message) -> None:
        """
        토론 히스토리에 메시지 추가

        Args:
            message: 추가할 메시지

        Note:
            threshold 초과 시 자동 요약 트리거
        """
        path = self.memory_dir / self.MAIN_FILE
        current = self.read_main()

        # 메시지 Markdown 변환 후 추가
        new_content = current + "\n" + message.to_markdown()

        # 요약 체크
        if len(new_content) > self.config.summary_threshold:
            new_content = self._summarize_main(new_content)

        path.write_text(new_content, encoding="utf-8")
        print(f"  📝 [Main Context] {message.role.value} 발언 기록됨")

    def write_main_header(self) -> None:
        """토론 히스토리 헤더 작성 (초기화)"""
        path = self.memory_dir / self.MAIN_FILE
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = MAIN_HEADER_TEMPLATE.format(
            topic=self.config.topic,
            timestamp=timestamp,
        )
        path.write_text(header, encoding="utf-8")

    def _summarize_main(self, content: str) -> str:
        """
        토론 히스토리 요약 (오래된 발언 압축)

        최근 4개 발언은 전문 유지, 이전 발언은 요약.

        Args:
            content: 현재 전체 내용

        Returns:
            요약된 내용
        """
        print("  🔄 [요약 트리거] 컨텍스트 압축 중...")

        # 발언 분리 (### 기준)
        lines = content.split("\n")
        header_lines: list[str] = []
        statements: list[str] = []
        current_statement: list[str] = []

        for line in lines:
            if line.startswith("### ["):
                if current_statement:
                    statements.append("\n".join(current_statement))
                current_statement = [line]
            elif current_statement:
                current_statement.append(line)
            else:
                header_lines.append(line)

        if current_statement:
            statements.append("\n".join(current_statement))

        # 최근 4개 유지, 나머지 요약
        if len(statements) <= 4:
            return content  # 요약 불필요

        to_summarize = statements[:-4]
        to_keep = statements[-4:]

        # LLM 요약
        summary_text = "\n\n".join(to_summarize)
        summary = self._call_summarize_llm(summary_text)

        # 재구성
        header = "\n".join(header_lines)
        summary_section = SUMMARY_SECTION_TEMPLATE.format(summary=summary)
        recent_section = "\n\n".join(to_keep)

        result = header + summary_section + recent_section
        print(f"  ✅ 요약 완료: {len(content)} → {len(result)} 문자")
        return result

    def _call_summarize_llm(self, text: str) -> str:
        """LLM을 사용한 텍스트 요약"""
        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 토론 내용을 간결하게 요약하는 전문가입니다. "
                               "각 측의 핵심 주장과 근거를 300-500자로 압축하세요. "
                               "중립적인 톤을 유지하세요.",
                },
                {
                    "role": "user",
                    "content": f"다음 토론 내용을 요약하세요:\n\n{text}",
                },
            ],
        )
        return response.choices[0].message.content or ""

    # =========================================================================
    # Private Context (에이전트별 비공개 메모)
    # =========================================================================

    def read_private(self, role: AgentRole) -> str:
        """에이전트 비공개 컨텍스트 읽기"""
        path = self.memory_dir / self.PRIVATE_FILES[role]
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def write_private(self, role: AgentRole, content: str) -> None:
        """에이전트 비공개 컨텍스트 덮어쓰기"""
        path = self.memory_dir / self.PRIVATE_FILES[role]
        path.write_text(content, encoding="utf-8")

    def append_private(self, role: AgentRole, entry: str) -> None:
        """에이전트 비공개 컨텍스트에 추가"""
        path = self.memory_dir / self.PRIVATE_FILES[role]
        current = self.read_private(role)
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_entry = f"\n### [{timestamp}]\n{entry}\n"
        path.write_text(current + new_entry, encoding="utf-8")

    def init_private(self, role: AgentRole, role_description: str) -> None:
        """에이전트 비공개 컨텍스트 초기화"""
        path = self.memory_dir / self.PRIVATE_FILES[role]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = PRIVATE_CONTEXT_HEADER_TEMPLATE.format(
            agent_type=role.value,
            role_description=role_description,
            timestamp=timestamp,
        )
        path.write_text(header, encoding="utf-8")

    # =========================================================================
    # Output (최종 결과물)
    # =========================================================================

    def write_summary(self, content: str) -> Path:
        """최종 토론 요약 저장"""
        path = self.output_dir / "debate_summary.md"
        path.write_text(content, encoding="utf-8")
        print(f"  📄 최종 요약 저장: {path}")
        return path

    # =========================================================================
    # Utility
    # =========================================================================

    def clear_all(self) -> None:
        """모든 메모리 파일 삭제 (새 토론 시작용)"""
        for file in self.memory_dir.glob("*.md"):
            file.unlink()

    def get_stats(self) -> dict[str, int]:
        """메모리 통계 반환"""
        stats: dict[str, int] = {}

        main_path = self.memory_dir / self.MAIN_FILE
        if main_path.exists():
            stats["main_context_chars"] = len(main_path.read_text(encoding="utf-8"))

        for role, filename in self.PRIVATE_FILES.items():
            path = self.memory_dir / filename
            if path.exists():
                stats[f"{role.value}_chars"] = len(
                    path.read_text(encoding="utf-8")
                )

        return stats
