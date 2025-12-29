"""
요약 기반 메모리 관리 심리 상담 챗봇
"""

COUNSELOR_PROMPT = """
[역할]
당신은 공감적이고 전문적인 심리 상담사입니다.

[목표]
내담자의 이야기를 경청하고, 감정을 이해하며, 적절한 질문과 조언을 제공하시오.

[제약사항]
- 판단하거나 비난하지 말 것
- 내담자의 감정을 먼저 공감하고 인정할 것
- 구체적인 질문을 통해 상황을 명확히 파악할 것
- 실행 가능한 작은 단계부터 제안할 것
- 전문적이지만 따뜻한 어조 유지

[출력]
내담자에게 도움이 되는 2-3문장의 응답
"""

SUMMARIZER_PROMPT = """
[역할]
당신은 심리 상담 대화 기록을 요약하는 전문가입니다.

[목표]
이전 상담 대화 내용을 핵심만 남겨 간결하게 요약하시오.

[제약사항]
- 내담자가 호소한 핵심 문제를 반드시 포함
- 언급된 구체적 사건, 감정, 과거 경험 보존
- 상담사의 개입 내용은 생략 가능
- 3-5문장으로 압축
- 시간 순서 유지

[출력]
간결한 대화 요약 (3-5문장)
"""


class MemoryCounselor:
    """
    요약 기반 메모리 관리를 사용하는 심리 상담 챗봇
    """

    def __init__(self, client, summary_threshold=2000, recent_turns=5):
        """
        Args:
            client: OpenAI 클라이언트
            summary_threshold: 요약 트리거 토큰 임계값
            recent_turns: 원본으로 유지할 최근 대화 턴 수
        """
        self.client = client
        self.summary_threshold = summary_threshold
        self.recent_turns = recent_turns
        self.conversation_history = []  # {"role": "user"/"assistant", "content": "..."}
        self.conversation_summary = None  # 요약된 이전 대화 (str 또는 None)

    def chat(self, user_message):
        """
        사용자 메시지를 받아 상담 응답 생성

        Args:
            user_message: 사용자의 입력 메시지

        Returns:
            str: 상담사의 응답
        """
        # 1. 사용자 메시지를 히스토리에 추가
        self.conversation_history.append({"role": "user", "content": user_message})

        # 2. 요약이 필요한지 확인
        if self._should_summarize():
            print("\n⚡ 메모리 압축 중... (요약 생성)")
            self._create_summary()

        # 3. 컨텍스트 구성 (요약 + 최근 대화)
        context = self._build_context()

        # 4. LLM으로 응답 생성
        response = self.client.responses.create(
            model="gpt-5.1",
            instructions=COUNSELOR_PROMPT,
            input=context,
        )

        assistant_message = response.output[0].content[0].text

        # 5. 응답을 히스토리에 추가
        self.conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )

        return assistant_message

    def _should_summarize(self):
        """
        요약이 필요한지 판단

        Returns:
            bool: 요약 필요 여부
        """
        total_tokens = self._count_tokens()
        has_enough_history = len(self.conversation_history) > self.recent_turns

        return total_tokens > self.summary_threshold and has_enough_history

    def _create_summary(self):
        """
        오래된 대화를 요약하여 메모리 압축

        최근 N턴을 제외한 이전 대화를 LLM으로 요약하고,
        요약된 부분은 히스토리에서 제거
        """
        # 요약할 메시지 (최근 N턴 제외)
        messages_to_summarize = self.conversation_history[: -self.recent_turns]

        if not messages_to_summarize:
            return  # 요약할 내용이 없으면 종료

        # 대화 기록을 텍스트로 변환
        conversation_text = "\n".join(
            [
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages_to_summarize
            ]
        )

        # 기존 요약이 있으면 함께 전달
        if self.conversation_summary:
            conversation_text = f"[기존 요약]\n{self.conversation_summary}\n\n[추가 대화]\n{conversation_text}"

        # LLM으로 요약 생성
        response = self.client.responses.create(
            model="gpt-5.1",
            instructions=SUMMARIZER_PROMPT,
            input=[{"role": "user", "content": conversation_text}],
        )

        # 새 요약 저장
        self.conversation_summary = response.output[0].content[0].text

        # 요약된 부분은 히스토리에서 제거 (최근 N턴만 유지)
        self.conversation_history = self.conversation_history[-self.recent_turns :]

    def _build_context(self):
        """
        요약 + 최근 대화를 조합하여 컨텍스트 구성

        Returns:
            list: LLM에 전달할 메시지 리스트
        """
        context = []

        # 요약이 있으면 시스템 메시지로 추가
        if self.conversation_summary:
            context.append(
                {
                    "role": "system",
                    "content": f"[이전 상담 요약]\n{self.conversation_summary}",
                }
            )

        # 최근 대화 추가
        context.extend(self.conversation_history)

        return context

    def _count_tokens(self):
        """
        현재 컨텍스트의 토큰 수 근사 계산

        Returns:
            int: 추정 토큰 수
        """
        # 단어 수 기반 근사 (한글: 단어당 ~2 토큰, 영어: 단어당 ~1.3 토큰)
        # 간단하게 글자 수 / 2로 근사
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)

        if self.conversation_summary:
            total_chars += len(self.conversation_summary)

        return total_chars // 2  # 글자 수를 2로 나눔 (대략적 토큰 추정)

    def get_stats(self):
        """
        현재 메모리 상태 통계 반환

        Returns:
            dict: 통계 정보
        """
        return {
            "current_tokens": self._count_tokens(),
            "history_length": len(self.conversation_history),
            "has_summary": self.conversation_summary is not None,
            "summary_length": (
                len(self.conversation_summary) if self.conversation_summary else 0
            ),
        }
