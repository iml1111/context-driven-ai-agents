# Chapter 12: Production Backend Engineering for AI Agents

AI 에이전트 시스템을 위한 프로덕션급 백엔드 인프라 구축

## 학습 목표

- FastAPI 비동기 API 서버 구현 (동기/비동기 엔드포인트)
- AWS SQS 기반 작업 큐 시스템 구현
- MongoDB 기반 작업 상태 관리
- Docker 컨테이너화 및 멀티 서비스 오케스트레이션
- 프로덕션 패턴: Rate Limiting, Exponential Backoff, Graceful Shutdown

## 아키텍처

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Client        │────▶│  FastAPI     │────▶│   AWS SQS       │
│   (curl/HTTP)   │     │  (app.py)    │     │   (Real AWS)    │
└─────────────────┘     └──────┬───────┘     └────────┬────────┘
                               │                      │
                               │                      │
                               ▼                      ▼
                        ┌──────────────┐     ┌─────────────────┐
                        │   MongoDB    │◀────│   Worker        │
                        │   (Docker)   │     │   (worker.py)   │
                        └──────────────┘     └─────────────────┘
```

### 컴포넌트 설명

| 컴포넌트 | 역할 |
|----------|------|
| **FastAPI (app.py)** | HTTP API 서버. 동기/비동기 감정 분석 엔드포인트 제공 |
| **Worker (worker.py)** | SQS 메시지 소비 → LLM 호출 → 결과 저장 |
| **MongoDB** | 작업 상태 및 결과 영속화 |
| **AWS SQS** | 비동기 작업을 위한 메시지 큐 |

## 빠른 시작

### Step 1: 환경 변수 설정

```bash
cd chapter_12

# .env 파일 생성
cat > .env << 'EOF'
# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# AWS SQS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-northeast-2
SQS_QUEUE_NAME=sentiment-analysis-queue

# MongoDB (docker-compose에서 자동 설정)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=chapter_12
MONGODB_COLLECTION=jobs

# Rate Limiting
LLM_MAX_RETRIES=3
LLM_BASE_DELAY=1.0
EOF
```

### Step 2: Docker Compose로 전체 스택 실행

```bash
# 이미지 빌드 및 컨테이너 시작
docker-compose up -d --build

# 로그 확인
docker-compose logs -f
```

### Step 3: API 테스트

#### 헬스체크

```bash
curl http://localhost:8000/health
```

**응답:**
```json
{
  "status": "healthy"
}
```

#### 동기 감정 분석 (즉시 응답)

```bash
curl -X POST http://localhost:8000/api/v1/sentiment/sync \
  -H "Content-Type: application/json" \
  -d '{"text": "이 제품 정말 최고예요! 강력 추천합니다!"}'

# 응답 시간 측정 버전
curl -w "\n⏱️ Total: %{time_total}s\n" \
  -X POST http://localhost:8000/api/v1/sentiment/sync \
  -H "Content-Type: application/json" \
  -d '{"text": "이 제품 정말 최고예요! 강력 추천합니다!"}'
```

**응답:**
```json
{
  "sentiment": "positive",
  "confidence": 0.95,
  "text_preview": "이 제품 정말 최고예요! 강력 추천합니다!"
}
```

#### 비동기 감정 분석 (Job 생성)

```bash
# 1. 작업 제출
curl -X POST http://localhost:8000/api/v1/sentiment/async \
  -H "Content-Type: application/json" \
  -d '{"text": "서비스가 너무 느리고 불친절해서 실망했습니다."}'
```

**응답:**
```json
{
  "job_id": "abc12345-uuid",
  "status": "pending",
  "message": "Job queued for processing."
}
```

```bash
# 2. 결과 폴링 (job_id로 조회)
curl http://localhost:8000/api/v1/jobs/abc12345-uuid
```

**응답 (처리 완료 시):**
```json
{
  "job_id": "abc12345-uuid",
  "status": "completed",
  "input_text": "서비스가 너무 느리고 불친절해서 실망했습니다.",
  "output": {
    "sentiment": "negative",
    "confidence": 0.92
  },
  "error": null,
  "retry_count": 0
}
```

> **Note**: `status`가 `completed` 또는 `failed`가 될 때까지 주기적으로 폴링하세요.

---

## API 레퍼런스

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | 헬스체크 |
| `POST` | `/api/v1/sentiment/sync` | 동기 감정 분석 (즉시 응답) |
| `POST` | `/api/v1/sentiment/async` | 비동기 감정 분석 (Job ID 반환) |
| `GET` | `/api/v1/jobs/{job_id}` | 작업 상태 조회 (폴링용) |

### Swagger UI

서버 실행 후 브라우저에서 접속:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 프로덕션 패턴

### 1. Rate Limit & Exponential Backoff

OpenAI API Rate Limit 발생 시 자동 재시도:

```
1차 실패 → 1초 대기 → 재시도
2차 실패 → 2초 대기 → 재시도
3차 실패 → 4초 대기 → 재시도 → 실패 처리
```

### 2. SQS 설정

| 설정 | 값 | 설명 |
|------|-----|------|
| Visibility Timeout | 300초 (5분) | 메시지 처리 중 다른 Consumer에게 보이지 않음 |
| Message Retention | 86400초 (1일) | 처리되지 않은 메시지 보관 기간 |
| Long Polling | 20초 | 빈 큐에서 대기하는 최대 시간 |

### 3. Job 상태 전이

```
PENDING → PROCESSING → COMPLETED
                    ↘ FAILED (재시도 3회 초과)
```

### 4. Graceful Shutdown

Worker는 SIGINT/SIGTERM 수신 시:
1. 현재 처리 중인 작업 완료
2. 새 메시지 수신 중단
3. MongoDB 연결 종료

## 파일 구조

```
chapter_12/
├── app.py              # FastAPI 서버
├── worker.py           # SQS Consumer
├── config.py           # 환경 설정
├── models.py           # Pydantic 모델
├── database.py         # MongoDB CRUD
├── queue_client.py     # SQS 클라이언트
├── llm_client.py       # OpenAI 클라이언트
├── requirements.txt    # 의존성
├── Dockerfile          # API 서버 이미지
├── Dockerfile.worker   # Worker 이미지
├── docker-compose.yml  # 전체 스택
└── README.md           # 실행 가이드
```

---

## 정리

```bash
# 모든 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제 (MongoDB 데이터 포함)
docker-compose down -v

# 이미지 삭제
docker rmi chapter_12-api chapter_12-worker
```
