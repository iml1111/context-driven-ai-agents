"""
Intent Classifier - Semantic Similarity-based Routing

[방식]
OpenAI Embeddings API를 사용하여 의미적 유사도를 계산하고 intent를 분류합니다.
Intent별 예시 문장들과 사용자 입력의 코사인 유사도를 비교합니다.

[장점]
✅ 의미적 이해: 동의어, 유사 표현 자동 처리 ("배송"과 "택배" 동일하게 인식)
✅ 예시 기반 확장: 코드 수정 없이 예시 추가로 성능 개선
✅ LLM보다 저렴: Embedding API는 LLM 추론보다 비용 낮음 (~$0.00002/request)
✅ LLM보다 빠름: Embedding 생성이 LLM 추론보다 빠름 (~50-100ms)
✅ 일관성: 동일 입력은 항상 동일 결과 (deterministic)

[단점]
❌ 초기 설정 필요: Intent별 예시 문장 준비 및 임베딩 생성
❌ 문맥 이해 제한: 복잡한 문맥, 다의적 표현은 LLM보다 약함
❌ 여전히 비용: Rule-based에 비해서는 API 비용 발생
❌ 예시 품질 의존: 예시 문장이 부실하면 정확도 하락

[적합한 사용 사례]
- 사용자 입력이 다양하지만 패턴화 가능한 경우
- LLM 비용 절감이 필요하지만 유연성은 유지하고 싶은 경우
- Intent별 대표 예시를 명확히 정의할 수 있는 경우
- 빠른 응답 + 의미적 이해 둘 다 필요한 경우

[비용/성능 특성]
- API 비용: ~$0.00002/request (text-embedding-3-small 기준)
- 응답 속도: ~50-100ms
- 정확도: 예시 품질에 따라 80-95%
"""

import json
import numpy as np


# Intent별 대표 예시 문장 정의
INTENT_EXAMPLES = {
    "faq": [
        "반품 정책이 어떻게 되나요?",
        "배송은 얼마나 걸리나요?",
        "제품 사양을 알려주세요",
        "가격이 얼마인가요?",
        "할인 이벤트가 있나요?",
        "이 제품 호환되나요?",
        "사용법을 알려주세요",
        "보증 기간이 어떻게 되나요?",
    ],
    "order": [
        "주문 ORD-12345 조회해주세요",
        "내 주문 배송 상태가 궁금해요",
        "주문이 언제 도착하나요?",
        "배송 추적 번호 알려주세요",
        "주문 확인하고 싶어요",
        "배송지 변경하고 싶습니다",
    ],
    "human": [
        "환불을 거부당했어요",
        "긴급하게 상담사와 통화하고 싶습니다",
        "불만 사항을 접수하고 싶어요",
        "이 문제 해결이 안 되고 있어요",
        "답변을 받지 못했습니다",
        "담당자와 직접 얘기하고 싶어요",
    ],
}


def get_embedding(client, text):
    """
    텍스트의 임베딩 벡터를 생성합니다.

    Args:
        client: OpenAI 클라이언트
        text: 임베딩할 텍스트

    Returns:
        list[float]: 임베딩 벡터
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def cosine_similarity(vec1, vec2):
    """
    두 벡터 간 코사인 유사도를 계산합니다.

    Args:
        vec1: 벡터 1
        vec2: 벡터 2

    Returns:
        float: 코사인 유사도 (0~1, 높을수록 유사)
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def run(client, user_message):
    """
    의미적 유사도를 사용하여 사용자 메시지를 분석하고 인텐트를 분류합니다.

    분류 전략:
    1. 사용자 입력의 임베딩 생성
    2. 각 Intent별 예시 문장들과 코사인 유사도 계산
    3. Intent별 평균 유사도 계산
    4. 가장 높은 평균 유사도의 Intent 선택
    5. Threshold (0.7) 이하면 "human" fallback

    Args:
        client: OpenAI 클라이언트
        user_message: 사용자 입력 메시지

    Returns:
        str: JSON 문자열 {"intent": "faq"|"order"|"human"}
    """
    # STEP 1: 사용자 입력 임베딩 생성
    user_embedding = get_embedding(client, user_message)

    # STEP 2: 각 Intent별로 예시들과 유사도 계산
    intent_scores = {}

    for intent, examples in INTENT_EXAMPLES.items():
        # 각 예시와 유사도 계산
        similarities = []
        for example in examples:
            example_embedding = get_embedding(client, example)
            similarity = cosine_similarity(user_embedding, example_embedding)
            similarities.append(similarity)

        # Intent별 평균 유사도 (또는 최대값 사용 가능)
        intent_scores[intent] = np.mean(similarities)

    # STEP 3: 가장 높은 점수의 intent 선택
    best_intent = max(intent_scores, key=intent_scores.get)
    best_score = intent_scores[best_intent]

    # STEP 4: Threshold 체크 (신뢰도가 낮으면 human으로 fallback)
    SIMILARITY_THRESHOLD = 0.7
    if best_score < SIMILARITY_THRESHOLD:
        best_intent = "human"

    # JSON 형식으로 반환 (다른 router들과 동일한 인터페이스)
    return json.dumps({"intent": best_intent}, ensure_ascii=False)
