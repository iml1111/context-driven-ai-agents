import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- 분석할 샘플 코드 (의도적 이슈 포함) --------
CODE = """
import json

def add(a, b=[]):
    b.append(a); return sum(b)

def load_cfg(path):
    f = open(path, "r")
    return json.load(f)
"""

print("=" * 60)
print("📝 분석 대상 코드:")
print("=" * 60)
print(CODE)
print("=" * 60)

# -------- 1단계: Logic (코드 분석 → JSON) --------
print("\n🔍 1단계: 코드 분석 중...")

logic_system = """
You are a Python code analyst. Return STRICT JSON only with keys:
summary, issues[], refactors[], checks, confidence.

Each issue: {type, severity, lines[], reason, fix_suggestion, snippet}.
Priorities: critical>security>performance>style. Include line numbers/snippets.
"""

logic_user = f"""
Analyze this Python code and report issues as JSON.

```python
{CODE}
```
"""

logic_resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": logic_system},
        {"role": "user", "content": logic_user},
    ],
)

logic_text = logic_resp.choices[0].message.content
logic_json = json.loads(logic_text)

print("✅ 분석 완료 (JSON 생성)")
print(json.dumps(logic_json, ensure_ascii=False, indent=2))

# -------- 2단계: Formatting (JSON → Markdown) --------
print("\n📄 2단계: 보고서 생성 중...")

fmt_system = """
You are a precise technical writer. Write a Korean Markdown report with sections:
(1) 개요(요약, 신뢰도)
(2) 핵심 이슈 표(유형|심각도|라인|이유|수정 제안)
(3) 문제/패치 스니펫(```python)
(4) 리팩터링 제안
(5) 체크리스트(PEP8/타이핑/보안)

표/코드블록/제목을 반드시 포함하고 줄 길이는 적당히 개행하세요.
"""

fmt_user = f"""
다음 JSON 분석 결과를 보고서로 작성:

{json.dumps(logic_json, ensure_ascii=False, indent=2)}
"""

fmt_resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": fmt_system},
        {"role": "user", "content": fmt_user},
    ],
)

markdown = fmt_resp.choices[0].message.content

# 보고서 저장
output_file = Path("report.md")
output_file.write_text(markdown, encoding="utf-8")

print("✅ 보고서 생성 완료")
print(f"   - 저장 위치: {output_file.absolute()}")
print("\n" + "=" * 60)
print("🎉 분석 완료! report.md를 확인하세요.")
print("=" * 60)
