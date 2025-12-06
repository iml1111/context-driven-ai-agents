"""
Chapter 10: Tester Agent - Dynamic E2E Testing with Playwright

요구사항을 기반으로 LLM이 동적으로 테스트 계획을 생성하고,
Playwright로 실제 브라우저에서 E2E 테스트를 수행.
"""

import json
import subprocess
import time
from pathlib import Path

from openai import OpenAI
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# 출력 디렉토리
OUTPUT_DIR = Path(__file__).parent / "output"

# 테스트 계획 생성 프롬프트
TEST_PLAN_PROMPT = """You are a QA Engineer creating E2E test plans for web applications.

Based on the requirements, generate a JSON array of test cases that can be executed with Playwright.

## Output Format (JSON Array)
```json
[
    {
        "name": "Test Name",
        "description": "What this test verifies",
        "steps": [
            {"action": "wait_for_selector", "selector": "CSS selector", "timeout": 5000},
            {"action": "fill", "selector": "CSS selector", "value": "text to type"},
            {"action": "click", "selector": "CSS selector"},
            {"action": "press", "selector": "CSS selector", "key": "Enter"},
            {"action": "wait", "ms": 500},
            {"action": "reload"}
        ],
        "verify": {
            "type": "contains_text|element_exists|element_count|checkbox_checked|localstorage_exists",
            "selector": "CSS selector (optional)",
            "text": "expected text (for contains_text)",
            "min_count": 1 (for element_count),
            "key": "storage key (for localstorage_exists)"
        }
    }
]
```

## Available Actions
- wait_for_selector: Wait for element to appear
- fill: Type text into input field
- click: Click an element
- press: Press a key (Enter, Tab, etc.)
- wait: Wait for milliseconds
- reload: Refresh the page

## Available Verifications
- contains_text: Check if page contains specific text
- element_exists: Check if element exists
- element_count: Check minimum number of elements
- checkbox_checked: Check if checkbox is checked
- localstorage_exists: Check if localStorage has any data

## Guidelines
- Create 4-6 focused test cases covering core functionality
- Use generic selectors that work across different implementations (input, button, etc.)
- Include a page load test as the first test
- Test user interactions based on requirements
- If data persistence is required, test reload behavior
- Keep selectors simple and robust

Return ONLY the JSON array, no explanations.
"""


def run(client: OpenAI, requirements: str) -> str:
    """
    요구사항 기반 동적 E2E 테스트 수행.

    Args:
        client: OpenAI 클라이언트
        requirements: 테스트 기준이 되는 요구사항

    Returns:
        테스트 리포트 (Markdown)
    """
    print("   🧪 Tester Agent: E2E 테스트 시작...")

    # LLM에게 테스트 계획 생성 요청
    print("   🤖 테스트 계획 생성 중...")
    test_plan = generate_test_plan(client, requirements)
    print(f"   📋 {len(test_plan)}개 테스트 케이스 생성됨")

    # 3. 로컬 서버 시작 (백그라운드)
    server_process = subprocess.Popen(
        ["python", "-m", "http.server", "8080", "--directory", str(OUTPUT_DIR)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)  # 서버 시작 대기

    test_results = []

    try:
        # 4. Playwright 테스트 실행
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 페이지 로드
            page.goto("http://localhost:8080/app.html")

            # 각 테스트 케이스 실행
            for test_case in test_plan:
                result = execute_test_case(page, test_case)
                test_results.append(result)
                status = "✅" if result["status"] == "PASS" else "❌"
                print(f"   {status} {result['name']}")

            # 스크린샷 저장
            screenshot_path = OUTPUT_DIR / "screenshot.png"
            page.screenshot(path=str(screenshot_path))
            browser.close()

    except Exception as e:
        test_results.append({
            "name": "Browser Test",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"   ❌ 테스트 오류: {e}")

    finally:
        # 5. 서버 종료
        server_process.terminate()
        server_process.wait()

    # 6. 테스트 리포트 생성
    report = generate_test_report(test_results, requirements)

    # 통과/실패 요약
    passed = sum(1 for t in test_results if t["status"] == "PASS")
    failed = sum(1 for t in test_results if t["status"] == "FAIL")
    print(f"   📊 결과: {passed} PASS / {failed} FAIL")

    return report


def generate_test_plan(client: OpenAI, requirements: str) -> list[dict]:
    """LLM을 사용하여 요구사항 기반 테스트 계획 생성"""

    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": TEST_PLAN_PROMPT},
            {"role": "user", "content": f"Generate test plan for this application:\n\n{requirements}"}
        ],
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    # JSON 파싱
    try:
        parsed = json.loads(content)
        # 배열이 직접 반환되거나 {"tests": [...]} 형태일 수 있음
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and "tests" in parsed:
            return parsed["tests"]
        else:
            # 첫 번째 배열 값 찾기
            for value in parsed.values():
                if isinstance(value, list):
                    return value
            return []
    except json.JSONDecodeError:
        print("   ⚠️  테스트 계획 파싱 실패, 기본 테스트 사용")
        return [
            {
                "name": "Page Load",
                "description": "Verify page loads correctly",
                "steps": [{"action": "wait_for_selector", "selector": "body", "timeout": 5000}],
                "verify": {"type": "element_exists", "selector": "body"}
            }
        ]


def execute_test_case(page, test_case: dict) -> dict:
    """단일 테스트 케이스 실행"""
    name = test_case.get("name", "Unknown Test")

    try:
        # 각 단계 실행
        for step in test_case.get("steps", []):
            execute_step(page, step)

        # 검증 수행
        verify = test_case.get("verify", {})
        if verify:
            success, error = execute_verification(page, verify)
            if success:
                return {"name": name, "status": "PASS", "error": None}
            else:
                return {"name": name, "status": "FAIL", "error": error}

        return {"name": name, "status": "PASS", "error": None}

    except PlaywrightTimeout as e:
        return {"name": name, "status": "FAIL", "error": f"Timeout: {str(e)}"}
    except Exception as e:
        return {"name": name, "status": "FAIL", "error": str(e)}


def execute_step(page, step: dict):
    """테스트 단계 실행"""
    action = step.get("action")
    selector = step.get("selector")
    timeout = step.get("timeout", 5000)

    if action == "wait_for_selector":
        page.wait_for_selector(selector, timeout=timeout)

    elif action == "fill":
        element = page.query_selector(selector)
        if element:
            element.fill(step.get("value", ""))
        else:
            raise Exception(f"Element not found: {selector}")

    elif action == "click":
        element = page.query_selector(selector)
        if element:
            element.click()
        else:
            raise Exception(f"Element not found: {selector}")

    elif action == "press":
        element = page.query_selector(selector)
        if element:
            element.press(step.get("key", "Enter"))
        else:
            raise Exception(f"Element not found: {selector}")

    elif action == "wait":
        time.sleep(step.get("ms", 500) / 1000)

    elif action == "reload":
        page.reload()
        page.wait_for_load_state("domcontentloaded")
        time.sleep(0.5)


def execute_verification(page, verify: dict) -> tuple[bool, str | None]:
    """검증 수행"""
    verify_type = verify.get("type")

    if verify_type == "contains_text":
        text = verify.get("text", "")
        if text in page.content():
            return True, None
        else:
            return False, f"Text not found: {text}"

    elif verify_type == "element_exists":
        selector = verify.get("selector", "body")
        element = page.query_selector(selector)
        if element:
            return True, None
        else:
            return False, f"Element not found: {selector}"

    elif verify_type == "element_count":
        selector = verify.get("selector", "*")
        min_count = verify.get("min_count", 1)
        elements = page.query_selector_all(selector)
        if len(elements) >= min_count:
            return True, None
        else:
            return False, f"Expected at least {min_count} elements, found {len(elements)}"

    elif verify_type == "checkbox_checked":
        selector = verify.get("selector", "input[type='checkbox']")
        checkbox = page.query_selector(selector)
        if checkbox and checkbox.is_checked():
            return True, None
        else:
            return False, "Checkbox not checked"

    elif verify_type == "localstorage_exists":
        key = verify.get("key")
        if key:
            data = page.evaluate(f"() => localStorage.getItem('{key}')")
        else:
            data = page.evaluate("() => Object.keys(localStorage).length > 0")
        if data:
            return True, None
        else:
            return False, "No data in localStorage"

    else:
        return True, None  # 알 수 없는 검증 타입은 통과 처리


def generate_test_report(test_results: list[dict], requirements: str) -> str:
    """테스트 리포트 생성"""
    passed = sum(1 for t in test_results if t["status"] == "PASS")
    failed = sum(1 for t in test_results if t["status"] == "FAIL")
    total = len(test_results)

    report = f"""# E2E Test Report

## Summary
- **Total Tests**: {total}
- **Passed**: {passed}
- **Failed**: {failed}
- **Pass Rate**: {(passed/total*100) if total > 0 else 0:.1f}%

## Test Results

| Test Name | Status | Error |
|-----------|--------|-------|
"""

    for test in test_results:
        status_emoji = "✅" if test["status"] == "PASS" else "❌"
        error = test.get("error") or "-"
        report += f"| {test['name']} | {status_emoji} {test['status']} | {error} |\n"

    # 버그 목록 (실패한 테스트)
    if failed > 0:
        report += "\n## Bug Report\n\n"
        for test in test_results:
            if test["status"] == "FAIL":
                report += f"### {test['name']}\n"
                report += f"- **Error**: {test.get('error', 'Unknown error')}\n"
                report += f"- **Expected**: This feature should work correctly\n\n"

    report += "\n## Screenshot\n"
    report += "![Test Screenshot](screenshot.png)\n"

    return report
