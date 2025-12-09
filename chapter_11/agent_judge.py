"""
JudgeAgent: 토론 판사 에이전트

토론을 조율하고, 발언자를 선택하며, 최종 판정을 내리는 역할.
Supervisor 패턴의 중심 에이전트.
"""

import json

# =============================================================================
# 프롬프트 템플릿 상수
# =============================================================================

HANDLE_MESSAGE_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 메모
{private_context}

## 수신한 메시지
{message_text}

적절한 응답을 작성하세요."""

OPENING_STATEMENT_PROMPT_TEMPLATE = """\
토론 주제: "{topic}"

토론 개회를 선언하세요. 다음을 포함하세요:
1. 주제 소개
2. 토론 규칙 간략 안내
3. PRO 측과 CON 측 소개
4. 개회사

간결하게 3-4문장으로 작성하세요."""

EVALUATE_DEBATE_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 평가 메모 (이전 라운드)
{private_context}

## 평가 요청
현재까지의 토론을 평가하고, 토론을 계속할지 결정하세요.
이전 메모를 참고하되, 새로운 발언에 따라 판단이 바뀔 수 있습니다.

다음 JSON 형식으로 응답하세요:
{{
    "should_continue": true/false,
    "reason": "계속/종료 이유 (1-2문장)",
    "evaluation_note": "현재까지 평가 메모 (내 참고용, 이전 메모 대비 변화 포함)"
}}

### 종료 조건
- 양측의 핵심 논점이 충분히 다뤄졌다고 판단될 때
- 논쟁이 반복되거나 새로운 논점 없이 순환할 때
- 한쪽이 결정적으로 논파당했을 때

### 계속 조건
- 아직 다뤄지지 않은 중요한 논점이 있을 때
- 반박에 대한 재반박이 필요할 때
- 토론이 생산적으로 진행 중일 때"""

FINAL_JUDGMENT_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 내 평가 메모
{private_context}

## 최종 판정 요청
토론을 종합하여 최종 판정을 내리세요.

다음을 포함하세요:
1. **승자 선언**: PRO 또는 CON (또는 무승부)
2. **판정 근거**: 왜 해당 측이 승리했는지 (3-4문장)
3. **양측 평가**:
   - PRO 측의 강점과 약점
   - CON 측의 강점과 약점
4. **마무리 멘트**

공정하고 상세한 판정문을 작성하세요."""

SELECT_SPEAKER_PROMPT_TEMPLATE = """\
## 토론 히스토리
{main_context}

## 참가자 정보
### PRO 측
- 이름: {pro_name}
- 설명: {pro_description}
- 발언 희망: {pro_wants}
- 누적 발언 횟수: {pro_count}

### CON 측
- 이름: {con_name}
- 설명: {con_description}
- 발언 희망: {con_wants}
- 누적 발언 횟수: {con_count}

## 요청
다음 발언자를 선택하세요.

### 판단 기준
1. 발언 희망 여부 (희망하지 않는 측은 선택 불가)
2. 토론 흐름상 누구의 발언이 더 필요한가
3. 직전 발언에 대한 반박이 필요한가
4. 양측 발언 기회의 균형

다음 JSON 형식으로 응답하세요:
{{
    "selected": "PRO" | "CON" | null,
    "reason": "선택 이유 (1-2문장)",
    "announcement": "발언자 지정 안내 멘트"
}}

- 양측 모두 발언 희망이 없으면 selected는 null
- announcement는 토론 참가자에게 전달될 공식 멘트"""

from openai import OpenAI

from base_agent import BaseAgent
from context_manager import ContextManager
from protocol import (
    AgentCard,
    AgentRole,
    DebateMessage,
    Message,
    create_debate_message,
)


class JudgeAgent(BaseAgent):
    """
    토론 판사 에이전트

    역할:
    - 토론 개회 및 주제 소개
    - 발언 희망자 확인 및 발언자 선택
    - 토론 진행 평가 및 종료 결정
    - 최종 판정 및 승자 선언
    """

    SYSTEM_PROMPT = """당신은 공정하고 중립적인 토론 판사입니다.

## 역할
- 토론의 원활한 진행을 조율합니다
- 양측의 발언 기회를 균형 있게 배분합니다
- 논쟁의 질과 깊이를 평가합니다
- 토론 종료 시점을 결정합니다
- 최종적으로 승자를 판정합니다

## 평가 기준
1. **논거의 타당성**: 주장을 뒷받침하는 근거의 질
2. **논리적 일관성**: 주장 간의 모순 없음
3. **반박의 효과성**: 상대 주장에 대한 효과적인 대응
4. **증거 활용**: 사실적 근거나 예시의 적절한 활용
5. **설득력**: 전체적인 논증의 설득력

## 행동 지침
- 항상 중립적인 입장을 유지하세요
- 개인적 의견을 배제하고 논증의 질만 평가하세요
- 명확하고 간결하게 소통하세요
- 토론이 생산적으로 진행되도록 필요시 개입하세요"""

    def __init__(
        self,
        client: OpenAI,
        context_manager: ContextManager,
    ) -> None:
        super().__init__(client, AgentRole.JUDGE, context_manager)
        self.system_prompt = self.SYSTEM_PROMPT

    def _create_agent_card(self) -> AgentCard:
        return AgentCard(
            name="Judge",
            description="공정하고 중립적인 토론 판사. 토론을 조율하고 최종 판정을 내립니다.",
        )

    def handle_message(self, message: Message) -> DebateMessage:
        """일반 메시지 처리 (판사의 응답)"""
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = HANDLE_MESSAGE_PROMPT_TEMPLATE.format(
            main_context=main_context,
            private_context=private_context,
            message_text=message.get_text(),
        )

        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        response_text = response.choices[0].message.content or ""

        return create_debate_message(
            role=self.role,
            text=response_text,
            should_continue=True,
            want_to_speak=False,
        )

    def opening_statement(self, topic: str) -> DebateMessage:
        """토론 개회 선언"""
        prompt = OPENING_STATEMENT_PROMPT_TEMPLATE.format(topic=topic)

        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        response_text = response.choices[0].message.content or ""

        return create_debate_message(
            role=self.role,
            text=response_text,
            should_continue=True,
            want_to_speak=False,
        )

    def ask_who_wants_to_speak(
        self,
        round_num: int,
    ) -> DebateMessage:
        """발언 희망자 질문"""
        text = f"[라운드 {round_num}] 발언을 희망하는 측이 있습니까? PRO 또는 CON, 발언 의사를 밝혀주세요."

        return create_debate_message(
            role=self.role,
            text=text,
            should_continue=True,
            want_to_speak=False,
        )

    def select_next_speaker(
        self,
        pro_card: AgentCard,
        con_card: AgentCard,
        pro_wants: bool,
        con_wants: bool,
        pro_count: int,
        con_count: int,
    ) -> tuple[AgentRole | None, DebateMessage]:
        """
        다음 발언자 선택 (LLM 기반 자율 판단)

        Args:
            pro_card: PRO 에이전트 카드
            con_card: CON 에이전트 카드
            pro_wants: PRO 발언 희망 여부
            con_wants: CON 발언 희망 여부
            pro_count: PRO 누적 발언 횟수
            con_count: CON 누적 발언 횟수

        Returns:
            (선택된 발언자 역할, 선택 메시지)
            발언자가 없으면 (None, 종료 안내 메시지)
        """
        main_context = self.get_main_context()

        prompt = SELECT_SPEAKER_PROMPT_TEMPLATE.format(
            main_context=main_context,
            pro_name=pro_card.name,
            pro_description=pro_card.description,
            pro_wants="예" if pro_wants else "아니오",
            pro_count=pro_count,
            con_name=con_card.name,
            con_description=con_card.description,
            con_wants="예" if con_wants else "아니오",
            con_count=con_count,
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
        selected_str = result.get("selected")
        announcement = result.get("announcement", "")

        # 선택 결과 매핑
        if selected_str == "PRO":
            selected = AgentRole.DEBATER_PRO
            should_continue = True
        elif selected_str == "CON":
            selected = AgentRole.DEBATER_CON
            should_continue = True
        else:
            selected = None
            should_continue = False
            if not announcement:
                announcement = "양측 모두 추가 발언 의사가 없습니다. 마무리 발언으로 넘어가겠습니다."

        return selected, create_debate_message(
            role=self.role,
            text=announcement,
            should_continue=should_continue,
            want_to_speak=False,
        )

    def evaluate_debate(self) -> tuple[bool, DebateMessage]:
        """
        현재 토론 상태 평가 및 계속 여부 결정

        Returns:
            (계속 여부, 평가 메시지)
        """
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = EVALUATE_DEBATE_PROMPT_TEMPLATE.format(
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
        should_continue = result.get("should_continue", True)
        reason = result.get("reason", "")
        eval_note = result.get("evaluation_note", "")

        # 비공개 메모 업데이트
        self.update_private_context(f"평가 메모: {eval_note}")

        message = create_debate_message(
            role=self.role,
            text=f"[판사 평가] {reason}",
            should_continue=should_continue,
            want_to_speak=False,
        )

        return should_continue, message

    def request_closing_statement(
        self,
        target: AgentRole,
    ) -> DebateMessage:
        """마무리 발언 요청"""
        side = "PRO" if target == AgentRole.DEBATER_PRO else "CON"
        text = f"{side} 측, 마무리 발언을 해주세요. 핵심 주장을 요약하고 마지막 어필을 하세요."

        return create_debate_message(
            role=self.role,
            text=text,
            should_continue=True,
            want_to_speak=False,
        )

    def final_judgment(self) -> DebateMessage:
        """
        최종 판정

        Returns:
            최종 판정 메시지
        """
        main_context = self.get_main_context()
        private_context = self.get_private_context()

        prompt = FINAL_JUDGMENT_PROMPT_TEMPLATE.format(
            main_context=main_context,
            private_context=private_context,
        )

        response = self.client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )

        response_text = response.choices[0].message.content or ""

        return create_debate_message(
            role=self.role,
            text=response_text,
            should_continue=False,
            want_to_speak=False,
        )
