"""
Chapter 10: Multi-Agent Collaboration POC - AI Development Team

Supervisor 패턴 기반의 멀티 에이전트 협업 시스템.
웹 애플리케이션을 자동 설계/개발/테스트하는 "AI 개발팀" 구현.

핵심 특징:
- Supervisor (PM Agent)가 전체 워크플로우 조율
- 문제 발생 시 자율적으로 루프하여 해결
- OpenAI Function Calling으로 서브 에이전트 호출
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경변수 로드
load_dotenv()

# 현재 디렉토리를 path에 추가 (agent 모듈 import를 위해)
sys.path.insert(0, str(Path(__file__).parent))

from tools import TOOLS, execute_tool

# 출력 디렉토리
OUTPUT_DIR = Path(__file__).parent / "output"

# Supervisor System Prompt
SUPERVISOR_PROMPT = """You are a Project Manager coordinating an AI Development Team.

## Your Team (3 agents)
1. Designer - Creates UI/UX design specs (uses web_search)
2. Architect - Generates production code (uses web_search)
3. Tester - Validates quality via E2E testing (Playwright)

## Your Responsibilities
- Extract and organize requirements from user input
- Coordinate team via tool calls
- Review each agent's output and decide on retries
- Write final README documentation

## CRITICAL RULES (NEVER SKIP - HIGHEST PRIORITY)
⚠️ These rules override all other instructions:
1. **NEVER complete workflow if ANY test fails** - You MUST keep trying until Pass Rate = 100%
2. **Test failure = MUST retry**: Call request_fix → then test_application again
3. **Maximum 3 retry cycles** for test failures - only then can you proceed with best effort
4. **ONLY provide final summary when ALL tests pass** (Pass Rate = 100%)

## Workflow Rules
1. Execute steps in order: extract_requirements → create_design_spec → generate_code → test_application
2. **REVIEW each result before proceeding**:
   - Is the output complete and aligned with requirements?
   - Are there any obvious issues or missing elements?
3. **If issues found**: Re-call the agent with `feedback` parameter describing the problem
4. **Max retries per step**: 3 times. After 3 failures, proceed with best effort.

## Test Failure Handling (MANDATORY)
When test_application returns ANY failures:
1. IMMEDIATELY call request_fix with the bug report
2. THEN call test_application again to verify fixes
3. REPEAT until all tests pass OR you've retried 3 times
4. The system will tell you how many retries remain

## Decision Examples
- Design spec missing key elements? → Re-call create_design_spec with feedback
- Code doesn't implement all features? → Re-call generate_code with feedback
- Any test fails? → Call request_fix with bug details, then test_application again
- Some tests pass but others fail? → MUST call request_fix, then test_application again
- All tests pass? → Provide final summary and stop

## Important
- Always explain your reasoning before each tool call
- After calling a tool, analyze its result and decide next action
- When all work is complete (ALL tests pass), output a final project summary
"""


def run_supervisor(client: OpenAI, user_input: str) -> dict:
    """
    Supervisor가 Tool Loop 패턴으로 에이전트들을 조율.

    Args:
        client: OpenAI 클라이언트
        user_input: 사용자의 프로젝트 요청

    Returns:
        모든 산출물을 담은 state dict
    """
    print("Chapter 10: Multi-Agent Collaboration POC - AI Development Team")
    print(f"\n💬 사용자 요청:\n{user_input}\n")

    # State 초기화
    state = {
        "requirements": None,
        "design_spec": None,
        "html_code": None,
        "test_report": None,
        "readme": None
    }

    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 대화 히스토리 초기화
    messages = [
        {"role": "system", "content": SUPERVISOR_PROMPT},
        {"role": "user", "content": f"다음 프로젝트를 진행해주세요:\n\n{user_input}"}
    ]

    iteration = 0
    max_iterations = 30  # 무한 루프 방지

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🤖 Supervisor Iteration #{iteration}")

        # Supervisor 호출
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            tools=TOOLS
        )

        choice = response.choices[0]
        assistant_message = choice.message

        # Case 1: 더 이상 Tool 호출 없음 - 워크플로우 완료
        if choice.finish_reason == "stop" and not assistant_message.tool_calls:
            print("\n✅ Supervisor: 워크플로우 완료!")
            if assistant_message.content:
                print(f"\n📝 최종 요약:\n{assistant_message.content[:500]}...")

            # README 작성
            state["readme"] = generate_readme(client, state)
            break

        # Case 2: Tool 호출 필요
        if assistant_message.tool_calls:
            # Supervisor의 reasoning 출력
            if assistant_message.content:
                print(f"   💭 Reasoning: {assistant_message.content[:200]}...")

            print(f"   🔧 Tool 호출: {len(assistant_message.tool_calls)}개")

            # 대화에 assistant 메시지 추가
            messages.append(assistant_message)

            # 각 Tool 실행
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"\n   → {func_name} 호출")

                # 에이전트 실행
                result = execute_tool(client, func_name, func_args)

                # State 업데이트 및 파일 저장
                update_state_and_save(state, func_name, result)

                # 결과를 대화에 추가 (각 에이전트가 2000자 이내로 작성하므로 자르지 않음)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

    if iteration >= max_iterations:
        print(f"\n⚠️  최대 반복 횟수({max_iterations}) 도달")

    return state


def update_state_and_save(state: dict, tool_name: str, result: str):
    """State 업데이트 및 파일 저장"""

    if tool_name == "extract_requirements":
        state["requirements"] = result
        path = OUTPUT_DIR / "requirements.md"
        path.write_text(result, encoding="utf-8")
        print(f"   ✅ 저장: {path.name}")

    elif tool_name == "create_design_spec":
        state["design_spec"] = result
        path = OUTPUT_DIR / "design_spec.md"
        path.write_text(result, encoding="utf-8")
        print(f"   ✅ 저장: {path.name}")

    elif tool_name == "generate_code":
        state["html_code"] = result
        path = OUTPUT_DIR / "app.html"
        path.write_text(result, encoding="utf-8")
        print(f"   ✅ 저장: {path.name}")

    elif tool_name == "test_application":
        state["test_report"] = result
        path = OUTPUT_DIR / "test_report.md"
        path.write_text(result, encoding="utf-8")
        print(f"   ✅ 저장: {path.name}")

    elif tool_name == "request_fix":
        # 수정된 코드로 업데이트
        state["html_code"] = result
        path = OUTPUT_DIR / "app.html"
        path.write_text(result, encoding="utf-8")
        print(f"   ✅ 업데이트: {path.name}")


def generate_readme(client: OpenAI, state: dict) -> str:
    """PM이 직접 README 작성"""
    print("\n📝 PM Agent: README 작성 중...")

    readme_prompt = """You are a Technical Writer. Generate a comprehensive README.md for this web application project.

Include:
1. Project Title and Description (based on requirements)
2. Features (based on requirements)
3. Tech Stack (based on requirements and generated code)
4. How to Run (open the HTML file in browser)
5. Project Structure
6. Test Results Summary
7. Screenshots (reference screenshot.png)

Keep it professional and concise.
"""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": readme_prompt},
            {"role": "user", "content": f"""Generate README based on:

## Requirements
{state.get('requirements', 'N/A')[:1500]}

## Design
{state.get('design_spec', 'N/A')[:1000]}

## Test Results
{state.get('test_report', 'N/A')[:1000]}
"""}
        ]
    )

    readme = response.choices[0].message.content
    path = OUTPUT_DIR / "README.md"
    path.write_text(readme, encoding="utf-8")
    print(f"   ✅ 저장: {path.name}")

    return readme


def main():
    """메인 실행 함수"""
    # OpenAI 클라이언트 생성
    client = OpenAI()

    # 데모 시나리오
    user_input = """로컬 스토리지에 저장되는 TODO List 웹앱을 만들어줘.

필요한 기능:
- 할 일 추가 (입력창 + 버튼)
- 완료 체크 (체크박스로 토글)
- 할 일 삭제 (삭제 버튼)
- 브라우저 새로고침해도 데이터 유지

디자인:
- 모던하고 깔끔한 UI
- 반응형 디자인
- 다크 테마 느낌

기술 제약:
- 순수 HTML/CSS/JavaScript만 사용
- 외부 라이브러리 사용 금지
- 단일 HTML 파일로 구현"""

    # Supervisor 실행
    state = run_supervisor(client, user_input)

    # 결과 출력
    print("\n" + "=" * 70)
    print("🎉 AI Development Team - 프로젝트 완료!")
    print("=" * 70)
    print("\n📂 생성된 산출물:")
    for file in OUTPUT_DIR.glob("*"):
        if file.is_file():
            print(f"   ✓ {file.name}")

    print(f"\n💡 웹앱 실행: open {OUTPUT_DIR / 'app.html'}")


if __name__ == "__main__":
    main()
