"""
Chapter 7-2: Tool 통합 - 회식 코스 플래너 에이전트

도구에서 생성되는 과도한 컨텍스트를 방지하기 위한 패턴:
- 여러 API를 기능별로 그룹화하여 통합 도구로 제공
- READ (get_place_info) / WRITE (manage_course) 분리

학습 목표:
1. Tool 통합 패턴: action 파라미터로 관련 API 그룹화
2. READ/WRITE 분리: SRP 원칙에 따른 도구 설계
3. 실제 API 호출: 카카오 로컬 API 활용

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

SYSTEM_PROMPT = """당신은 회식 코스를 짜주는 전문 플래너입니다.

사용 가능한 도구:

1. get_place_info: 장소 정보 조회 (카카오 API)
   - action="keyword_search": 키워드로 장소 검색 (query 필수)
   - action="category_search": 카테고리로 장소 검색 (category_code, x, y 필수)
   - action="coord_to_address": 좌표 → 도로명 주소 (x, y 필수)
   - action="coord_to_region": 좌표 → 행정구역 (x, y 필수)

   카테고리 코드:
   - FD6: 음식점
   - CE7: 카페
   - CT1: 문화시설 (노래방 등)

2. manage_course: 회식 코스 관리 (JSON 파일 저장)
   - action="add": 코스에 장소 추가 (place_id, place_name, step, address, category 필수)
   - action="remove": 장소 제거 (place_id 필수)
   - action="list": 현재 코스 목록 조회
   - action="clear": 코스 초기화

회식 코스를 짤 때:
1. 먼저 기준 위치(역, 건물 등)를 검색하여 좌표를 얻습니다.
2. 해당 좌표 주변에서 카테고리별로 장소를 검색합니다.
3. 적절한 장소를 선택하여 코스에 추가합니다.
4. 최종 코스를 정리하여 보여줍니다.

코스에 장소를 추가할 때는 반드시 place_id, place_name, step, address, category를 모두 포함해야 합니다.
"""


# ============================================================
# Tool Loop 구현
# ============================================================


def run_course_planner(user_message: str) -> str:
    """
    Tool Loop 패턴으로 회식 코스 플래너 에이전트를 실행합니다.

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
    max_iterations = 15  # 복합 시나리오를 위해 충분히 설정

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
                result = execute_tool(func_name, func_args.copy())

                # 결과가 길면 축약해서 출력
                result_preview = result[:300] + "..." if len(result) > 300 else result
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


if __name__ == "__main__":
    # 코스 초기화
    from tools import manage_course
    manage_course("clear")
    print("🔄 기존 코스 초기화 완료\n")

    # -------- 시나리오: 강남역 회식 코스 --------
    answer = run_course_planner(
        """강남역 근처에서 회식 코스 짜줘.
1차는 고기집, 2차는 술집이나 호프, 3차는 노래방으로 해줘.
각 장소의 정확한 도로명 주소와 어느 동에 위치하는지도 알려줘.
코스에 저장해줘."""
    )
    print(f"\n💡 최종 응답:\n{answer}")
