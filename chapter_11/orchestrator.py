"""
DebateOrchestrator: 토론 흐름 제어 State Machine

토론의 전체 생명주기를 관리하고 에이전트 간 상호작용을 조율.
"""

from enum import Enum

# =============================================================================
# 템플릿 상수
# =============================================================================

DEBATE_SUMMARY_TEMPLATE = """\
# 토론 요약

## 주제
{topic}

## 참가자
- **PRO (찬성)**: Debater PRO
- **CON (반대)**: Debater CON
- **판사**: Judge

## 통계
- 총 라운드: {round_count}
- PRO 발언 횟수: {pro_speak_count}
- CON 발언 횟수: {con_speak_count}

## 최종 판정

{judgment}

---

## 전체 토론 기록

{main_context}
"""

from openai import OpenAI

from agent_debater import DebaterAgent
from agent_judge import JudgeAgent
from context_manager import ContextManager
from protocol import AgentRole, DebateConfig


class DebateState(str, Enum):
    """토론 상태 (State Machine)"""
    INITIALIZATION = "initialization"
    OPENING_STATEMENTS = "opening_statements"
    FREE_DEBATE = "free_debate"
    JUDGE_EVALUATION = "judge_evaluation"
    CLOSING_STATEMENTS = "closing_statements"
    JUDGMENT = "judgment"
    ENDED = "ended"


class DebateOrchestrator:
    """
    토론 흐름 관리자 (State Machine)

    상태 흐름:
    INITIALIZATION → OPENING_STATEMENTS → FREE_DEBATE ⇄ JUDGE_EVALUATION
                                                      ↓
                          ENDED ← JUDGMENT ← CLOSING_STATEMENTS

    Attributes:
        client: OpenAI 클라이언트
        config: 토론 설정
        context_manager: 컨텍스트 관리자
        state: 현재 상태
        judge: 판사 에이전트
        debater_pro: PRO 토론자
        debater_con: CON 토론자
        round_count: 현재 라운드
        pro_speak_count: PRO 발언 횟수
        con_speak_count: CON 발언 횟수
    """

    def __init__(
        self,
        client: OpenAI,
        config: DebateConfig,
        context_manager: ContextManager,
        judge: JudgeAgent,
        debater_pro: DebaterAgent,
        debater_con: DebaterAgent,
    ) -> None:
        """
        Args:
            client: OpenAI 클라이언트
            config: 토론 설정
            context_manager: 컨텍스트 관리자 (주입)
            judge: 판사 에이전트 (주입)
            debater_pro: PRO 토론자 (주입)
            debater_con: CON 토론자 (주입)
        """
        self.client = client
        self.config = config
        self.context_manager = context_manager
        self.judge = judge
        self.debater_pro = debater_pro
        self.debater_con = debater_con

        # 상태 초기화
        self.state = DebateState.INITIALIZATION
        self.round_count = 0
        self.pro_speak_count = 0
        self.con_speak_count = 0

    def run(self) -> str:
        """
        토론 전체 실행

        Returns:
            최종 판정 내용
        """
        print(f"\n{'='*60}")
        print(f"🎤 토론 시작: {self.config.topic}")
        print(f"{'='*60}\n")

        # 1. 초기화
        self._initialize()

        # 2. 개회 발언
        self._opening_statements()

        # 3. 자유 토론 루프
        while self.state not in [DebateState.CLOSING_STATEMENTS, DebateState.ENDED]:
            self._free_debate_round()

            # 판사 평가
            if self.state == DebateState.JUDGE_EVALUATION:
                should_continue = self._judge_evaluation()
                if not should_continue:
                    self.state = DebateState.CLOSING_STATEMENTS
                else:
                    self.state = DebateState.FREE_DEBATE

            # 안전장치: 최대 발언 횟수 체크 (or HITL)
            total_speaks = self.pro_speak_count + self.con_speak_count
            if total_speaks >= self.config.max_speaking_turns:
                print(f"\n⚠️ 최대 발언 횟수({self.config.max_speaking_turns}) 도달, 강제 루프 종료 처리.")
                self.state = DebateState.CLOSING_STATEMENTS
                break

        # 4. 마무리 발언
        if self.state == DebateState.CLOSING_STATEMENTS:
            self._closing_statements()

        # 5. 최종 판정
        self.state = DebateState.JUDGMENT
        result = self._final_judgment()

        # 6. 종료
        self.state = DebateState.ENDED
        print(f"\n{'='*60}")
        print("🏁 토론 종료")
        print(f"{'='*60}\n")

        # 통계 출력
        stats = self.context_manager.get_stats()
        print(f"📊 통계: PRO {self.pro_speak_count}회, CON {self.con_speak_count}회 발언")
        print(f"📊 컨텍스트: {stats}")

        return result

    def _initialize(self) -> None:
        """초기화 단계"""
        print("📋 [INITIALIZATION] 토론 초기화 중...")

        # 메모리 초기화
        self.context_manager.clear_all()

        # 헤더 작성
        self.context_manager.write_main_header()

        # 에이전트 비공개 컨텍스트 초기화
        self.context_manager.init_private(
            AgentRole.JUDGE,
            "공정하고 중립적인 토론 판사"
        )
        self.context_manager.init_private(
            AgentRole.DEBATER_PRO,
            f"'{self.config.topic}'에 대해 PRO(찬성) 입장 옹호"
        )
        self.context_manager.init_private(
            AgentRole.DEBATER_CON,
            f"'{self.config.topic}'에 대해 CON(반대) 입장 옹호"
        )

        self.state = DebateState.OPENING_STATEMENTS
        print("  ✅ 초기화 완료\n")

    def _opening_statements(self) -> None:
        """개회 발언 단계"""
        print("🎙️ [OPENING_STATEMENTS] 개회 발언")

        # 판사 개회 선언
        print("\n  👨‍⚖️ [JUDGE] 개회 선언...")
        judge_opening = self.judge.opening_statement(self.config.topic)
        self.context_manager.append_main(judge_opening)
        print(f"    → {judge_opening.get_text()}")

        # PRO 개회 발언
        print("\n  🟢 [PRO] 개회 발언...")
        pro_opening = self.debater_pro.opening_statement()
        self.context_manager.append_main(pro_opening)
        self.pro_speak_count += 1
        print(f"    → {pro_opening.get_text()}")

        # CON 개회 발언
        print("\n  🔴 [CON] 개회 발언...")
        con_opening = self.debater_con.opening_statement()
        self.context_manager.append_main(con_opening)
        self.con_speak_count += 1
        print(f"    → {con_opening.get_text()}")

        self.state = DebateState.FREE_DEBATE
        print("\n  ✅ 개회 발언 완료\n")

    def _free_debate_round(self) -> None:
        """자유 토론 1라운드"""
        self.round_count += 1
        print(f"\n🔄 [FREE_DEBATE] 라운드 {self.round_count}")

        # 1. 판사가 발언 희망자 질문
        ask_msg = self.judge.ask_who_wants_to_speak(self.round_count)
        print(f"  👨‍⚖️ {ask_msg.get_text()}")

        # 2. 각 토론자 발언 의사 확인
        print("  🟢 [PRO] 발언 의사 확인 중...")
        pro_intent = self.debater_pro.express_speaking_intent()
        print(f"    → want_to_speak={pro_intent.want_to_speak}, should_continue={pro_intent.should_continue}")

        print("  🔴 [CON] 발언 의사 확인 중...")
        con_intent = self.debater_con.express_speaking_intent()
        print(f"    → want_to_speak={con_intent.want_to_speak}, should_continue={con_intent.should_continue}")

        # 3. 양측 모두 계속 의사 없으면 종료
        if not pro_intent.should_continue and not con_intent.should_continue:
            print("  ⚠️ 양측 모두 토론 종료 의사 표명")
            self.state = DebateState.CLOSING_STATEMENTS
            return

        # 4. 판사가 다음 발언자 선택
        selected_role, select_msg = self.judge.select_next_speaker(
            pro_card=self.debater_pro.agent_card,
            con_card=self.debater_con.agent_card,
            pro_wants=pro_intent.want_to_speak,
            con_wants=con_intent.want_to_speak,
            pro_count=self.pro_speak_count,
            con_count=self.con_speak_count,
        )
        self.context_manager.append_main(select_msg)
        print(f"  👨‍⚖️ {select_msg.get_text()}")

        # 발언자 없으면 종료
        if selected_role is None:
            self.state = DebateState.CLOSING_STATEMENTS
            return

        # 5. 선택된 토론자 발언
        if selected_role == AgentRole.DEBATER_PRO:
            print("\n  🟢 [PRO] 발언 중...")
            response = self.debater_pro.handle_message(select_msg)
            self.pro_speak_count += 1
        else:
            print("\n  🔴 [CON] 발언 중...")
            response = self.debater_con.handle_message(select_msg)
            self.con_speak_count += 1

        self.context_manager.append_main(response)
        print(f"    → {response.get_text()}")

        # tool_calls 로깅
        if response.metadata.get("tool_calls"):
            print(f"    🔍 web_search 사용: {response.metadata['tool_calls']}")

        # 6. 판사 평가로 전이
        self.state = DebateState.JUDGE_EVALUATION

    def _judge_evaluation(self) -> bool:
        """
        판사 평가

        Returns:
            True: 토론 계속, False: 종료
        """
        print("\n  👨‍⚖️ [JUDGE] 평가 중...")
        should_continue, eval_msg = self.judge.evaluate_debate()
        print(f"    → should_continue={should_continue}")
        print(f"    → {eval_msg.get_text()}")

        # 평가 메시지는 메인 컨텍스트에 기록하지 않음 (판사 비공개)
        return should_continue

    def _closing_statements(self) -> None:
        """마무리 발언 단계"""
        print("\n📝 [CLOSING_STATEMENTS] 마무리 발언")

        # PRO 마무리 요청
        pro_request = self.judge.request_closing_statement(AgentRole.DEBATER_PRO)
        self.context_manager.append_main(pro_request)

        print("\n  🟢 [PRO] 마무리 발언...")
        pro_closing = self.debater_pro.closing_statement()
        self.context_manager.append_main(pro_closing)
        print(f"    → {pro_closing.get_text()}")

        # CON 마무리 요청
        con_request = self.judge.request_closing_statement(AgentRole.DEBATER_CON)
        self.context_manager.append_main(con_request)

        print("\n  🔴 [CON] 마무리 발언...")
        con_closing = self.debater_con.closing_statement()
        self.context_manager.append_main(con_closing)
        print(f"    → {con_closing.get_text()}")

        print("\n  ✅ 마무리 발언 완료")

    def _final_judgment(self) -> str:
        """
        최종 판정

        Returns:
            판정문 내용
        """
        print("\n⚖️ [JUDGMENT] 최종 판정")

        judgment_msg = self.judge.final_judgment()
        self.context_manager.append_main(judgment_msg)

        judgment_text = judgment_msg.get_text()
        print(f"\n{judgment_text}")

        # 최종 요약 저장
        summary_content = self._generate_summary(judgment_text)
        summary_path = self.context_manager.write_summary(summary_content)

        return judgment_text

    def _generate_summary(self, judgment: str) -> str:
        """최종 요약 문서 생성"""
        main_context = self.context_manager.read_main()

        return DEBATE_SUMMARY_TEMPLATE.format(
            topic=self.config.topic,
            round_count=self.round_count,
            pro_speak_count=self.pro_speak_count,
            con_speak_count=self.con_speak_count,
            judgment=judgment,
            main_context=main_context,
        )
