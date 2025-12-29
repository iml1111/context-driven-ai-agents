"""
Chapter 10: Architect Agent - Code Generation

요구사항과 디자인 기획서를 기반으로 완전한 웹앱 코드 생성.
"""

from openai import OpenAI

SYSTEM_PROMPT = """You are a Frontend Developer specializing in vanilla JavaScript applications.

Your task is to generate a complete, production-ready web application as a single HTML file based on the provided requirements and design specification.

## Technical Constraints
- Single HTML file with inline CSS and JavaScript
- NO external dependencies (no CDN, no npm packages)
- Pure vanilla JavaScript (no jQuery, React, Vue, etc.)
- Use localStorage for data persistence if needed
- Semantic HTML5
- Accessible (ARIA labels, keyboard navigation)

## Output Format
Return ONLY the complete HTML code, starting with <!DOCTYPE html> and ending with </html>.
Do NOT include markdown code blocks or explanations.

## Implementation Guidelines
- Implement ALL features specified in requirements
- Follow the design specification for styling
- Handle empty states and edge cases gracefully
- Include proper error handling and input validation

## Code Quality
- Clean, readable code with comments
- Consistent naming conventions
- Event delegation for dynamic elements
- Proper error handling
- Input validation (no empty tasks)

## Structure
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TODO App</title>
    <style>
        /* CSS here */
    </style>
</head>
<body>
    <!-- HTML structure here -->
    <script>
        // JavaScript here
    </script>
</body>
</html>
```
"""

FIX_SYSTEM_PROMPT = """You are a Frontend Developer fixing bugs in a web application.

Your task is to fix the reported bugs while maintaining existing functionality.

## Instructions
1. Read the bug report carefully
2. Identify the root cause
3. Fix the code without breaking other features
4. Return the COMPLETE fixed HTML file

## Output Format
Return ONLY the complete fixed HTML code, starting with <!DOCTYPE html> and ending with </html>.
Do NOT include markdown code blocks or explanations.

Be precise and fix only what's broken. Do not refactor or change working code.
"""


def run(
    client: OpenAI,
    requirements: str,
    design_spec: str,
    feedback: str | None = None
) -> str:
    """
    요구사항과 디자인 기반 코드 생성.

    Args:
        client: OpenAI 클라이언트
        requirements: 요구사항 문서
        design_spec: 디자인 기획서
        feedback: 이전 결과에 대한 개선 피드백 (재호출 시)

    Returns:
        완전한 HTML 코드
    """
    print("   👨‍💻 Architect Agent: 코드 생성 중...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # 피드백이 있으면 개선 요청
    if feedback:
        messages.append({
            "role": "user",
            "content": f"""Previous code needs improvement.

Requirements:
{requirements}

Design Specification:
{design_spec}

Feedback to address:
{feedback}

Please generate improved code addressing the feedback."""
        })
        print(f"   ⚠️  피드백 반영: {feedback[:50]}...")
    else:
        messages.append({
            "role": "user",
            "content": f"""Generate a complete TODO app based on these specifications.

Requirements:
{requirements}

Design Specification:
{design_spec}

Please generate production-ready code."""
        })

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=messages
    )

    result = response.choices[0].message.content

    # 마크다운 코드 블록 제거 (```html ... ``` 형태)
    if result.startswith("```"):
        lines = result.split("\n")
        # 첫 줄과 마지막 줄의 ``` 제거
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        result = "\n".join(lines)

    print("   ✅ 코드 생성 완료")

    return result


def run_fix(
    client: OpenAI,
    current_code: str,
    bug_report: str,
    requirements: str,
    design_spec: str
) -> str:
    """
    버그 리포트 기반 코드 수정.

    Args:
        client: OpenAI 클라이언트
        current_code: 현재 HTML 코드
        bug_report: 테스트에서 발견된 버그 목록
        requirements: 요구사항 문서
        design_spec: 디자인 기획서

    Returns:
        수정된 HTML 코드
    """
    print("   🔧 Architect Agent: 버그 수정 중...")

    messages = [
        {"role": "system", "content": FIX_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""Fix the bugs in this TODO app.

## Current Code
{current_code}

## Bug Report
{bug_report}

## Original Requirements
{requirements}

## Design Specification
{design_spec}

Please fix all reported bugs and return the complete fixed HTML code."""
        }
    ]

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=messages
    )

    result = response.choices[0].message.content

    # 마크다운 코드 블록 제거
    if result.startswith("```"):
        lines = result.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        result = "\n".join(lines)

    print("   ✅ 버그 수정 완료")

    return result
