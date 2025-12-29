"""
Chapter 12: Production Backend Engineering - Models

Pydantic 모델 정의
- Request/Response 스키마
- MongoDB 문서 스키마
- 열거형 정의
"""

from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """작업 상태"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SentimentResult(str, Enum):
    """감정 분석 결과"""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ============================================================
# Request Models
# ============================================================


class SentimentRequest(BaseModel):
    """감정 분석 요청"""

    text: str = Field(..., min_length=1, max_length=10000, description="분석할 텍스트")


# ============================================================
# Response Models
# ============================================================


class SyncSentimentResponse(BaseModel):
    """동기 감정 분석 응답"""

    sentiment: SentimentResult
    confidence: float = Field(..., ge=0.0, le=1.0)
    text_preview: str


class AsyncSentimentResponse(BaseModel):
    """비동기 감정 분석 응답 (Job 생성)"""

    job_id: str
    status: JobStatus
    message: str


class JobResponse(BaseModel):
    """작업 상태 조회 응답 (폴링용)"""

    job_id: str
    status: JobStatus
    input_text: str
    output: Optional[dict] = None
    error: Optional[str] = None
    retry_count: int


class HealthResponse(BaseModel):
    """헬스체크 응답"""

    status: str


# ============================================================
# MongoDB Document Schema
# ============================================================


class JobDocument(BaseModel):
    """MongoDB 작업 문서 스키마"""

    job_id: str = Field(default_factory=lambda: str(uuid4()))
    status: JobStatus = JobStatus.PENDING
    input_text: str
    output: Optional[dict] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
