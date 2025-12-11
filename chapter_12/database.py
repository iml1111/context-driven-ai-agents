"""
Chapter 12: Production Backend Engineering - Database

MongoDB CRUD 작업 모듈
- JobDatabase: pymongo 기반 동기 클라이언트 (FastAPI + Worker 공용)
"""

from typing import Optional

from pymongo import MongoClient

from models import JobDocument, JobStatus


class JobDatabase:
    """
    동기 MongoDB 클라이언트 (FastAPI + Worker 공용)

    pymongo 라이브러리를 사용하여 단순하고 이해하기 쉬운 동기 방식으로 구현
    """

    def __init__(self, uri: str, db_name: str, collection_name: str):
        """
        Args:
            uri: MongoDB 연결 URI
            db_name: 데이터베이스 이름
            collection_name: 컬렉션 이름
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def create_job(self, input_text: str) -> JobDocument:
        """새 작업 생성 (PENDING 상태)"""
        job = JobDocument(input_text=input_text)
        self.collection.insert_one(job.model_dump())
        return job

    def get_job(self, job_id: str) -> Optional[JobDocument]:
        """작업 ID로 조회"""
        doc = self.collection.find_one({"job_id": job_id})
        if doc:
            doc.pop("_id", None)
            return JobDocument(**doc)
        return None

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        output: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> bool:
        """작업 상태 업데이트"""
        update_data = {"status": status.value}
        if output is not None:
            update_data["output"] = output
        if error is not None:
            update_data["error"] = error

        result = self.collection.update_one({"job_id": job_id}, {"$set": update_data})
        return result.modified_count > 0

    def get_retry_count(self, job_id: str) -> int:
        """현재 재시도 횟수 조회"""
        doc = self.collection.find_one({"job_id": job_id})
        return doc.get("retry_count", 0) if doc else 0

    def get_max_retries(self, job_id: str) -> int:
        """최대 재시도 횟수 조회"""
        doc = self.collection.find_one({"job_id": job_id})
        return doc.get("max_retries", 3) if doc else 3

    def increment_retry(self, job_id: str) -> int:
        """재시도 횟수 증가 후 현재 값 반환"""
        result = self.collection.find_one_and_update(
            {"job_id": job_id},
            {"$inc": {"retry_count": 1}},
            return_document=True,
        )
        return result["retry_count"] if result else 0

    def close(self):
        """연결 종료"""
        self.client.close()
