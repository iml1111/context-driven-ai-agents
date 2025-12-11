"""
Chapter 12: Production Backend Engineering - Configuration

환경 변수 관리를 위한 중앙 설정 모듈
pydantic-settings를 사용하여 타입 안전한 설정 관리
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # OpenAI
    openai_api_key: str

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "chapter_12"
    mongodb_collection: str = "jobs"

    # AWS SQS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-northeast-2"
    sqs_queue_name: str = "sentiment-analysis-queue"

    # Rate Limiting
    llm_max_retries: int = 3
    llm_base_delay: float = 1.0  # seconds

    # Worker
    worker_poll_interval: int = 1  # seconds between polls when no messages

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()
