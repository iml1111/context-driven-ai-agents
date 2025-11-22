import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import agent_planner
import agent_writer

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PDF_PATH = Path(__file__).parent.parent / "assets" / "sample.pdf"

print("=" * 60)
print("Chapter 4: Planning 패턴 실습 - Plan → 실행")
print("=" * 60)

# -------- 파일 업로드 --------
print("\n📄 파일 업로드 중...")
uploaded_file = client.files.create(
    file=open(PDF_PATH, "rb"),
    purpose="assistants",
)
print("✅ 업로드 완료")
file_id = uploaded_file.id

# -------- STEP 1: 요약 계획 수립 (Planner) --------
print("\n📋 STEP 1: 요약 계획 수립 중...")
plan = agent_planner.run(client, file_id)
print("✅ 계획 완료")
print("\n📝 생성된 계획:")
print(plan)

# -------- STEP 2: 계획에 따라 요약 작성 (Writer) --------
print("\n" + "=" * 60)
print("📝 STEP 2: 계획에 따라 요약 작성 중...")
summary = agent_writer.run(client, file_id, plan)
print("✅ 요약 완료")

# -------- 최종 결과 출력 및 저장 --------
print("\n" + "=" * 60)
print("📄 최종 요약:")
print(summary)

output_file = Path(__file__).parent / "output_summary.txt"
output_file.write_text(summary, encoding="utf-8")

print("\n" + "=" * 60)
print("🎉 Planning 패턴 실습 완료!")
