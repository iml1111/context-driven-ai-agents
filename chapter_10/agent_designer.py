"""
Chapter 10: Designer Agent - UI/UX Design Specification

요구사항을 기반으로 모던한 UI/UX 디자인 기획서를 작성.
web_search를 사용하여 최신 트렌드 참고.
"""

from openai import OpenAI

SYSTEM_PROMPT = """You are a Web Designer specializing in modern, accessible UI/UX design.

Your task is to create a detailed design specification based on requirements.

## Output Format (Markdown)

# Design Specification

## Design Philosophy
Brief description of the design approach.

## Color Palette
- Primary: #HEX (purpose)
- Secondary: #HEX (purpose)
- Background: #HEX
- Text: #HEX
- Accent/Success: #HEX
- Error/Danger: #HEX

## Typography
- Font Family: (e.g., system-ui, sans-serif)
- Headings: size, weight
- Body: size, weight
- Small/Caption: size

## Layout Structure
Describe the overall page layout using ASCII art or description.
Consider: Header, Main Content Area, Sidebar (if any), Footer.

## Component Specifications
For each UI component identified in requirements:

### [Component Name]
- Size, spacing, layout
- Colors and visual styling
- States (normal, hover, active, disabled, error)
- Responsive behavior

## Responsive Design
- Mobile breakpoint considerations
- Touch-friendly tap targets (min 44px)

## Accessibility
- Color contrast ratios
- Focus indicators
- Keyboard navigation
- ARIA labels

## Animations/Transitions
- Hover effects
- Completion animation
- Delete animation

---

## Guidelines
- Use modern, clean design principles
- Ensure accessibility (WCAG 2.1 AA)
- Provide specific CSS values (px, rem, hex colors)
- Keep it implementable with vanilla CSS

## Length Constraint
- Keep the entire document under 2000 characters
- Focus on essential specifications only
"""


def run(
    client: OpenAI,
    requirements: str,
    feedback: str | None = None
) -> str:
    """
    요구사항 기반 디자인 기획서 생성.

    Args:
        client: OpenAI 클라이언트
        requirements: 요구사항 문서
        feedback: 이전 결과에 대한 개선 피드백 (재호출 시)

    Returns:
        디자인 기획서 (Markdown)
    """
    print("   🎨 Designer Agent: 디자인 기획서 작성 중...")
    print("   🔍 Web Search: modern web app UI design trends...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # 피드백이 있으면 개선 요청
    if feedback:
        messages.append({
            "role": "user",
            "content": f"""Previous design spec needs improvement.

Requirements:
{requirements}

Feedback to address:
{feedback}

Please search for modern UI trends and create an improved design specification."""
        })
        print(f"   ⚠️  피드백 반영: {feedback[:50]}...")
    else:
        messages.append({
            "role": "user",
            "content": f"""Create a design specification for this project.

Requirements:
{requirements}

Please search for modern web UI design trends relevant to this project and create a detailed design specification."""
        })

    # web_search 도구 사용 (Responses API)
    response = client.responses.create(
        model="gpt-5.1",
        input=messages,
        tools=[{"type": "web_search"}]
    )

    result = response.output_text
    print("   ✅ 디자인 기획서 작성 완료")

    return result
