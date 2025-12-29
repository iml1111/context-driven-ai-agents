"""
Chapter 8-1: RAG Pipeline - 질의 엔드포인트 (Query)

사용자 질문을 받아 Vector Search로 관련 문서를 검색하고,
LLM을 사용하여 답변을 생성합니다.

실행: python chapter_8-1/query.py
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient

load_dotenv()

SYSTEM_PROMPT = """당신은 제공된 문서를 기반으로 질문에 답변하는 AI 어시스턴트입니다.

규칙:
1. 제공된 컨텍스트의 정보를 우선적으로 활용하여 답변하세요.
2. 컨텍스트에서 직접 언급되지 않더라도, 맥락상 추론 가능한 내용은 답변해도 됩니다.
3. 답변은 명확하고 간결하게 작성하세요.
4. 답변 시 참고한 컨텍스트 번호를 [1], [2] 형식으로 본문에 인용 표시하세요."""


def main():
    # 클라이언트 초기화
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    mongo_client = MongoClient(os.getenv("MONGODB_URI"))
    collection = mongo_client["hackers"]["rag_demo"]

    # 하드코딩된 질문
    query = "데이터북 기준 나루토와 사스케의 스태미나 수치는 각각 얼마이며, 이 차이가 최종전에서 어떤 영향을 미쳤나요?"
    print(f"\n🙋 질문: {query}")

    # STEP 1: Vector Search로 관련 문서 검색
    print("\n🔍 검색 중...")
    t0 = time.perf_counter()

    # 쿼리 임베딩 생성
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    query_embedding = embedding_response.data[0].embedding

    # MongoDB $vectorSearch
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "content_vector",
                "queryVector": query_embedding,
                "numCandidates": 40,
                "limit": 5,
            }
        },
        {
            "$project": {
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    documents = list(collection.aggregate(pipeline))

    search_time = time.perf_counter() - t0
    print(f"   → {len(documents)}개 문서 검색됨 ({search_time:.2f}초)")

    # 검색된 컨텍스트 미리보기
    if documents:
        print("\n📄 검색된 컨텍스트:")
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            score = doc.get("score", 0)
            preview = content.replace("\n", " ")[:80]
            print(f"   [{i}] (score: {score:.4f}) {preview}...")

    # STEP 2: 컨텍스트 포맷팅
    if not documents:
        context = "관련 문서를 찾을 수 없습니다."
    else:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            score = doc.get("score", 0)
            context_parts.append(f"[{i}] (score: {score:.4f})\n{content}")
        context = "\n\n".join(context_parts)

    # STEP 3: LLM으로 답변 생성
    print("\n💡 답변 생성 중...")
    t0 = time.perf_counter()

    response = openai_client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"컨텍스트:\n{context}\n\n질문: {query}"},
        ],
    )
    answer = response.choices[0].message.content

    gen_time = time.perf_counter() - t0
    print(f"   → 답변 생성 완료 ({gen_time:.2f}초)")

    print(f"\n✅ 답변:\n{answer}")


if __name__ == "__main__":
    main()
