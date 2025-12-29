"""
Chapter 12: Production Backend Engineering - FastAPI Server

API 서버
- /api/v1/sentiment/sync: 동기 감정 분석 (즉시 응답)
- /api/v1/sentiment/async: 비동기 감정 분석 (Job ID 반환)
- /api/v1/jobs/{job_id}: 작업 상태 조회 (폴링용)
- /health: 헬스체크
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import JobDatabase
from llm_client import LLMClient
from models import (
    AsyncSentimentResponse,
    HealthResponse,
    JobResponse,
    JobStatus,
    SentimentRequest,
    SyncSentimentResponse,
)
from queue_client import SQSClient

# 전역 인스턴스
db: JobDatabase
sqs: SQSClient
llm: LLMClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 리소스 관리"""
    global db, sqs, llm

    # 초기화
    print("🔌 Initializing connections...")
    db = JobDatabase(
        settings.mongodb_uri,
        settings.mongodb_db,
        settings.mongodb_collection,
    )
    print(f"   ✅ MongoDB: {settings.mongodb_uri}/{settings.mongodb_db}")

    sqs = SQSClient(
        settings.aws_access_key_id,
        settings.aws_secret_access_key,
        settings.aws_region,
        settings.sqs_queue_name,
    )
    # queue_url 접근 시 자동으로 큐 확인/생성
    _ = sqs.queue_url
    print(f"   ✅ SQS Queue: {settings.sqs_queue_name}")

    llm = LLMClient(
        settings.openai_api_key,
        settings.llm_max_retries,
        settings.llm_base_delay,
    )
    print(f"   ✅ OpenAI: gpt-5.1 (max_retries={settings.llm_max_retries})")
    print("🚀 FastAPI server ready! Docs: http://localhost:8000/docs")

    yield

    # 정리
    print("\n🔌 Closing connections...")
    db.close()
    print("   ✅ MongoDB connection closed")


app = FastAPI(
    title="Chapter 12: Sentiment Analysis API",
    description="Production Backend Engineering for AI Agents - 감정 분석 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Health Check
# ============================================================


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """헬스체크 엔드포인트"""
    return HealthResponse(status="healthy")


# ============================================================
# Sync Sentiment Analysis
# ============================================================


@app.post(
    "/api/v1/sentiment/sync",
    response_model=SyncSentimentResponse,
    tags=["Sentiment Analysis"],
)
def analyze_sentiment_sync(request: SentimentRequest):
    """
    동기 감정 분석

    LLM을 직접 호출하고 결과를 즉시 반환합니다.
    응답 시간: ~1초 이상 (OpenAI API 응답 시간에 의존)
    """
    try:
        result = llm.analyze_sentiment(request.text)

        text_preview = (
            request.text[:100] + "..." if len(request.text) > 100 else request.text
        )

        return SyncSentimentResponse(
            sentiment=result["sentiment"],
            confidence=result["confidence"],
            text_preview=text_preview,
        )
    except Exception as e:
        print(f"   ❌ Sync analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail="현재 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
        )


# ============================================================
# Async Sentiment Analysis
# ============================================================


@app.post(
    "/api/v1/sentiment/async",
    response_model=AsyncSentimentResponse,
    tags=["Sentiment Analysis"],
)
def analyze_sentiment_async(request: SentimentRequest):
    """
    비동기 감정 분석

    작업을 생성하고 SQS 큐에 발행합니다.
    응답 시간: ~100ms (Job 생성 + SQS 발행)

    Worker가 처리 완료 후 MongoDB에 결과를 저장합니다.
    """
    try:
        # MongoDB에 Job 생성
        job = db.create_job(request.text)
        print(f"   📝 Created job: {job.job_id}")

        # SQS에 메시지 발행
        message_id = sqs.send_message(job.job_id, request.text)
        print(f"   📬 Sent to SQS: {message_id}")

        return AsyncSentimentResponse(
            job_id=job.job_id,
            status=JobStatus.PENDING,
            message="Job queued for processing.",
        )
    except Exception as e:
        print(f"   ❌ Async queue error: {e}")
        raise HTTPException(
            status_code=500,
            detail="현재 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
        )


# ============================================================
# Job Status (Polling)
# ============================================================


@app.get(
    "/api/v1/jobs/{job_id}",
    response_model=JobResponse,
    tags=["Jobs"],
)
def get_job(job_id: str):
    """
    작업 상태 조회 (폴링용)

    비동기 감정 분석 요청 후 이 엔드포인트로 결과를 폴링합니다.
    status가 'completed' 또는 'failed'가 될 때까지 주기적으로 호출하세요.
    """
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        input_text=job.input_text,
        output=job.output,
        error=job.error,
        retry_count=job.retry_count,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
