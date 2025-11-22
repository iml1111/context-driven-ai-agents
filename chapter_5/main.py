import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from counselor import MemoryCounselor
from scenario import COUNSELING_SCENARIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("=" * 60)
print("Chapter 5: 요약 기반 메모리 관리 실습")
print("=" * 60)

# -------- 상담 챗봇 초기화 --------
print("\n🧠 상담 챗봇 초기화 중...")
counselor = MemoryCounselor(
    client=client,
    summary_threshold=2000,  # 2000 토큰 이상 시 요약
    recent_turns=5,  # 최근 5턴은 원본 유지
)
print("✅ 초기화 완료 (임계값: 2000 토큰, 최근 유지: 5턴)")

# -------- 상담 시뮬레이션 --------
print("\n" + "=" * 60)
print("💬 심리 상담 시작")
print("=" * 60)

turn_count = 0
for user_message in COUNSELING_SCENARIO:
    turn_count += 1
    print(f"\n[턴 {turn_count}] 내담자: {user_message}")

    # 응답 생성
    assistant_response = counselor.chat(user_message)
    print(f"[턴 {turn_count}] 상담사: {assistant_response}")

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

# -------- 메모리 테스트 결과 분석 --------
print("\n" + "=" * 60)
print("🔍 메모리 테스트 결과 분석")
print("=" * 60)

print("\n마지막 2개 질문은 초기 정보 기억 테스트였습니다:")
print("1. '처음에 뭐가 제일 힘들다고 했죠?'")
print("   → 기대 답변: 상사와의 관계, 직장 스트레스")
print("\n2. '학창 시절에 어떤 경험이 있다고 말씀드렸나요?'")
print("   → 기대 답변: 중학교 때 친구들의 따돌림")

print("\n💡 요약 기반 메모리 관리의 장점:")
print("- 오래된 대화를 압축하여 컨텍스트 크기 제한")
print("- 최근 대화는 원본 유지로 자연스러운 흐름 보존")
print("- 핵심 정보는 요약에 포함되어 장기 기억 유지")
print("- 토큰 비용 절감 및 응답 속도 향상")

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
    role = "내담자" if msg["role"] == "user" else "상담사"
    conversation_log += f"\n[{i}] {role}: {msg['content']}\n"

output_file.write_text(conversation_log, encoding="utf-8")

print("\n" + "=" * 60)
print("🎉 메모리 관리 실습 완료!")
