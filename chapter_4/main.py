import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import module_faq
import module_human
import module_order
import router

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def handle_user_message(user_message):
    """
    사용자 메시지를 라우팅하여 적절한 모듈로 처리합니다.

    Args:
        user_message: 사용자 입력 메시지

    Returns:
        str: 최종 답변
    """
    print(f"\n💬 사용자: {user_message}")

    # -------- STEP 1: Intent 분류 --------
    print("🔍 Intent 분류 중...")
    intent_json = router.run(client, user_message)
    intent_data = json.loads(intent_json)
    intent = intent_data["intent"]
    print(f"✅ 분류 결과: {intent}")
    print(f"   원본 JSON: {intent_json}")

    # -------- STEP 2: Intent별 모듈 실행 --------
    # 안전한 체크를 위해 'in' 연산자 사용 (== 대신)
    if "faq" in intent:
        print("📚 FAQ 모듈 실행 중...")
        answer = module_faq.run(client, user_message)
    elif "order" in intent:
        print("📦 Order 모듈 실행 중...")
        answer = module_order.run(client, user_message)
    elif "human" in intent:
        print("🙋 Human 모듈 실행 중...")
        answer = module_human.run(client, user_message)
    else:
        answer = f"알 수 없는 intent: {intent}"

    print("✅ 답변 생성 완료")
    return answer


# -------- 테스트 시나리오 3개 --------
print("=" * 60)
print("Chapter 4: Intent Routing 패턴 실습")
print("=" * 60)

# 시나리오 1: FAQ
print("\n[시나리오 1: FAQ]")
answer1 = handle_user_message("반품 정책이 어떻게 되나요?")
print(f"\n💡 최종 답변:\n{answer1}")

# 시나리오 2: Order
print("\n" + "=" * 60)
print("[시나리오 2: Order]")
answer2 = handle_user_message("주문번호 ORD-12345 배송 조회 부탁드립니다")
print(f"\n💡 최종 답변:\n{answer2}")

print("\n[시나리오 2.1: Invalid Order]")
answer2 = handle_user_message("주문번호 ORD-99999 배송 조회 부탁드립니다")
print(f"\n💡 최종 답변:\n{answer2}")

# 시나리오 3: Human
print("\n" + "=" * 60)
print("[시나리오 3: Human Escalation]")
answer3 = handle_user_message("환불 거부당했는데 이해가 안 갑니다. 상담사 연결 부탁드립니다")
print(f"\n💡 최종 답변:\n{answer3}")

print("\n" + "=" * 60)
print("🎉 모든 시나리오 완료!")
print("=" * 60)
