"""
Chapter 5-2: Learning & Adaptation Pattern

ACE (Agentic Context Engineering) 패턴의 단순화 버전
- Generator → Reflector → Curator 3-에이전트 워크플로우
- 2-Epoch 구조: 학습 모드 → 평가 모드
- Before/After 성능 비교로 학습 효과 시연

실행: python chapter_5-2/main.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# 로컬 모듈 import
from playbook import Playbook
from scenario import TASKS, evaluate
import agent_generator
import agent_reflector
import agent_curator


def run_epoch(client: OpenAI, playbook: Playbook, epoch_num: int, learn_mode: bool = True) -> int:
    """
    단일 Epoch 실행

    Args:
        client: OpenAI 클라이언트
        playbook: 현재 플레이북
        epoch_num: Epoch 번호 (1 또는 2)
        learn_mode: True면 학습 모드 (실수 시 플레이북 업데이트), False면 평가 모드

    Returns:
        정답 개수
    """
    correct_count = 0

    for i, task in enumerate(TASKS, 1):
        print("=" * 70)
        print(f"📝 Task {i}/{len(TASKS)}: {task['question']}")
        print("-" * 70)

        # 1. Generate: 현재 플레이북을 사용하여 답변 생성
        print(f"🤖 Generator: 답변 생성 중...")
        result = agent_generator.run(client, playbook, task['question'])
        answer = result['answer']
        reasoning = result.get('reasoning', 'N/A')

        print(f"  답변: {answer}")
        print(f"  추론: {reasoning}")

        # 2. Evaluate: 답변 평가
        is_correct = evaluate(answer, task['ground_truth'])

        if is_correct:
            print(f"  ✅ 정답!")
            correct_count += 1
        else:
            print(f"  ❌ 오답! (정답: {task['ground_truth']})")

            # 학습 모드에서만 플레이북 업데이트
            if learn_mode:
                print()

                # 3. Reflect: 실수 분석 및 인사이트 추출
                print(f"🔍 Reflector: 실수 분석 중...")
                reflection = agent_reflector.run(client, task, result, is_correct)
                insight = reflection['insight']
                category = reflection['category']

                print(f"  인사이트: {insight}")
                print(f"  카테고리: {category}")
                print()

                # 4. Curate: 새로운 플레이북 항목 제안
                print(f"💡 Curator: 플레이북 업데이트 제안 중...")
                new_items = agent_curator.run(client, playbook, reflection)

                if new_items:
                    for item in new_items:
                        playbook.add(item)
                        print(f"  ✅ 추가됨: [{item.category}] {item.content}")
                else:
                    print(f"  ⚠️  유사한 항목이 이미 존재하여 추가하지 않음")
                print()

        # 5. Progress: 현재 플레이북 상태 출력
        print(f"📊 플레이북 상태: {len(playbook.items)}개 항목")
        print()

    return correct_count


def main():
    """Learning & Adaptation 패턴 실행 (2-Epoch)"""
    # 환경 변수 로드
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    # OpenAI 클라이언트 초기화
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 빈 플레이북 초기화
    playbook = Playbook()

    # ========================================================================
    # EPOCH 1: 학습 모드 (빈 플레이북 → 실수하며 학습)
    # ========================================================================
    print("🎓 EPOCH 1: 학습 모드 (Learning from Mistakes)\n")

    epoch1_correct = run_epoch(client, playbook, epoch_num=1, learn_mode=True)
    epoch1_accuracy = (epoch1_correct / len(TASKS)) * 100

    print("📊 EPOCH 1 결과\n")
    print(f"정답: {epoch1_correct}/{len(TASKS)} ({epoch1_accuracy:.0f}%)")
    print(f"플레이북 크기: {len(playbook.items)}개 항목")
    print()

    # ========================================================================
    # EPOCH 2: 평가 모드 (학습된 플레이북 → 성능 향상 확인)
    # ========================================================================
    print("🎯 EPOCH 2: 평가 모드 (Testing with Learned Playbook)\n")

    epoch2_correct = run_epoch(client, playbook, epoch_num=2, learn_mode=False)
    epoch2_accuracy = (epoch2_correct / len(TASKS)) * 100

    print("📊 EPOCH 2 결과\n")
    print(f"정답: {epoch2_correct}/{len(TASKS)} ({epoch2_accuracy:.0f}%)")
    print(f"플레이북 크기: {len(playbook.items)}개 항목 (변경 없음)")
    print()

    # ========================================================================
    # 최종 요약
    # ========================================================================
    print("🎉 학습 완료!\n")

    # 성능 비교
    print("📈 성능 비교 (Before vs After Learning)")
    print("-" * 70)
    print(f"EPOCH 1 (학습 전): {epoch1_correct}/{len(TASKS)} ({epoch1_accuracy:.0f}%) - 플레이북 0개 → {len(playbook.items)}개")
    print(f"EPOCH 2 (학습 후): {epoch2_correct}/{len(TASKS)} ({epoch2_accuracy:.0f}%) - 플레이북 {len(playbook.items)}개 활용")
    improvement = epoch2_accuracy - epoch1_accuracy
    print(f"개선도: +{improvement:.0f}%p")
    print()

    # 최종 플레이북 내용 출력
    print("📚 학습된 플레이북 내용:")
    print("-" * 70)
    if playbook.items:
        for item in playbook.items:
            print(f"[{item.id}] [{item.category}] {item.content}")
    else:
        print("(플레이북이 비어있습니다)")
    print()

    # 플레이북 저장
    output_path = Path(__file__).parent / "output_playbook_final.json"
    playbook.save(str(output_path))
    print(f"💾 플레이북 저장: {output_path.name}")
    print(f"📈 최종 항목 수: {len(playbook.items)}개")

if __name__ == "__main__":
    main()
