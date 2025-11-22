import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import agent_clarifier
import agent_rewriter
import agent_researcher

load_dotenv()

# Deep Research는 시간이 오래 걸리므로 timeout을 길게 설정 (30분)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=1800)

print("=" * 60)
print("Chapter 4-2: OpenAI Deep Research 실습")
print("=" * 60)

# -------- 사용자 초기 요청 (하드코딩) --------
user_input = "초보자를 위한 서핑보드를 추천해주세요."
print(f"\n🔍 초기 리서치 요청:")
print(user_input)

# -------- STEP 1: 추가 정보 수집 (Clarifier) --------
print("\n" + "=" * 60)
print("📋 STEP 1: 추가 정보 수집 중...")
clarifying_questions = agent_clarifier.run(client, user_input)
print("✅ 추가 질문 생성 완료")
print(f"\n💬 추가 질문:")
print(clarifying_questions)

# -------- 사용자 답변 시뮬레이션 (하드코딩) --------
user_clarifications = """- 완전 초보자입니다.
- 예산은 50만원 정도입니다.
- 작은~중간 크기의 해변 파도에서 탈 예정입니다.
- 안정적이고 배우기 쉬운 것을 선호합니다."""

print(f"\n💡 사용자 답변 (시뮬레이션):")
print(user_clarifications)

# -------- STEP 2: 리서치 프롬프트 재작성 (Rewriter) --------
print("\n" + "=" * 60)
print("📝 STEP 2: 리서치 프롬프트 재작성 중...")
enriched_prompt = agent_rewriter.run(client, user_input, user_clarifications)
print("✅ 프롬프트 재작성 완료")
print(f"\n📄 상세 리서치 프롬프트:")
print(enriched_prompt)

# -------- STEP 3: Deep Research 수행 (Researcher) --------
print("\n" + "=" * 60)
print("🌐 STEP 3: Deep Research 수행 중...")
print("(o4-mini-deep-research 사용 - 수 분 소요 예상)")
response = agent_researcher.run(client, enriched_prompt)
print("✅ 리서치 완료")

# -------- 최종 결과 출력 및 저장 --------
print("\n" + "=" * 60)
print("📊 최종 리서치 리포트:")
print(response.output_text)

output_file = Path(__file__).parent / "output_research.txt"
output_file.write_text(response.output_text, encoding="utf-8")

print("\n" + "=" * 60)
print("🎉 Deep Research 실습 완료!")
print(f"💾 결과 저장: {output_file}")
print("=" * 60)
