"""
Chapter 9-2: Calendar Agent (MCP Client + OpenAI Function Calling)

FastMCP 서버와 연동하여 일정을 관리하는 에이전트.
MCP 서버를 별도 터미널에서 먼저 실행해야 합니다.

학습 목표:
1. FastMCP 서버 직접 구현 및 실행
2. MCP Client + SSE 트랜스포트 연동
3. OpenAI Function Calling + Tool Loop 패턴

실행 방법:
1. 터미널 1: python server.py  (MCP 서버 먼저 실행)
2. 터미널 2: python main.py    (Agent 실행)
"""

import asyncio
import json

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI

load_dotenv()
openai_client = OpenAI()

MCP_SERVER_URL = "http://localhost:8000/sse"

SYSTEM_PROMPT = """당신은 친절한 일정 관리 비서입니다.

사용 가능한 MCP 도구:
1. get_current_datetime: 현재 날짜/시간 조회
2. list_events: 일정 목록 조회 (date 파라미터로 특정 날짜 필터링 가능)
3. get_event: 특정 일정 상세 조회 (event_id 필요)
4. add_event: 새 일정 추가 (title, date, time 필수)
5. update_event: 일정 수정 (event_id 필수)
6. delete_event: 일정 삭제 (event_id 필수)

일정 관련 요청에 적절한 도구를 사용하여 정확한 정보를 제공하세요.
한국어로 친절하게 답변합니다.
"""


async def run_agent(session: ClientSession, user_message: str, conversation: list, tools: list[dict]) -> str:
    """Tool Loop 패턴으로 에이전트 실행"""

    conversation.append({"role": "user", "content": user_message})

    iteration = 0
    max_iterations = 5

    while iteration < max_iterations:
        iteration += 1
        print(f"   🤖 LLM 호출 #{iteration}...")

        response = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation,
            tools=tools,
        )

        choice = response.choices[0]
        assistant_message = choice.message

        # Case 1: 최종 응답
        if choice.finish_reason == "stop":
            conversation.append({"role": "assistant", "content": assistant_message.content})
            return assistant_message.content

        # Case 2: Tool 호출
        if assistant_message.tool_calls:
            conversation.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"   🔧 [{func_name}] 호출 중...")

                # MCP Tool 호출 (인라인)
                result = await session.call_tool(func_name, func_args)
                result_text = result.content[0].text if result.content else json.dumps({"error": "No content"})

                print(f"   📊 결과: {result_text[:100]}..." if len(result_text) > 100 else f"   📊 결과: {result_text}")

                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    }
                )

    return "최대 반복 횟수를 초과했습니다."


async def main():
    """Calendar Agent 메인 함수 - CLI 대화형 루프"""

    print("📅 Calendar Agent (MCP 연동)")
    print(f"🔌 Connecting to {MCP_SERVER_URL}...")

    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("✅ MCP 서버 연결 완료")

            # MCP Tools → OpenAI Function Calling 스키마 변환 (인라인)
            mcp_tools = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
                    },
                }
                for tool in mcp_tools.tools
            ]
            print(f"📋 사용 가능한 도구: {[t['function']['name'] for t in tools]}")

            conversation = []

            while True:
                try:
                    user_input = input("🧑 You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n👋 일정 관리 종료!")
                    break

                if not user_input:
                    continue

                response = await run_agent(session, user_input, conversation, tools)
                print(f"\n🤖 Agent: {response}\n")


if __name__ == "__main__":
    asyncio.run(main())
