"""
Chapter 9-1: Study Buddy Agent

GitHub Public 레포를 함께 읽고 구조를 설명해주는 Study Buddy Agent.
OpenAI Responses API + Hosted MCP (GitMCP.io) 연동을 통해
LLM이 실시간으로 GitHub 코드를 읽고 분석합니다.

학습 목표:
1. Hosted MCP 개념 이해 (Remote MCP Server)
2. OpenAI Responses API + MCP 연동
3. 컨텍스트 유지 대화 패턴
"""

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# ========================================
# 📌 여기에 분석할 GitHub 레포 URL을 입력하세요
# ========================================
GITHUB_REPO_URL = "https://github.com/iml1111/void"

# Study Buddy 시스템 프롬프트
SYSTEM_PROMPT = """당신은 친근한 코드 학습 도우미 "Study Buddy"입니다.

역할:
- GitHub 레포의 코드를 함께 읽고 분석합니다
- 코드 구조, 파일 역할, 함수 동작을 쉽게 설명합니다
- 학습자의 질문에 친절하게 답변합니다

스타일:
- 한국어로 답변합니다
- 복잡한 개념은 단계별로 설명합니다
- 필요시 코드 예시를 포함합니다
- 이해를 돕는 비유를 사용합니다

MCP 도구를 활용하여:
- 레포 구조 탐색 (디렉토리, 파일 목록)
- 특정 파일 내용 읽기
- 코드 분석 및 설명
"""

# GitMCP URL 변환: https://github.com/owner/repo → https://gitmcp.io/owner/repo
GITMCP_URL = GITHUB_REPO_URL.replace("https://github.com/", "https://gitmcp.io/")


def chat(user_message: str, conversation: list) -> str:
    """Responses API + MCP로 대화합니다 (스트리밍)."""
    # 사용자 메시지 추가
    conversation.append({
        "role": "user",
        "content": user_message,
    })

    # Responses API 스트리밍 호출
    stream = client.responses.create(
        model="gpt-4.1",
        input=conversation,
        instructions=SYSTEM_PROMPT,
        tools=[
            {
                "type": "mcp",
                "server_label": "gitmcp",
                "server_url": GITMCP_URL,
                "require_approval": "never",
            }
        ],
        stream=True,
    )

    # 스트리밍 이벤트 처리
    full_text = ""
    first_output = True

    for event in stream:
        # MCP 도구 호출 시작 (output_item.added에서 mcp_call 타입 감지)
        if event.type == "response.output_item.added":
            if hasattr(event, "item") and getattr(event.item, "type", None) == "mcp_call":
                if first_output:
                    print("\r🤖 Agent: ", end="", flush=True)
                    first_output = False
                tool_name = getattr(event.item, "name", "unknown")
                print(f"\n🔧 [{tool_name}] 호출 중...", end="", flush=True)
        # MCP 도구 호출 완료
        elif event.type == "response.mcp_call.completed":
            print(" ✓", flush=True)
        # 텍스트 출력 스트리밍
        elif event.type == "response.output_text.delta":
            if first_output:
                print("\r🤖 Agent: ", end="", flush=True)
                first_output = False
            print(event.delta, end="", flush=True)
            full_text += event.delta

    # 대화 히스토리에 추가
    conversation.append({
        "role": "assistant",
        "content": full_text,
    })

    return full_text


def main():
    """Study Buddy Agent 메인 함수 - CLI 대화형 루프"""
    conversation = []

    # 시작 메시지
    print("📚 Study Buddy Agent")
    print(f"🔗 레포: {GITHUB_REPO_URL}")
    print(f"🌐 MCP:  {GITMCP_URL}")
    print()

    # 대화 루프
    while True:
        try:
            user_input = input("🧑 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 공부 끝! 다음에 또 만나요!")
            break

        # 빈 입력 무시
        if not user_input:
            continue

        # 에이전트 응답 (스트리밍)
        print("\n🤖 Agent: 생각 중...", end="", flush=True)

        try:
            chat(user_input, conversation)  # 스트리밍으로 직접 출력
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")

        print()


if __name__ == "__main__":
    main()
