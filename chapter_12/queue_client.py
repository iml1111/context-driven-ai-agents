"""
Chapter 12: Production Backend Engineering - Queue Client

AWS SQS 클라이언트 래퍼
- 메시지 발행 (send_message)
- 메시지 수신 (receive_messages) - Long Polling
- 메시지 삭제 (delete_message)
"""

import json
from dataclasses import dataclass
from typing import Optional

import boto3


@dataclass
class SQSMessage:
    """SQS 메시지 데이터 클래스"""

    job_id: str
    input_text: str
    receipt_handle: Optional[str] = None


class SQSClient:
    """
    AWS SQS 클라이언트 래퍼

    실제 AWS SQS와 통신하는 클라이언트
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        queue_name: str,
    ):
        """
        Args:
            access_key: AWS Access Key ID
            secret_key: AWS Secret Access Key
            region: AWS 리전 (예: ap-northeast-2)
            queue_name: SQS 큐 이름
        """
        self.sqs = boto3.client(
            "sqs",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self.queue_name = queue_name
        self._queue_url: Optional[str] = None

    @property
    def queue_url(self) -> str:
        """큐 URL (Lazy Loading)"""
        if not self._queue_url:
            response = self.sqs.get_queue_url(QueueName=self.queue_name)
            self._queue_url = response["QueueUrl"]
        return self._queue_url

    def send_message(self, job_id: str, input_text: str) -> str:
        """
        메시지 발행

        Args:
            job_id: 작업 ID
            input_text: 분석할 텍스트

        Returns:
            SQS MessageId
        """
        message_body = json.dumps({"job_id": job_id, "input_text": input_text})

        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message_body,
        )

        return response["MessageId"]

    def receive_message(self) -> Optional[SQSMessage]:
        """
        메시지 수신 (1개)

        SQS 큐 설정(VisibilityTimeout, WaitTimeSeconds 등)을 그대로 사용

        Returns:
            SQSMessage 또는 None (메시지가 없는 경우)
        """
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=1,
        )

        messages = response.get("Messages", [])
        if not messages:
            return None

        msg = messages[0]
        body = json.loads(msg["Body"])
        return SQSMessage(
            job_id=body["job_id"],
            input_text=body["input_text"],
            receipt_handle=msg["ReceiptHandle"],
        )

    def delete_message(self, receipt_handle: str) -> None:
        """
        메시지 삭제 (처리 완료 후 호출)

        Args:
            receipt_handle: 메시지 수신 시 받은 핸들
        """
        self.sqs.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle,
        )
