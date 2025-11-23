"""
단일 루프 Reflection 패턴 실습

흐름:
1. Generate: Producer가 초안 생성
2. Critique: Critic이 초안 평가
3. Refine: Producer가 피드백 반영하여 개선
4. 결과 출력: 초안 vs 개선본 비교
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
import agent_producer
import agent_critic

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 실습 주제
TOPIC = "AI 에이전트를 활용한 생산성 향상 방법"


def main():
    # ===== STEP 1: 초안 생성 =====
    print("=" * 70)
    print("📝 STEP 1: 초안 생성")
    print("=" * 70)
    draft = agent_producer.run(client, TOPIC)
    print(draft)
    print()

    # ===== STEP 2: 품질 평가 =====
    print("=" * 70)
    print("🔍 STEP 2: 품질 평가")
    print("=" * 70)
    critique = agent_critic.run(client, TOPIC, draft)

    print(f"📊 평가 점수:")
    print(f"  - 명확성 (Clarity): {critique.clarity}/10")
    print(f"  - 구조 (Structure): {critique.structure}/10")
    print(f"  - 완전성 (Completeness): {critique.completeness}/10")
    print(f"  - 실용성 (Practicality): {critique.practicality}/10")
    print(f"  평균: {critique.average:.1f}/10")
    print()

    print("💡 개선 제안:")
    for i, suggestion in enumerate(critique.suggestions, 1):
        print(f"  {i}. {suggestion}")
    print()

    # ===== STEP 3: 최종 개선 =====
    print("=" * 70)
    print("✨ STEP 3: 최종 개선")
    print("=" * 70)
    print("개선 중...")
    improved = agent_producer.run(client, TOPIC, critique.format_feedback())
    print()
    print(improved)
    print()

    # ===== STEP 4: 최종 평가 (선택적) =====
    print("=" * 70)
    print("🎯 STEP 4: 최종 품질 확인")
    print("=" * 70)
    final_critique = agent_critic.run(client, TOPIC, improved)

    print(f"📊 최종 점수:")
    print(f"  - 명확성: {final_critique.clarity}/10")
    print(f"  - 구조: {final_critique.structure}/10")
    print(f"  - 완전성: {final_critique.completeness}/10")
    print(f"  - 실용성: {final_critique.practicality}/10")
    print(f"  평균: {final_critique.average:.1f}/10")


if __name__ == "__main__":
    main()
