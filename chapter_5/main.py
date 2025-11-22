import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from counselor import MemoryCounselor
from scenario import COUNSELING_SCENARIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------- 상담 챗봇 초기화 --------
print("\n🧠 상담 챗봇 초기화 중...")
counselor = MemoryCounselor(
    client=client,
    summary_threshold=1000,  # 1000 토큰 이상 시 요약
    recent_turns=4,  # 최근 4턴은 원본 유지
)
print("✅ 초기화 완료 (임계값: 1000 토큰, 최근 유지: 4턴)")

# -------- 상담 시뮬레이션 --------
print("\n" + "=" * 60)
print("💬 심리 상담 시작")
print("=" * 60)

turn_count = 0
for user_message in COUNSELING_SCENARIO:
    turn_count += 1
    print(f"\n[턴 {turn_count}] 사용자: {user_message}")

    # 응답 생성
    assistant_response = counselor.chat(user_message)
    print(f"[턴 {turn_count}] AI 상담사: {assistant_response}")

    # 메모리 상태 표시
    stats = counselor.get_stats()
    print(
        f"📊 메모리 상태: {stats['current_tokens']} 토큰 | "
        f"히스토리: {stats['history_length']}개 메시지 | "
        f"요약 존재: {'✅' if stats['has_summary'] else '❌'}"
    )

# -------- 최종 통계 출력 --------
print("\n" + "=" * 60)
print("📈 최종 메모리 관리 통계")
print("=" * 60)

final_stats = counselor.get_stats()
print(f"\n✅ 전체 대화 턴 수: {turn_count}턴")
print(f"✅ 현재 컨텍스트 크기: {final_stats['current_tokens']} 토큰")
print(f"✅ 유지 중인 메시지: {final_stats['history_length']}개")
print(f"✅ 요약 생성 여부: {'예' if final_stats['has_summary'] else '아니오'}")

if final_stats["has_summary"]:
    print(f"\n📝 생성된 요약:")
    print(counselor.conversation_summary)

# -------- 대화 기록 저장 --------
output_file = Path(__file__).parent / "output_conversation.txt"
conversation_log = f"""심리 상담 대화 기록
{'=' * 60}

전체 대화 턴 수: {turn_count}턴
최종 컨텍스트 크기: {final_stats['current_tokens']} 토큰
유지 중인 메시지: {final_stats['history_length']}개
요약 생성 여부: {'예' if final_stats['has_summary'] else '아니오'}

"""

if final_stats["has_summary"]:
    conversation_log += f"""생성된 요약:
{counselor.conversation_summary}

{'=' * 60}

"""

conversation_log += "최근 대화 히스토리:\n"
for i, msg in enumerate(counselor.conversation_history, 1):
    role = "사용자" if msg["role"] == "user" else "AI 상담사"
    conversation_log += f"\n[{i}] {role}: {msg['content']}\n"

output_file.write_text(conversation_log, encoding="utf-8")

print("\n" + "=" * 60)
print("🎉 메모리 관리 실습 완료!")
