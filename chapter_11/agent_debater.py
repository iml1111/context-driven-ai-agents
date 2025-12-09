"""
DebaterAgent: 토론자 에이전트

특정 입장(PRO/CON)을 옹호하며 논쟁하는 역할.
web_search 도구를 사용하여 근거를 수집할 수 있음.
"""

import json

# =============================================================================
# 프롬프트 템플릿 상수
# =============================================================================

HANDLE_MESSAGE_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 전략 메모
{private_context}

## 판사 메시지
{message_text}

## 요청
위 맥락을 바탕으로 발언하세요.
- 필요시 web_search로 근거를 수집하세요
- 발언 후 추가 발언 의사를 표시하세요

다음 JSON 형식으로 응답하세요:
{{
    "statement": "발언 내용 (300-500자)",
    "should_continue": true/false,
    "want_to_speak": true/false,
    "strategy_note": "다음 전략 메모 (내 참고용)"
}}"""

OPENING_STATEMENT_PROMPT_TEMPLATE = """\
토론 주제: "{topic}"

개회 발언을 작성하세요.
- {position} 입장에서 핵심 주장을 제시하세요
- 앞으로의 논증 방향을 간략히 예고하세요
- 300-400자 내외로 작성하세요

다음 JSON 형식으로 응답하세요:
{{
    "statement": "개회 발언 내용",
    "strategy_note": "토론 전략 메모"
}}"""

CLOSING_STATEMENT_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 전략 메모
{private_context}

## 마무리 발언 요청
{position} 입장에서 마무리 발언을 작성하세요.

포함할 내용:
1. 핵심 주장 재강조
2. 상대측 반박에 대한 최종 응답
3. 왜 {position} 입장이 옳은지 어필
4. 판사에게 호소

300-400자 내외로 설득력 있게 작성하세요."""

EXPRESS_SPEAKING_INTENT_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 전략 메모
{private_context}

## 질문
현재 토론 상황에서 발언을 희망하십니까?
발언하고 싶은 내용이 있으면 want_to_speak=true, 더 들어보고 싶으면 want_to_speak=false.
토론을 계속하고 싶으면 should_continue=true.

다음 JSON 형식으로 응답하세요:
{{
    "want_to_speak": true/false,
    "should_continue": true/false,
    "reason": "이유 (1문장)"
}}"""

from openai import OpenAI

from base_agent import BaseAgent
from context_manager import ContextManager
from protocol import (
    AgentCard,
    AgentRole,
    DebateMessage,
    Message,
    create_debate_message,
    create_debate_message_with_data,
)


class DebaterAgent(BaseAgent):
    """
    토론자 에이전트

    역할:
    - 할당된 입장(PRO/CON)을 옹호
    - 상대 주장에 대한 반박
    - web_search로 근거 수집
    - 전략적 논쟁 전개

    Attributes:
        position: "PRO" 또는 "CON"
    """

    SYSTEM_PROMPT_TEMPLATE = """당신은 토론에서 {position} 입장을 옹호하는 토론자입니다.

## 역할
- "{topic}" 주제에 대해 {position} 입장을 강력히 옹호합니다
- 논리적이고 설득력 있는 주장을 전개합니다
- 상대측 주장의 약점을 찾아 효과적으로 반박합니다
- 필요시 web_search로 근거를 수집합니다

## 논증 전략
1. **명확한 주장**: 핵심 논점을 명확히 제시
2. **강력한 근거**: 사실, 통계, 전문가 의견으로 뒷받침
3. **효과적인 반박**: 상대 논거의 논리적 허점 지적
4. **설득력 있는 어필**: 청중/판사를 설득하는 화법

## 발언 형식
- 300-500자 내외로 간결하게
- 핵심 주장 → 근거 → 결론 구조
- 감정적이지 않고 논리적으로

## 발언 의사 표시
- 추가 발언이 필요하면 should_continue=True
- 할 말을 다 했으면 should_continue=False
- 발언 기회를 원하면 want_to_speak=True"""

    def __init__(
        self,
        client: OpenAI,
        context_manager: ContextManager,
        position: str,  # "PRO" or "CON"
        topic: str,
    ) -> None:
        self.position = position.upper()
        self.topic = topic

        # AgentRole 결정
        role = (
            AgentRole.DEBATER_PRO
            if self.position == "PRO"
            else AgentRole.DEBATER_CON
        )

        super().__init__(client, role, context_manager)

        # 시스템 프롬프트 설정
        self.system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            position=self.position,
            topic=self.topic,
        )

    def _create_agent_card(self) -> AgentCard:
        return AgentCard(
            name=f"Debater ({self.position})",
            description=f"'{self.topic}'에 대해 {self.position} 입장을 옹호하는 토론자",
        )

    def handle_message(self, message: Message) -> DebateMessage:
        """
        메시지 처리 (발언 생성)

        web_search 도구를 사용하여 근거를 수집하고 발언을 생성합니다.
        """
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = HANDLE_MESSAGE_PROMPT_TEMPLATE.format(
            main_context=main_context,
            private_context=private_context,
            message_text=message.get_text(),
        )

        # Responses API 사용 (web_search 지원)
        response = self.client.responses.create(
            model="gpt-5.1",
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            tools=[{"type": "web_search"}],
        )

        # 응답 파싱
        response_text = response.output_text or "{}"

        # JSON 추출 시도
        try:
            # JSON 블록 찾기
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_str = response_text[json_start:json_end]
            else:
                json_str = response_text

            result = json.loads(json_str)
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값
            result = {
                "statement": response_text[:500],
                "should_continue": True,
                "want_to_speak": True,
                "strategy_note": "",
            }

        statement = result.get("statement", "")
        should_continue = result.get("should_continue", True)
        want_to_speak = result.get("want_to_speak", True)
        strategy_note = result.get("strategy_note", "")

        # 전략 메모 저장
        if strategy_note:
            self.update_private_context(f"전략: {strategy_note}")

        # web_search 사용 기록
        tool_calls = []
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if hasattr(item, "type") and item.type == "web_search_call":
                    tool_calls.append({"type": "web_search", "id": item.id})

        # 메시지 생성
        if tool_calls:
            self.update_private_context(f"검색 사용: {tool_calls}")
            return create_debate_message_with_data(
                role=self.role,
                text=statement,
                data={"tool_calls": tool_calls},
                should_continue=should_continue,
                want_to_speak=want_to_speak,
                tool_calls=tool_calls,
            )
        else:
            return create_debate_message(
                role=self.role,
                text=statement,
                should_continue=should_continue,
                want_to_speak=want_to_speak,
            )

    def opening_statement(self) -> DebateMessage:
        """개회 발언 (입장 표명)"""
        prompt = OPENING_STATEMENT_PROMPT_TEMPLATE.format(
            topic=self.topic,
            position=self.position,
        )

        response = self.client.responses.create(
            model="gpt-5.1",
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            tools=[{"type": "web_search"}],
        )

        response_text = response.output_text or "{}"

        try:
            if "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                result = json.loads(response_text[json_start:json_end])
            else:
                result = {"statement": response_text, "strategy_note": ""}
        except json.JSONDecodeError:
            result = {"statement": response_text[:500], "strategy_note": ""}

        statement = result.get("statement", "")
        strategy_note = result.get("strategy_note", "")

        if strategy_note:
            self.update_private_context(f"초기 전략: {strategy_note}")

        return create_debate_message(
            role=self.role,
            text=statement,
            should_continue=True,
            want_to_speak=True,
        )

    def closing_statement(self) -> DebateMessage:
        """마무리 발언"""
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = CLOSING_STATEMENT_PROMPT_TEMPLATE.format(
            main_context=main_context,
            private_context=private_context,
            position=self.position,
        )

        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        statement = response.choices[0].message.content or ""

        return create_debate_message(
            role=self.role,
            text=statement,
            should_continue=False,
            want_to_speak=False,
        )

    def express_speaking_intent(self) -> DebateMessage:
        """발언 의사 표시 (자유 신청용)"""
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = EXPRESS_SPEAKING_INTENT_PROMPT_TEMPLATE.format(
            main_context=main_context,
            private_context=private_context,
        )

        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content or "{}")
        want_to_speak = result.get("want_to_speak", True)
        should_continue = result.get("should_continue", True)
        reason = result.get("reason", "")

        # 의사 표시 메시지
        if want_to_speak:
            text = f"[{self.position}] 발언을 희망합니다."
        else:
            text = f"[{self.position}] 상대측 발언을 듣겠습니다."

        if reason:
            self.update_private_context(f"발언 의사: {reason}")

        return create_debate_message(
            role=self.role,
            text=text,
            should_continue=should_continue,
            want_to_speak=want_to_speak,
        )
