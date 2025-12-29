"""
Chapter 3-2: Intent Routing 패턴 - 다중 Router 방식 비교

이 실습에서는 동일한 Intent Routing 문제를 3가지 다른 방식으로 구현하여
각 접근법의 장단점을 비교합니다:

1. LLM-based Router: GPT-5.1을 사용한 유연한 분류
2. Rule-based Router: 키워드/패턴 기반 빠른 분류
3. Semantic Router: Embedding 기반 의미적 분류
"""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

import module_faq
import module_human
import module_order
import router_llm
import router_rule
import router_semantic

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def compare_routers(user_message):
    """
    3가지 router를 모두 실행하고 결과를 비교합니다.

    Args:
        user_message: 사용자 입력 메시지

    Returns:
        dict: 각 router의 결과 및 성능 메트릭
    """
    print(f"\n{'='*70}")
    print("🔍 Router 방식별 결과 비교")
    print(f"{'='*70}")

    results = {}

    # Router 1: LLM-based
    print("\n[1] 🤖 LLM-based Router (GPT-5.1)")
    print("    특징: 유연성 최고, 비용 발생, 200-500ms 지연")
    start = time.time()
    llm_result = router_llm.run(client, user_message)
    llm_time = (time.time() - start) * 1000
    llm_intent = json.loads(llm_result)["intent"]
    print(f"    결과: {llm_intent} (응답시간: {llm_time:.0f}ms)")
    results["llm"] = {"intent": llm_intent, "time_ms": llm_time, "json": llm_result}

    # Router 2: Rule-based
    print("\n[2] 📋 Rule-based Router (Keyword/Regex)")
    print("    특징: 즉시 응답, 무료, 패턴 명확 시 정확")
    start = time.time()
    rule_result = router_rule.run(client, user_message)
    rule_time = (time.time() - start) * 1000
    rule_intent = json.loads(rule_result)["intent"]
    print(f"    결과: {rule_intent} (응답시간: {rule_time:.0f}ms)")
    results["rule"] = {"intent": rule_intent, "time_ms": rule_time, "json": rule_result}

    # Router 3: Semantic Similarity
    print("\n[3] 🧠 Semantic Router (Embedding)")
    print("    특징: 의미 이해, 중간 비용, 50-100ms 지연")
    start = time.time()
    semantic_result = router_semantic.run(client, user_message)
    semantic_time = (time.time() - start) * 1000
    semantic_intent = json.loads(semantic_result)["intent"]
    print(f"    결과: {semantic_intent} (응답시간: {semantic_time:.0f}ms)")
    results["semantic"] = {
        "intent": semantic_intent,
        "time_ms": semantic_time,
        "json": semantic_result,
    }
    return results


def handle_user_message(user_message, router_type="llm"):
    """
    사용자 메시지를 라우팅하여 적절한 모듈로 처리합니다.

    Args:
        user_message: 사용자 입력 메시지
        router_type: 사용할 router 타입 ("llm", "rule", "semantic")

    Returns:
        str: 최종 답변
    """
    print(f"\n💬 사용자: {user_message}")

    # -------- STEP 1: Router 비교 --------
    router_results = compare_routers(user_message)

    # -------- STEP 2: 선택한 Router의 결과로 모듈 실행 --------
    selected_result = router_results[router_type]
    intent = selected_result["intent"]

    print(f"🎯 최종 선택: {router_type.upper()} Router 결과 사용 → intent: {intent}\n")

    # -------- STEP 3: Intent별 모듈 실행 --------
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
print("=" * 70)
print("Chapter 3-2: Intent Routing 패턴 - 다중 Router 방식 비교")
print("=" * 70)
print("\n🎓 학습 목표:")
print("  - LLM, Rule-based, Semantic 3가지 Routing 방식 비교")
print("  - 각 방식의 장단점 (속도, 비용, 정확도, 유연성) 체험")
print("  - 실무에서 적절한 방식 선택 기준 이해")

# 시나리오 1: FAQ (명확한 케이스)
print("\n" + "=" * 70)
print("[시나리오 1: FAQ - 명확한 제품 질문]")
answer1 = handle_user_message("반품 정책이 어떻게 되나요?", router_type="llm")
print(f"\n💡 최종 답변:\n{answer1}")

# 시나리오 2: Order (패턴 매칭 가능)
print("\n" + "=" * 70)
print("[시나리오 2: Order - 명확한 주문번호 포함]")
answer2 = handle_user_message("주문번호 ORD-12345 배송 조회 부탁드립니다", router_type="llm")
print(f"\n💡 최종 답변:\n{answer2}")

# 시나리오 3: Human (애매한 케이스 - 차이가 날 가능성)
print("\n" + "=" * 70)
print("[시나리오 3: Human Escalation - 복잡한 문제]")
answer3 = handle_user_message(
    "환불 거부당했는데 이해가 안 갑니다. 상담사 연결 부탁드립니다", router_type="llm"
)
print(f"\n💡 최종 답변:\n{answer3}")

