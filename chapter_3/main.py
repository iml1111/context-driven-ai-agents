import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import step1_summarize
import step2_trends
import step3_email

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PDF_PATH = Path(__file__).parent / "sample.pdf"


# -------- 파일 업로드 --------
print("📄 파일 업로드 중...")
uploaded_file = client.files.create(
    file=open(PDF_PATH, "rb"),
    purpose="assistants",
)
print("✅ 업로드 완료")
file_id = uploaded_file.id

# -------- STEP 1: 요약 생성 --------
print("📝 STEP 1: 요약 생성 중...")
summary = step1_summarize.run(client, file_id)
print("✅ 요약 완료")
print(summary)

# -------- STEP 2: 트렌드 추출 --------
print("🔍 STEP 2: 트렌드 분석 중...")
trends_json = step2_trends.run(client, summary)
print("✅ 트렌드 추출 완료")
print(json.dumps(json.loads(trends_json), indent=2, ensure_ascii=False))

# -------- STEP 3: 이메일 작성 --------
print("✉️ STEP 3: 이메일 작성 중...")
email = step3_email.run(client, trends_json)
print("✅ 이메일 생성 완료")

# -------- 최종 결과 출력 및 저장 --------
print("📧 최종 이메일")
print(email)

output_file = Path(__file__).parent / "output_email.txt"
output_file.write_text(email, encoding="utf-8")

print("🎉 모든 단계 완료!")
