"""
Chapter 7-2: Tool 통합 - BTC 투자 도우미 에이전트

도구에서 생성되는 과도한 컨텍스트를 방지하기 위한 패턴:
- 여러 API를 기능별로 그룹화하여 통합 도구로 제공
- READ (get_btc_info) / WRITE (execute_btc_order) 분리

학습 목표:
1. Tool 통합 패턴: action 파라미터로 관련 API 그룹화
2. READ/WRITE 분리: SRP 원칙에 따른 도구 설계
3. 실제 API 호출: 빗썸 공개 API 활용

실행: python chapter_7-2/main.py
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

SYSTEM_PROMPT = """당신은 BTC 투자를 도와주는 전문 투자 어시스턴트입니다.

사용 가능한 도구:
1. get_btc_info: BTC 투자 정보 조회 (통합 도구)
   - action="price": 현재 가격 조회
   - action="candles": 최근 20일 일봉 캔들 조회

2. execute_btc_order: BTC 매수/매도 주문 실행 (Mock)
   - action="buy": 매수
   - action="sell": 매도
   - amount_krw: 주문 금액 (KRW)

사용자의 투자 관련 질문에 적절한 도구를 사용하여 정보를 제공하세요.
가격 정보는 한국 원화(KRW) 기준입니다.
차트 분석 시에는 추세, 지지/저항선 등을 간단히 설명해주세요.
"""


# ============================================================
# Tool Loop 구현
# ============================================================


def run_btc_agent(user_message: str) -> str:
    """
    Tool Loop 패턴으로 BTC 투자 도우미 에이전트를 실행합니다.

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

                # 결과가 길면 축약해서 출력
                result_preview = result[:200] + "..." if len(result) > 200 else result
                print(f"   📊 결과: {result_preview}")

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

# -------- 시나리오 1: 매수/매도/보유 결정 --------
answer1 = run_btc_agent("현재 나는 비트코인 10억원어치를 가지고 있어. 비트코인 현재 가격 및 과거 캔들을 분석한 후, 현재가 어떤 지점인지 판단한 후, 매수/매도/보유를 결정하여 실행해줘.")
print(f"\n💡 최종 응답:\n{answer1}")


# -------- 시나리오 2: 매수/매도 결정 (보유 금지) --------
# answer2 = run_btc_agent("""
# 현재 나는 비트코인 10억원어치를 가지고 있어.
# 비트코인 현재 가격 및 과거 캔들을 분석한 후, 현재가 어떤 지점인지 판단한 후, 
# 매수/매도를 결정하여 직접 실행해줘. 다만, 홀드는 금지. 둘 중 하나는 반드시 실행해줘.
# """)
# print(f"\n💡 최종 응답:\n{answer2}")
