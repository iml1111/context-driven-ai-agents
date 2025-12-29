import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- Campaign Brief (입력 데이터) --------
CAMPAIGN_BRIEF = """
[Campaign Brief]
- Google Ads: spend $5,000, clicks 10,000, CVR 2.1%, AOV $24
- Meta Ads:   spend $3,200, clicks  6,400, CVR 1.8%, AOV $27
- Coupon: 15% of all orders get $3 off
- Payment fee: 3% of revenue (apply AFTER coupon)
- ROAS = net_revenue / total_ad_spend
- Round ONLY the final ROAS to 2 decimals
"""

print("=" * 60)
print("💰 Exercise 2 - After (CoT + Self-Consistency)")
print("=" * 60)
print("Campaign Brief:")
print(CAMPAIGN_BRIEF.strip())
print("=" * 60)

# -------- Generator Prompt (5개 독립 솔루션 생성) --------
GENERATOR_PROMPT = f"""
Solve step by step in ONE short line per step:
1) Assumptions 2) Formula/basis 3) Calculations 4) Sanity check 5) Final: <number>
Create 5 independent solutions with slightly different reasoning.

Constraints:
- orders_google = clicks_google * CVR_google
- orders_meta   = clicks_meta   * CVR_meta
- gross_revenue = orders_google*AOV_g + orders_meta*AOV_m
- coupon_value  = (orders_google + orders_meta) * 0.15 * 3
- net_revenue   = (gross_revenue - coupon_value) * (1 - 0.03)   # fee AFTER coupon
- ROAS = net_revenue / total_ad_spend

Round ONLY final ROAS to 2 decimals.
Return 5 plain texts, each ending with 'Final: <number>'.

Problem:
{CAMPAIGN_BRIEF}
"""


def generate_candidate():
    """단일 후보 솔루션 생성"""
    resp = client.chat.completions.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": GENERATOR_PROMPT}],
    )
    return resp.choices[0].message.content.strip()


print("\n🔍 1단계: 5개 독립 솔루션 생성 중...")

candidates = []
for i in range(5):
    print(f"   후보 {i+1}/5 생성 중...")
    candidates.append(generate_candidate())

print("✅ 5개 후보 생성 완료")
print("\n" + "=" * 60)
print("📋 생성된 후보들:")
print("=" * 60)
for i, cand in enumerate(candidates, 1):
    print(f"\n[후보 {i}]")
    print(cand)
    print("-" * 60)

# -------- Aggregator Prompt (다수결 집계) --------
joined_candidates = "\n\n---\n\n".join(candidates)

AGGREGATOR_PROMPT = f"""
You are an aggregator. Given 5 candidates each ending with "Final: <number>" (ROAS),
1) Extract the numbers (exact to 2 decimals),
2) Choose the majority value,
3) If tie, prefer the value whose candidate explicitly applies the fee AFTER coupon.

Output JSON only: {{"final_roas": <number>, "candidates":[<numbers>]}}

Candidates:
{joined_candidates}
"""

print("\n🔍 2단계: 다수결 집계 중...")

resp = client.chat.completions.create(
    model="gpt-5.1",
    response_format={"type": "json_object"},
    messages=[{"role": "user", "content": AGGREGATOR_PROMPT}],
)

result = json.loads(resp.choices[0].message.content)

print("✅ 집계 완료")
print("\n" + "=" * 60)
print("🎯 최종 결과:")
print("=" * 60)
print(json.dumps(result, ensure_ascii=False, indent=2))
print("\n" + "=" * 60)
print(f"💡 최종 ROAS: {result.get('final_roas')}")
print(f"📊 후보 값들: {result.get('candidates')}")
print("=" * 60)
