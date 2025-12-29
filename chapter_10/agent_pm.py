"""
Chapter 10: PM Agent - Requirements Extraction

사용자 입력에서 구조화된 요구사항을 추출하는 에이전트.
web_search를 사용하여 베스트 프랙티스 리서치.
"""

from openai import OpenAI

SYSTEM_PROMPT = """You are a Product Manager specializing in requirements analysis.

Your task is to extract clear, structured requirements from vague user requests.

## Output Format (Markdown)

# Requirements Document

## Project Overview
Brief description of the project.

## Functional Requirements
1. [Feature 1]: Description
2. [Feature 2]: Description
...

## UI/UX Requirements
1. [UI Element]: Description
2. [Interaction]: Description
...

## Technical Constraints
- Constraint 1
- Constraint 2
...

## Out of Scope
- What will NOT be implemented

---

## Guidelines
- Be specific and actionable
- Include all user-mentioned features
- Add reasonable implicit requirements (e.g., error handling, empty states, edge cases)
- Search for best practices relevant to the project type

## Length Constraint
- Keep the entire document under 2000 characters
- Be concise but complete
"""


def run_extract_requirements(
    client: OpenAI,
    user_input: str,
    feedback: str | None = None
) -> str:
    """
    사용자 입력에서 요구사항 추출.

    Args:
        client: OpenAI 클라이언트
        user_input: 사용자의 프로젝트 요청
        feedback: 이전 결과에 대한 개선 피드백 (재호출 시)

    Returns:
        구조화된 요구사항 문서 (Markdown)
    """
    print("   📋 PM Agent: 요구사항 추출 중...")
    print("   🔍 Web Search: best practices for this project type...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # 피드백이 있으면 개선 요청
    if feedback:
        messages.append({
            "role": "user",
            "content": f"""Previous requirements need improvement.

User Request:
{user_input}

Feedback to address:
{feedback}

Please search for best practices and generate improved requirements addressing the feedback."""
        })
        print(f"   ⚠️  피드백 반영: {feedback[:50]}...")
    else:
        messages.append({
            "role": "user",
            "content": f"Search for best practices relevant to this project and extract requirements from this request:\n\n{user_input}"
        })

    # web_search 도구 사용 (Responses API)
    response = client.responses.create(
        model="gpt-5.1",
        input=messages,
        tools=[{"type": "web_search"}]
    )

    result = response.output_text
    print("   ✅ 요구사항 추출 완료")

    return result
