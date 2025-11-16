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
print("💰 Exercise 2 - Before (단순 프롬프트)")
print("=" * 60)
print("Campaign Brief:")
print(CAMPAIGN_BRIEF.strip())
print("=" * 60)

# -------- Before: 단순 프롬프트 --------
print("\n🔍 LLM 호출 중...")

PROMPT_BEFORE = """
Compute the ROAS for this month's campaign and give the answer.
"""

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": PROMPT_BEFORE + "\n\n" + CAMPAIGN_BRIEF},
    ],
)

result = resp.choices[0].message.content

print("✅ 응답 완료")
print("\n" + "=" * 60)
print("📄 결과:")
print("=" * 60)
print(result)
