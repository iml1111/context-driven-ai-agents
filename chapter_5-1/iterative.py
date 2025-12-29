"""
반복 루프 Reflection 패턴 실습

흐름:
1. 초안 생성
2. 반복 루프 (최대 3회):
   - Critic 평가
   - 종료 조건 체크 (평균 8.0 이상 OR 3회 도달)
   - Producer 개선
3. 결과 출력: 각 반복의 점수 변화 + 최종 결과
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
MAX_ITERATIONS = 3


def main():
    iteration_count = 0
    current_output = ""
    scores = []  # 각 반복의 점수 기록

    # ===== 초안 생성 =====
    print("=" * 70)
    print("📝 초안 생성")
    print("=" * 70)
    current_output = agent_producer.run(client, TOPIC)
    print(current_output)
    print()

    # ===== 반복 루프 =====
    while iteration_count < MAX_ITERATIONS:
        iteration_count += 1

        print("=" * 70)
        print(f"🔄 Iteration {iteration_count}/{MAX_ITERATIONS}")
        print("=" * 70)

        # Critique 단계
        critique = agent_critic.run(client, TOPIC, current_output)
        scores.append(critique.average)

        print(f"📊 평가 점수:")
        print(f"  - 명확성: {critique.clarity}/10")
        print(f"  - 구조: {critique.structure}/10")
        print(f"  - 완전성: {critique.completeness}/10")
        print(f"  - 실용성: {critique.practicality}/10")
        print(f"  평균: {critique.average:.1f}/10 ({critique.status})")
        print()

        print("💡 개선 제안:")
        for i, suggestion in enumerate(critique.suggestions, 1):
            print(f"  {i}. {suggestion}")
        print()

        # 종료 조건 체크
        if critique.status == "OK":
            print("🎉 목표 달성! 평균 8.0점 이상 도달. 반복 종료.")
            print()
            break

        if iteration_count >= MAX_ITERATIONS:
            print("⏱️  최대 반복 횟수 도달. 반복 종료.")
            print()
            break

        # Refine 단계
        print("✨ 개선 중...")
        current_output = agent_producer.run(client, TOPIC, critique.format_feedback())
        print("✅ 개선 완료!")
        print()

    # ===== 최종 결과 =====
    print("=" * 70)
    print("📈 점수 변화 요약")
    print("=" * 70)
    for i, score in enumerate(scores, 1):
        print(f"  Iteration {i}: {score:.1f}/10")
    print()

    if len(scores) > 1:
        improvement = scores[-1] - scores[0]
        print(f"  초안 → 최종: {scores[0]:.1f} → {scores[-1]:.1f} (향상도: {improvement:+.1f}점)")
    print()

    print("=" * 70)
    print("✅ 최종 결과")
    print("=" * 70)
    print(current_output)


if __name__ == "__main__":
    main()
