"""
Chapter 8-1: RAG Pipeline - 수집 엔드포인트 (Ingest)

Markdown 문서를 로드하고, 청크로 분할한 후, 임베딩을 생성하여 MongoDB에 저장합니다.

[Langchain 사용 범위]
- MarkdownHeaderTextSplitter: 헤더 기준 섹션 분할
- RecursiveCharacterTextSplitter: 세부 청크 분할

[OpenAI SDK 직접 사용]
- 임베딩 생성: client.embeddings.create()

실행: python chapter_8-1/ingest.py
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from openai import OpenAI
from pymongo import MongoClient
from pymongo.collection import Collection

load_dotenv()

# 샘플 데이터 경로
SAMPLE_MD_PATH = Path(__file__).parent.parent / "assets" / "sample.md"


def split_document(text: str) -> list[dict]:
    """
    Markdown 문서를 청크로 분할합니다.

    1단계: MarkdownHeaderTextSplitter로 헤더 기준 섹션 분할
    2단계: RecursiveCharacterTextSplitter로 세부 청크 분할

    Args:
        text: Markdown 문서 텍스트

    Returns:
        list[dict]: 청크 리스트 [{"content": ..., "metadata": ...}, ...]
    """
    # STEP 1: 헤더 기준 분할
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "h1"),
            ("##", "h2"),
            ("###", "h3"),
        ]
    )
    sections = header_splitter.split_text(text)

    # STEP 2: 세부 청크 분할
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = []
    for section in sections:
        # 섹션별로 세부 분할
        sub_chunks = char_splitter.split_text(section.page_content)
        for sub_chunk in sub_chunks:
            chunks.append(
                {
                    "content": sub_chunk,
                    "metadata": section.metadata,
                }
            )

    return chunks


def store_chunks(
    collection: Collection,
    client: OpenAI,
    chunks: list[dict],
    source_name: str = "sample.md",
) -> int:
    documents = []
    total = len(chunks)

    for i, chunk in enumerate(chunks, 1):
        print(f"   🧠 임베딩 생성 중... ({i}/{total})", end="\r")

        # 임베딩 생성
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk["content"],
        )
        embedding = response.data[0].embedding

        # 문서 구성
        doc = {
            "content": chunk["content"],
            "metadata": {
                **chunk["metadata"],
                "source": source_name,
            },
            "content_vector": embedding,
        }
        documents.append(doc)

    print()  # 줄바꿈

    # 기존 데이터 삭제 후 새로 삽입 (데모용)
    collection.delete_many({})
    collection.insert_many(documents)

    return len(documents)


# ============================================================
# 메인 실행
# ============================================================


def main():
    # 클라이언트 초기화
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    mongo_client = MongoClient(os.getenv("MONGODB_URI"))
    collection = mongo_client["hackers"]["rag_demo"]

    # STEP 1: 문서 로드
    raw_text = SAMPLE_MD_PATH.read_text(encoding="utf-8")
    print(f"   📝 Markdown 로드 완료 ({len(raw_text):,}자)")

    # STEP 2: 문서 분할
    chunks = split_document(raw_text)
    print(f"   🔪 청크 분할 완료: {len(chunks)}개")

    # STEP 3: 임베딩 생성 + MongoDB 저장
    stored_count = store_chunks(
        collection,
        openai_client,
        chunks,
        source_name=SAMPLE_MD_PATH.name,
    )
    print(f"\n✅ 수집 완료! ({stored_count}개 청크)")


if __name__ == "__main__":
    main()
