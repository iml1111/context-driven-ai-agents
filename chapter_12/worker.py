"""
Chapter 12: Production Backend Engineering - SQS Worker

SQS 메시지를 소비하고 LLM 감정 분석을 수행하는 Worker
- Long Polling으로 메시지 수신
- Graceful Shutdown (SIGINT/SIGTERM)
- 재시도 로직 (max_retries 초과 시 FAILED)
"""

import signal
import sys
import time

from config import settings
from database import JobDatabase
from llm_client import LLMClient
from models import JobStatus
from queue_client import SQSClient

# Graceful Shutdown 플래그
shutdown_requested = False


def signal_handler(sig, frame):
    """SIGINT/SIGTERM 핸들러"""
    global shutdown_requested
    print("\n⚠️ Shutdown requested. Finishing current job...")
    shutdown_requested = True


# 시그널 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Worker 메인 루프"""
    # 클라이언트 초기화
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
    print("🚀 Worker started. Polling for messages... (Ctrl+C to stop)")

    while not shutdown_requested:
        try:
            # 메시지 수신
            msg = sqs.receive_message()

            if not msg:
                # 메시지가 없으면 짧게 대기 후 재시도
                if not shutdown_requested:
                    time.sleep(settings.worker_poll_interval)
                continue

            job_id = msg.job_id
            print(f"\n📥 Processing job: {job_id}")
            print(f"   Text: {msg.input_text[:50]}...")

            # 상태를 PROCESSING으로 업데이트
            db.update_status(job_id, JobStatus.PROCESSING)
            print(f"   📊 Status: PENDING → PROCESSING")

            try:
                # 감정 분석 수행
                print(f"   🤖 Calling LLM...")
                result = llm.analyze_sentiment(msg.input_text)

                # 성공: 상태를 COMPLETED로 업데이트
                db.update_status(job_id, JobStatus.COMPLETED, output=result)
                print(f"   ✅ Status: PROCESSING → COMPLETED")
                print(f"   📊 Result: {result['sentiment']} ({result['confidence']:.2f})")

                # SQS에서 메시지 삭제
                sqs.delete_message(msg.receipt_handle)
                print(f"   🗑️ Message deleted from SQS")

            except Exception as e:
                # 실패: 재시도 횟수 확인
                current_retry = db.get_retry_count(job_id)
                max_retries = db.get_max_retries(job_id)

                print(f"   ❌ LLM Error: {str(e)[:50]}...")
                print(f"   🔄 Retry count: {current_retry}/{max_retries}")

                if current_retry < max_retries:
                    # 재시도 가능: 카운트 증가, 상태를 PENDING으로 복원
                    db.increment_retry(job_id)
                    db.update_status(job_id, JobStatus.PENDING)
                    print(f"   ⏳ Will retry later (visibility timeout)")
                    # 메시지를 삭제하지 않음 → Visibility Timeout 후 재시도
                else:
                    # 최대 재시도 초과: FAILED 처리
                    db.update_status(
                        job_id,
                        JobStatus.FAILED,
                        error=f"Max retries exceeded: {str(e)}",
                    )
                    print(f"   💀 Status: PROCESSING → FAILED")

                    # SQS에서 메시지 삭제 (더 이상 재시도하지 않음)
                    sqs.delete_message(msg.receipt_handle)
                    print(f"   🗑️ Message deleted from SQS")

        except KeyboardInterrupt:
            # Ctrl+C 처리 (signal_handler에서 이미 처리됨)
            break
        except Exception as e:
            print(f"\n❌ Worker error: {e}")
            print("   Retrying in 5 seconds...")
            time.sleep(5)

    # 정리
    print("\n🛑 Worker shutting down...")
    db.close()
    print("   ✅ MongoDB connection closed")
    sys.exit(0)


if __name__ == "__main__":
    main()
