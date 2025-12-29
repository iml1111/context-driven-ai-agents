"""
Chapter 7-1: Tool 컨셉 - 여행 준비 도우미 에이전트

OpenAI Function Calling(Tools) API를 활용한 에이전트 구현:
1. Tool Definition: JSON Schema 기반 도구 정의
2. LLM 의사결정: LLM이 스스로 어떤 도구를 호출할지 판단
3. Tool Execution Loop: tool_calls → 실행 → 결과 전달 → 최종 응답

실행: python chapter_7-1/main.py
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOLS, execute_tool

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """당신은 여행 준비를 도와주는 친절한 여행 도우미입니다.

사용 가능한 도구:
1. get_weather: 서울, 도쿄, 상하이의 날씨 정보 조회
2. get_exchange_rate: KRW(한국 원), JPY(일본 엔), CNY(중국 위안) 환율 조회

사용자의 여행 관련 질문에 적절한 도구를 사용하여 정확한 정보를 제공하세요.
정보를 조회한 후에는 친절하고 유용한 여행 팁도 함께 알려주세요.
"""


# ============================================================
# Tool Loop 구현
# ============================================================


def run_travel_agent(user_message: str) -> str:
    """
    Tool Loop 패턴으로 여행 도우미 에이전트를 실행합니다.

    Args:
        user_message: 사용자 입력 메시지

    Returns:
        에이전트의 최종 응답
    """
    print(f"💬 사용자: {user_message}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    iteration = 0
    max_iterations = 5  # 무한 루프 방지

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🤖 LLM 호출 #{iteration}...")

        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            tools=TOOLS,
        )

        choice = response.choices[0]
        assistant_message = choice.message

        # -------- Case 1: Tool 호출 없이 최종 응답 --------
        if choice.finish_reason == "stop":
            print("✅ 최종 응답 생성 완료")
            return assistant_message.content

        # -------- Case 2: Tool 호출 필요 --------
        if assistant_message.tool_calls:
            print(f"🔧 Tool 호출 감지: {len(assistant_message.tool_calls)}개")

            # Assistant 메시지를 먼저 추가 (tool_calls 포함)
            messages.append(assistant_message)

            # 각 Tool 실행 및 결과 추가
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"   → {func_name}({func_args})")

                # Tool 실행
                result = execute_tool(func_name, func_args)
                print(f"   📊 결과: {result}")

                # Tool 결과를 messages에 추가
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

    return "최대 반복 횟수를 초과했습니다."


# ============================================================
# 테스트 시나리오 실행
# ============================================================

# -------- 시나리오 1: 단일 날씨 조회 --------
print("\n" + "=" * 60)
print("[시나리오 1: 단일 날씨 조회]")
answer1 = run_travel_agent("도쿄 여행 준비 중인데 날씨가 어때?")
print(f"\n💡 최종 응답:\n{answer1}")

# -------- 시나리오 2: 단일 환율 조회 --------
print("\n" + "=" * 60)
print("[시나리오 2: 단일 환율 조회]")
answer2 = run_travel_agent("일본 여행 가는데 엔화 환율 알려줘")
print(f"\n💡 최종 응답:\n{answer2}")

# -------- 시나리오 3: 복합 정보 조회 (Multi-tool) --------
print("\n" + "=" * 60)
print("[시나리오 3: 복합 정보 조회 - Multi-tool 호출]")
answer3 = run_travel_agent("상하이 출장 가는데 날씨랑 환율 둘 다 알려줘")
print(f"\n💡 최종 응답:\n{answer3}")

