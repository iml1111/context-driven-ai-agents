"""
Chapter 10: AI Development Team - Tool Definitions

Supervisor 패턴에서 사용하는 5개 Tool 정의.
각 Tool은 서브 에이전트를 호출하는 인터페이스 역할.
"""

import json
from typing import Any

from openai import OpenAI

# Tool 정의: Supervisor가 호출할 수 있는 서브 에이전트들
TOOLS = [
    # 1. 요구사항 추출
    {
        "type": "function",
        "function": {
            "name": "extract_requirements",
            "description": "사용자 입력에서 요구사항 추출. 결과가 불명확하면 feedback과 함께 재호출 가능.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "사용자의 프로젝트 요청"
                    },
                    "feedback": {
                        "type": "string",
                        "description": "이전 결과에 대한 개선 피드백 (재호출 시)"
                    }
                },
                "required": ["user_input"]
            }
        }
    },
    # 2. 디자인 기획
    {
        "type": "function",
        "function": {
            "name": "create_design_spec",
            "description": "UI/UX 디자인 기획서 작성. web_search로 트렌드 탐색. 문제 시 feedback과 함께 재호출.",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "요구사항 문서"
                    },
                    "feedback": {
                        "type": "string",
                        "description": "이전 결과에 대한 개선 피드백 (재호출 시)"
                    }
                },
                "required": ["requirements"]
            }
        }
    },
    # 3. 코드 생성
    {
        "type": "function",
        "function": {
            "name": "generate_code",
            "description": "HTML/CSS/JS 코드 생성. web_search로 베스트 프랙티스 탐색. 문제 시 feedback과 함께 재호출.",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "요구사항 문서"
                    },
                    "design_spec": {
                        "type": "string",
                        "description": "디자인 기획서"
                    },
                    "feedback": {
                        "type": "string",
                        "description": "버그 수정 또는 개선 피드백 (재호출 시)"
                    }
                },
                "required": ["requirements", "design_spec"]
            }
        }
    },
    # 4. E2E 테스트
    {
        "type": "function",
        "function": {
            "name": "test_application",
            "description": "Playwright MCP로 E2E 테스트 수행. PASS/FAIL 결과 및 버그 목록 반환.",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "검증 기준이 되는 요구사항"
                    }
                },
                "required": ["requirements"]
            }
        }
    },
    # 5. 버그 수정 요청
    {
        "type": "function",
        "function": {
            "name": "request_fix",
            "description": "테스트 실패 시 Architect에게 버그 수정 요청. 버그 목록을 전달하고 수정된 코드 반환.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_code": {
                        "type": "string",
                        "description": "현재 HTML 코드"
                    },
                    "bug_report": {
                        "type": "string",
                        "description": "테스트에서 발견된 버그 목록"
                    },
                    "requirements": {
                        "type": "string",
                        "description": "요구사항 문서"
                    },
                    "design_spec": {
                        "type": "string",
                        "description": "디자인 기획서"
                    }
                },
                "required": ["current_code", "bug_report", "requirements", "design_spec"]
            }
        }
    }
]


def execute_tool(client: OpenAI, name: str, arguments: dict[str, Any]) -> str:
    """
    Tool 이름에 따라 적절한 에이전트 함수를 호출.

    Args:
        client: OpenAI 클라이언트
        name: Tool 이름
        arguments: Tool 호출 인자

    Returns:
        에이전트 실행 결과 (문자열)
    """
    if name == "extract_requirements":
        import agent_pm
        return agent_pm.run_extract_requirements(
            client,
            arguments["user_input"],
            arguments.get("feedback")
        )

    elif name == "create_design_spec":
        import agent_designer
        return agent_designer.run(
            client,
            arguments["requirements"],
            arguments.get("feedback")
        )

    elif name == "generate_code":
        import agent_architect
        return agent_architect.run(
            client,
            arguments["requirements"],
            arguments["design_spec"],
            arguments.get("feedback")
        )

    elif name == "test_application":
        import agent_tester
        return agent_tester.run(client, arguments["requirements"])

    elif name == "request_fix":
        import agent_architect
        return agent_architect.run_fix(
            client,
            arguments["current_code"],
            arguments["bug_report"],
            arguments["requirements"],
            arguments["design_spec"]
        )

    else:
        return json.dumps({"error": f"Unknown tool: {name}"})
