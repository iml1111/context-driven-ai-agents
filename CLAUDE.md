# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요 (Project Overview)

**강의명**: [AI Agent 시대의 새 공식] CONTEXT로 완성하는 멀티 에이전트 워크플로우

이 저장소는 AI 에이전트를 설계하고 활용하는 실습 코드 레포지토리입니다. 특정 프레임워크에 구애받지 않고, **컨텍스트 기반 설계**와 **자기개선형 에이전트** 구현에 중점을 둡니다.

### 핵심 원칙
- **컨텍스트 중심 설계**: 프롬프트보다 컨텍스트를 통한 에이전트 제어
- **자기개선형 아키텍처**: LLM이 스스로 프롬프트와 컨텍스트를 개선하도록 설계
- **프레임워크 독립적 사고**: 특정 도구에 의존하지 않는 핵심 원리 이해
- **실무 중심 학습**: 프로덕션 환경을 고려한 설계·운영·확장

## 개발 환경 설정

### Python 환경
이 프로젝트는 Python 기반으로 개발됩니다. 다음 도구들 중 하나를 사용할 수 있습니다:
- **uv**: 권장 (빠른 패키지 관리)
- **poetry**: 의존성 관리
- **venv**: 표준 가상환경

### 환경 설정 명령어
```bash
# uv 사용시
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# poetry 사용시
poetry install
poetry shell

# 표준 venv 사용시
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 프로젝트 구조

이 저장소는 **차시별 폴더 격리 방식**으로 구성되어 있습니다. 각 챕터는 독립적으로 실행 가능하며, 순차적으로 학습할 수 있도록 설계되었습니다.

```
context-driven-ai-agents/
├── assets/
│   └── sample.pdf              # 공유 리소스: PDF 샘플 파일
├── chapter_0/
│   └── main.py                  # Fact-Check Agent (Plan → Analysis, web_search)
├── chapter_1/
│   └── main.py                  # 2단계 파이프라인 (코드 분석 → 보고서 생성)
├── chapter_2/
│   ├── exercise1_before.py     # 실습#1 Before: 회의 메모 분석 (간단한 프롬프트)
│   ├── exercise1_after.py      # 실습#1 After: 회의 메모 분석 (구조화 + Pydantic 검증)
│   ├── exercise2_before.py     # 실습#2 Before: ROAS 계산 (단순 프롬프트)
│   └── exercise2_after.py      # 실습#2 After: ROAS 계산 (CoT + Self-Consistency)
├── chapter_3/
│   ├── main.py                  # 3단계 체인 오케스트레이션
│   ├── step1_summarize.py      # STEP 1: Market Analyst (PDF 요약)
│   ├── step2_trends.py         # STEP 2: Trend Analyst (트렌드 추출)
│   └── step3_email.py          # STEP 3: Documentation Writer (이메일 작성)
├── chapter_3-2/
│   ├── main.py                  # Intent Routing 오케스트레이션 (3가지 router 비교 모드)
│   ├── router.py               # Intent Classifier (기존, 참고용)
│   ├── router_llm.py           # LLM-based Router (GPT-5.1)
│   ├── router_rule.py          # Rule-based Router (Keyword/Regex)
│   ├── router_semantic.py      # Semantic Router (Embedding 유사도)
│   ├── module_faq.py           # FAQ 모듈 (제품 관련 질문 답변)
│   ├── module_order.py         # Order 모듈 (주문 조회, Mock DB)
│   └── module_human.py         # Human 모듈 (상담사 연결, Mock 티켓)
├── chapter_4/
│   ├── main.py                  # Planning 패턴 오케스트레이션
│   ├── agent_planner.py        # Planner 에이전트 (요약 계획 생성)
│   └── agent_writer.py         # Writer 에이전트 (계획 기반 요약 작성)
├── chapter_4-2/
│   ├── main.py                  # Deep Research 오케스트레이션
│   ├── agent_clarifier.py      # Clarifier 에이전트 (추가 질문 생성)
│   ├── agent_rewriter.py       # Rewriter 에이전트 (프롬프트 재작성)
│   └── agent_researcher.py     # Deep Research 에이전트 (웹 검색 리서치)
├── chapter_4-3/
│   ├── main.py                  # 메모리 관리 실습 오케스트레이션
│   ├── scenario.py             # 심리 상담 시나리오 (11턴)
│   └── counselor.py            # MemoryCounselor 클래스 (요약 기반 메모리)
├── chapter_5-1/
│   ├── agent_producer.py       # Producer 에이전트 (블로그 글 생성/개선)
│   ├── agent_critic.py         # Critic 에이전트 (점수 기반 평가)
│   ├── single_pass.py          # 단일 루프 모드 (1회 Reflection)
│   └── iterative.py            # 반복 루프 모드 (최대 3회)
├── chapter_5-2/
│   ├── main.py                 # Learning & Adaptation 오케스트레이션
│   ├── playbook.py             # 플레이북 데이터 구조 및 관리
│   ├── scenario.py             # 5개 Mock 태스크 (수학/재무 계산)
│   ├── agent_generator.py      # Generator 에이전트 (플레이북 사용)
│   ├── agent_reflector.py      # Reflector 에이전트 (인사이트 추출)
│   └── agent_curator.py        # Curator 에이전트 (플레이북 업데이트)
├── chapter_7-1/
│   ├── main.py                 # Tool Loop 오케스트레이션 (여행 도우미)
│   └── tools.py                # Tool 정의 + Mock 데이터 (날씨/환율)
├── chapter_7-2/
│   ├── main.py                 # Tool 통합 오케스트레이션 (회식 코스 플래너)
│   ├── tools.py                # 통합 Tool 정의 + 카카오 로컬 API + JSON 파일
│   └── course_data.json        # 코스 데이터 저장 (런타임 자동 생성)
├── chapter_8-1/
│   ├── ingest.py               # RAG 수집: Markdown → 청크 → 임베딩 → MongoDB
│   ├── query.py                # RAG 질의: Vector Search → LLM 답변 생성 (단일 실행)
│   └── requirements.txt        # 의존성
├── chapter_9-1/
│   ├── main.py                 # Study Buddy Agent (MCP 연동 + 대화형 루프)
│   └── requirements.txt        # 의존성 (openai)
├── chapter_9-2/
│   ├── server.py               # Mock Calendar MCP Server (FastMCP + SSE)
│   ├── main.py                 # Calendar Agent (MCP Client + Function Calling)
│   └── requirements.txt        # 의존성 (mcp, openai)
├── chapter_10/
│   ├── main.py                 # Supervisor Tool Loop 오케스트레이션
│   ├── tools.py                # 5개 Tool 정의 + execute_tool() 라우팅
│   ├── agent_pm.py             # PM Agent: 요구사항 추출 (web_search)
│   ├── agent_designer.py       # Designer Agent: UI/UX 기획 (web_search)
│   ├── agent_architect.py      # Architect Agent: 코드 생성
│   ├── agent_tester.py         # Tester Agent: LLM 기반 동적 E2E 테스트
│   └── output/                 # 생성된 산출물 저장
│       ├── requirements.md
│       ├── design_spec.md
│       ├── app.html
│       ├── test_report.md
│       └── README.md
├── chapter_11/
│   ├── main.py                 # CLI Entry Point + 데모 시나리오
│   ├── protocol.py             # A2A 영감: Message, Part, AgentCard, AgentRole 정의
│   ├── base_agent.py           # BaseAgent ABC (추상 기반 클래스)
│   ├── context_manager.py      # ContextManager: .md 파일 I/O + 요약
│   ├── orchestrator.py         # DebateOrchestrator: State Machine
│   ├── agent_judge.py          # JudgeAgent: 토론 조율, 평가, 최종 판정
│   ├── agent_debater.py        # DebaterAgent: 주장 전개, web_search 사용
│   ├── factory.py              # 에이전트/오케스트레이터 팩토리 함수
│   ├── memory/                 # 런타임 생성 .md 파일 (gitignore)
│   │   ├── debate_history.md   # 메인 공유 컨텍스트
│   │   ├── judge_context.md    # 판사 비공개 메모
│   │   ├── debater_pro_context.md  # PRO 전략 메모
│   │   └── debater_con_context.md  # CON 전략 메모
│   └── output/
│       └── debate_summary.md   # 최종 판정 결과
├── chapter_12/
│   ├── app.py                  # FastAPI 서버 (동기/비동기 감정 분석 API)
│   ├── worker.py               # SQS Consumer (작업 처리 워커)
│   ├── config.py               # 환경 설정 (pydantic-settings)
│   ├── models.py               # Pydantic 모델 + MongoDB 스키마
│   ├── database.py             # MongoDB CRUD (pymongo 동기 클라이언트)
│   ├── queue_client.py         # AWS SQS 클라이언트 (boto3)
│   ├── llm_client.py           # OpenAI 클라이언트 (Rate Limit, Retry)
│   ├── requirements.txt        # 의존성
│   ├── Dockerfile              # API 서버용 Docker 이미지
│   ├── Dockerfile.worker       # Worker용 Docker 이미지
│   ├── docker-compose.yml      # 전체 스택 오케스트레이션
│   └── README.md               # 실행 가이드
└── scripts/                     # 유틸리티 및 실험 스크립트
```

### 공유 리소스 (assets/)

**assets/** 디렉토리는 여러 챕터에서 공통으로 사용하는 리소스를 관리합니다:
- **sample.pdf**: Chapter 3 및 기타 챕터에서 사용하는 PDF 샘플 파일
- **sample.md**: Chapter 8-1 RAG Pipeline에서 사용하는 Markdown 샘플 파일
- 다른 챕터에서 접근 시: `Path(__file__).parent.parent / "assets" / "파일명"`

### 챕터 구성

#### Chapter 0: Fact-Check Agent (무료 맛보기)
- **주제**: 특정 정보에 대해 True/False 팩트 체크를 수행하는 에이전트
- **파일**: [main.py](chapter_0/main.py)
- **학습 목표**:
  - Plan → Analysis 2단계 워크플로우 이해
  - OpenAI Responses API + web_search 도구 활용
  - Confidence 기반 신뢰도 수치 반환
- **워크플로우**:
  - Plan: 팩트체크를 위한 체크리스트 생성
  - Analysis: 체크리스트 기반 분석 (web_search 활용)
- **출력**: verdict (TRUE/FALSE) + confidence (0~1)

#### Chapter 1: 프롬프트 기반 접근의 기초
- **주제**: 2단계 파이프라인 구조 (분석 → 포맷팅)
- **파일**: [main.py](chapter_1/main.py)
- **학습 목표**:
  - 하드코딩된 프롬프트의 한계 이해
  - LLM 파이프라인 기본 구조 학습
  - 중간 결과(JSON) 전달 방식 이해

#### Chapter 2: Prompt vs Context Engineering
- **주제**: Before/After 비교를 통한 프롬프트 엔지니어링 개선
- **실습 #1**: 회의 메모 → 액션 아이템 추출
  - Before: 간단한 프롬프트
  - After: 구조화된 프롬프트 + Pydantic 스키마 검증
- **실습 #2**: 마케팅 캠페인 ROAS 계산
  - Before: 단일 프롬프트
  - After: CoT(Chain of Thought) + Self-Consistency (5개 후보 → 다수결)
- **학습 목표**:
  - 프롬프트 구조화의 중요성
  - 스키마 검증으로 출력 품질 보장
  - 다수결 패턴으로 일관성 향상

#### Chapter 3: Prompt Chaining
- **주제**: 3단계 프롬프트 체인 구현 (PDF → 요약 → 트렌드 → 이메일)
- **파일**:
  - [main.py](chapter_3/main.py) - 전체 체인 오케스트레이션
  - [step1_summarize.py](chapter_3/step1_summarize.py) - Market Analyst 역할
  - [step2_trends.py](chapter_3/step2_trends.py) - Trend Analyst 역할
  - [step3_email.py](chapter_3/step3_email.py) - Documentation Writer 역할
- **학습 목표**:
  - Prompt Chaining 패턴 이해
  - 단계별 출력 → 입력 연결 구조
  - OpenAI Responses API 사용법
  - Files API로 PDF 처리
  - 역할별 프롬프트 설계

#### Chapter 3-2: Intent Routing - 다중 Router 방식 비교
- **주제**: 동일한 Intent Routing 문제를 3가지 다른 방식으로 구현하여 비교
- **파일**:
  - [main.py](chapter_3-2/main.py) - 3가지 Router 비교 오케스트레이션
  - [router_llm.py](chapter_3-2/router_llm.py) - LLM-based Router (GPT-5.1)
  - [router_rule.py](chapter_3-2/router_rule.py) - Rule-based Router (Keyword/Regex)
  - [router_semantic.py](chapter_3-2/router_semantic.py) - Semantic Router (Embedding 유사도)
  - [module_faq.py](chapter_3-2/module_faq.py) - FAQ 모듈 (제품 질문 답변)
  - [module_order.py](chapter_3-2/module_order.py) - Order 모듈 (주문 조회, Mock DB)
  - [module_human.py](chapter_3-2/module_human.py) - Human 모듈 (상담사 연결, Mock 티켓)
- **학습 목표**:
  - **3가지 Routing 방식 비교**: LLM-based, Rule-based, Semantic Similarity
  - **Trade-off 체험**: 속도 vs 비용 vs 정확도 vs 유연성 균형점 이해
  - **실무 선택 기준**: 각 방식의 장단점과 적합한 사용 사례 파악
  - **성능 메트릭 측정**: 응답 시간, API 비용, 분류 일치도 비교
  - **동일 입력에 대한 결과 비교**: 3가지 방식이 같은/다른 결과를 내는 경우 분석

#### Chapter 4: Planning 패턴
- **주제**: "Plan → 실행" 2단계 에이전트 협업 (Planner → Writer)
- **파일**:
  - [main.py](chapter_4/main.py) - Planning 패턴 오케스트레이션
  - [agent_planner.py](chapter_4/agent_planner.py) - Planner 에이전트 (요약 계획 수립)
  - [agent_writer.py](chapter_4/agent_writer.py) - Writer 에이전트 (계획 기반 요약 작성)
- **학습 목표**:
  - Planning 패턴 이해 (계획 수립과 실행의 분리)
  - 2단계 에이전트 협업 구조
  - Planner: PDF 분석하여 요약 계획(불릿 리스트) 생성
  - Writer: Planner의 계획 + PDF를 받아 최종 요약 작성
  - 에이전트 간 컨텍스트 전달 (file_id + plan)

#### Chapter 4-2: Deep Research (매니지드 Planning)
- **주제**: OpenAI Deep Research - 3단계 Planning & Research 프로세스
- **파일**:
  - [main.py](chapter_4-2/main.py) - Deep Research 오케스트레이션
  - [agent_clarifier.py](chapter_4-2/agent_clarifier.py) - Clarifier 에이전트 (추가 질문 생성)
  - [agent_rewriter.py](chapter_4-2/agent_rewriter.py) - Rewriter 에이전트 (프롬프트 재작성)
  - [agent_researcher.py](chapter_4-2/agent_researcher.py) - Deep Research 에이전트 (웹 검색 리서치)
- **학습 목표**:
  - ChatGPT Deep Research의 3단계 프로세스 이해
  - Clarification → Rewriting → Research 패턴
  - o4-mini-deep-research 모델 + web_search_preview 사용법
  - 장기 실행 태스크 처리 (timeout 설정)
  - 매니지드 Planning & Research API 활용

#### Chapter 4-3: 요약 기반 메모리 관리
- **주제**: LLM의 단기 메모리 관리 - 요약 기반 컨텍스트 압축
- **파일**:
  - [main.py](chapter_4-3/main.py) - 메모리 관리 실습 오케스트레이션
  - [scenario.py](chapter_4-3/scenario.py) - 심리 상담 시나리오 (11턴)
  - [counselor.py](chapter_4-3/counselor.py) - MemoryCounselor 클래스 (요약 기반 메모리)
- **학습 목표**:
  - 긴 대화에서 컨텍스트 비대화 문제 이해
  - 요약 기반 메모리 압축 전략 구현 (임계값: 1000 토큰, 최근 4턴 유지)
  - 최근 대화 유지 + 오래된 대화 요약 패턴
  - 토큰 사용량 추적 및 압축 트리거 로직
  - 메모리 테스트로 장기 기억 검증

#### Chapter 5-1: Reflection Pattern (단일/반복 루프)
- **주제**: Generate → Critique → Refine 패턴의 두 가지 운용 방식
- **파일**:
  - [agent_producer.py](chapter_5-1/agent_producer.py) - Producer 에이전트 (블로그 글 생성/개선)
  - [agent_critic.py](chapter_5-1/agent_critic.py) - Critic 에이전트 (점수 기반 평가)
  - [single_pass.py](chapter_5-1/single_pass.py) - 단일 루프 모드 (1회 Reflection)
  - [iterative.py](chapter_5-1/iterative.py) - 반복 루프 모드 (최대 3회)
- **학습 목표**:
  - Reflection 패턴의 두 가지 운용 방식 이해
  - 단일 vs 반복 루프의 품질·비용·지연 트레이드오프 체감
  - 점수 기반 평가 및 종료 조건 설계
  - 상태 관리와 점진적 개선 프로세스
  - Producer-Critic 에이전트 협업 패턴

#### Chapter 5-2: Learning & Adaptation Pattern
- **주제**: ACE (Agentic Context Engineering) 단순화 버전 - 2-Epoch 학습을 통한 성능 향상 시연
- **파일**:
  - [main.py](chapter_5-2/main.py) - 2-Epoch 오케스트레이션 (학습 모드 → 평가 모드)
  - [playbook.py](chapter_5-2/playbook.py) - 플레이북 데이터 구조 및 관리
  - [scenario.py](chapter_5-2/scenario.py) - 5개 Mock 태스크 (수학/재무 계산)
  - [agent_generator.py](chapter_5-2/agent_generator.py) - Generator 에이전트 (플레이북 사용)
  - [agent_reflector.py](chapter_5-2/agent_reflector.py) - Reflector 에이전트 (인사이트 추출)
  - [agent_curator.py](chapter_5-2/agent_curator.py) - Curator 에이전트 (플레이북 업데이트)
- **학습 목표**:
  - ACE의 Learning & Adaptation 메커니즘 이해
  - Generator → Reflector → Curator 3-에이전트 워크플로우
  - 구조화된 플레이북 (itemized bullets) 진화 과정
  - 2-Epoch 구조: EPOCH 1 (학습) → EPOCH 2 (평가) → Before/After 성능 비교
  - Reflection Pattern과의 차이점 (단일 콘텐츠 개선 vs 재사용 가능한 지식 축적)

#### Chapter 7-1: Tool 컨셉 - 여행 준비 도우미
- **주제**: OpenAI Function Calling(Tools) API를 활용한 에이전트 구현
- **파일**:
  - [main.py](chapter_7-1/main.py) - Tool Loop 오케스트레이션 (테스트 시나리오 3개)
  - [tools.py](chapter_7-1/tools.py) - Tool 정의 + Mock 데이터 (날씨/환율)
- **학습 목표**:
  - **Tool Definition**: JSON Schema 기반 도구 정의 방법
  - **LLM 의사결정**: LLM이 스스로 어떤 도구를 호출할지 판단
  - **Tool Execution Loop**: tool_calls → 실행 → 결과 전달 → 최종 응답 흐름
  - **Multi-tool 호출**: 단일 요청에서 여러 도구 동시 호출 처리
- **Mock 데이터**: 서울, 도쿄, 상하이 (날씨 + 환율)

#### Chapter 7-2: Tool 통합 - 회식 코스 플래너
- **주제**: 도구에서 생성되는 과도한 컨텍스트 방지 - Tool 통합 패턴
- **파일**:
  - [main.py](chapter_7-2/main.py) - Tool 통합 오케스트레이션 (회식 코스 시나리오)
  - [tools.py](chapter_7-2/tools.py) - 통합 Tool 정의 + 카카오 로컬 API + JSON 파일
  - `course_data.json` - 코스 데이터 저장 (런타임 자동 생성)
- **학습 목표**:
  - **Tool 통합 패턴**: 관련 API들을 action 파라미터로 그룹화
  - **READ/WRITE 분리**: 조회(get_place_info)와 저장(manage_course) 분리 (SRP 원칙)
  - **실제 API 호출**: 카카오 로컬 API (키워드 검색, 카테고리 검색, 좌표→주소, 좌표→행정구역)
  - **컨텍스트 최적화**: 도구 수 최소화로 LLM 선택 부담 감소
- **Tool 구조**:
  - `get_place_info` (READ): keyword_search, category_search, coord_to_address, coord_to_region
  - `manage_course` (WRITE): add, remove, list, clear (JSON 파일 저장)
- **API**: 카카오 로컬 API (KAKAO_REST_API_KEY 필요)

#### Chapter 8-1: RAG Pipeline POC
- **주제**: MongoDB Atlas Vector Search + OpenAI SDK를 활용한 RAG Pipeline 구현
- **파일**:
  - [ingest.py](chapter_8-1/ingest.py) - 수집 엔드포인트 (Markdown → 청크 → 임베딩 → MongoDB)
  - [query.py](chapter_8-1/query.py) - 질의 엔드포인트 (Vector Search → LLM 답변, 단일 실행)
- **학습 목표**:
  - **RAG 파이프라인 이해**: 문서 수집 → 임베딩 → 검색 → 답변 생성 전체 흐름
  - **Langchain 부분 활용**: 텍스트 분할에만 Langchain 사용 (MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter)
  - **OpenAI SDK 직접 사용**: 임베딩/Chat Completion은 Raw SDK로 구현하여 동작 원리 이해
  - **MongoDB Atlas Vector Search**: $vectorSearch 파이프라인 직접 구현
- **데이터**: assets/sample.md (Markdown 문서)
- **MongoDB 설정**: DB=hackers, Collection=rag_demo, Index=vector_index

#### Chapter 9-1: Study Buddy Agent (MCP 연동)
- **주제**: GitHub Public 레포를 함께 읽고 구조를 설명해주는 Study Buddy Agent
- **파일**:
  - [main.py](chapter_9-1/main.py) - MCP 연동 + CLI 대화형 루프
- **학습 목표**:
  - **Hosted MCP 개념 이해**: Remote MCP Server vs Local MCP Server 차이
  - **GitMCP.io 활용**: GitHub 레포를 MCP 서버로 즉시 변환 (`https://gitmcp.io/{owner}/{repo}`)
  - **OpenAI Responses API + MCP 연동**: `tools` 파라미터에 MCP 도구 정의
  - **컨텍스트 유지 대화**: conversation 리스트를 통한 대화 히스토리 관리
- **기술 스택**:
  - OpenAI SDK (`client.responses.create()`)
  - GitMCP.io (Hosted Remote MCP Server)
- **설정**: `GITHUB_REPO_URL` 변수에 분석할 레포 URL 입력

#### Chapter 9-2: Calendar Agent (Local MCP Server)
- **주제**: 직접 MCP 서버를 만들어 서빙하고 LLM과 연동하는 일정 관리 에이전트
- **파일**:
  - [server.py](chapter_9-2/server.py) - FastMCP 서버 (SSE 트랜스포트, port 8000)
  - [main.py](chapter_9-2/main.py) - MCP Client + OpenAI Function Calling + CLI 루프
- **학습 목표**:
  - **Local MCP Server 구현**: FastMCP로 직접 MCP 서버 구현 및 실행
  - **SSE 트랜스포트**: HTTP 기반 Server-Sent Events로 클라이언트-서버 연동
  - **2개 프로세스 연동 체험**: 터미널 2개에서 독립적으로 서버/클라이언트 실행
  - **MCP Tool → OpenAI Function Calling 변환**: 스키마 변환 패턴 이해
  - **Tool Loop 패턴**: tool_calls → MCP 호출 → 결과 전달 → 최종 응답
- **MCP Tools (6개)**:
  - `get_current_datetime`: 현재 날짜/시간 조회 (Mock)
  - `list_events`: 일정 목록 조회
  - `get_event`: 일정 상세 조회
  - `add_event`: 새 일정 추가
  - `update_event`: 일정 수정
  - `delete_event`: 일정 삭제
- **Mock 데이터**: 4개 초기 일정 (팀 회의, 점심 약속, 프로젝트 마감, 치과 예약)

#### Chapter 10: Multi-Agent Collaboration - AI Development Team
- **주제**: Supervisor 패턴 기반 멀티 에이전트 협업 시스템 - 범용 웹앱 자동 설계/개발/테스트
- **파일**:
  - [main.py](chapter_10/main.py) - Supervisor Tool Loop 오케스트레이션
  - [tools.py](chapter_10/tools.py) - 5개 Tool 정의 + execute_tool() 라우팅
  - [agent_pm.py](chapter_10/agent_pm.py) - PM Agent (요구사항 추출, web_search)
  - [agent_designer.py](chapter_10/agent_designer.py) - Designer Agent (UI/UX 기획, web_search)
  - [agent_architect.py](chapter_10/agent_architect.py) - Architect Agent (코드 생성)
  - [agent_tester.py](chapter_10/agent_tester.py) - Tester Agent (LLM 기반 동적 E2E 테스트)
- **학습 목표**:
  - **Supervisor 패턴**: 중앙 집중식 에이전트 조율 방식 이해
  - **자율 문제 해결 루프**: Supervisor가 자율적으로 재시도 여부 판단
  - **Function Calling 확장**: 서브 에이전트를 Tool로 표현하는 패턴
  - **Web Search 통합**: Responses API + `tools=[{"type": "web_search"}]` 활용
  - **동적 E2E 테스트**: LLM이 요구사항 기반으로 테스트 계획 생성 → Playwright 실행
  - **산출물 관리**: 멀티 에이전트 협업의 결과물 체계적 저장
- **에이전트 구성**:
  - PM (Supervisor): 요구사항 추출 (web_search), 워크플로우 조율, README 작성
  - Designer: 모던 UI/UX 디자인 기획서 작성 (web_search로 트렌드 탐색)
  - Architect: 바닐라 JS/HTML/CSS 코드 생성 + 버그 수정
  - Tester: LLM이 요구사항 분석 → 동적 테스트 계획 생성 → Playwright 실행
- **워크플로우**:
  ```
  User → PM(요구사항) → Designer(기획) → Architect(코드)
                            ↑              ↑
                            └──────────────┴── Supervisor 자율 재호출
                                               ↓
                                    Tester(동적 E2E) → 실패 시 request_fix
                                               ↓
                                    PM(README) → User
  ```
- **핵심 설계 결정**:
  - **범용성**: 어떤 요구사항이든 처리 가능 (TODO 앱, 계산기, 갤러리 등)
  - **동적 테스트**: 하드코딩된 테스트 대신 LLM이 요구사항 기반 테스트 생성
  - **2000자 제한**: PM/Designer 출력물은 2000자 이내로 간결하게
  - **Supervisor 자율성**: 강제 재시도 로직 없이 Supervisor가 판단
- **의존성**: `pip install playwright && playwright install chromium`

#### Chapter 11: Agentic Debate System (에이전틱 토론 시스템)
- **주제**: A2A 프로토콜 영감의 멀티 에이전트 토론 시스템 - 확장 가능한 클래스 기반 아키텍처
- **파일**:
  - [main.py](chapter_11/main.py) - CLI Entry Point + 데모 시나리오
  - [protocol.py](chapter_11/protocol.py) - A2A 영감: Message, Part, AgentCard, AgentRole 정의
  - [base_agent.py](chapter_11/base_agent.py) - BaseAgent ABC (추상 기반 클래스)
  - [context_manager.py](chapter_11/context_manager.py) - ContextManager (.md 파일 I/O + 요약)
  - [orchestrator.py](chapter_11/orchestrator.py) - DebateOrchestrator (State Machine)
  - [agent_judge.py](chapter_11/agent_judge.py) - JudgeAgent (토론 조율, 평가, 최종 판정)
  - [agent_debater.py](chapter_11/agent_debater.py) - DebaterAgent (주장 전개, web_search)
  - [factory.py](chapter_11/factory.py) - 에이전트/오케스트레이터 팩토리 함수
- **학습 목표**:
  - **클래스 기반 아키텍처**: 확장 가능한 에이전트 구조 설계
  - **A2A 프로토콜 영감**: Message, Part, AgentCard 등 표준화된 통신 구조
  - **State Machine 기반 오케스트레이션**: 명확한 상태 전이로 토론 흐름 제어
  - **파일 기반 메모리**: .md 파일로 실시간 개발자 가시성 제공
  - **자유 형식 토론**: 발언 신청 → 판사 선택 → 종료 결정 패턴
  - **자동 요약**: 10,000자 초과 시 이전 발언 LLM 요약
- **에이전트 구성**:
  - Judge (판사/Supervisor): 토론 조율, 발언자 선택, 평가, 최종 판정
  - Debater PRO: 찬성 입장 옹호 (web_search로 근거 수집)
  - Debater CON: 반대 입장 옹호 (web_search로 근거 수집)
- **워크플로우**:
  ```
  INITIALIZATION → OPENING_STATEMENTS → FREE_DEBATE ⇄ JUDGE_EVALUATION
                                                    ↓
                        ENDED ← JUDGMENT ← CLOSING_STATEMENTS
  ```
- **A2A에서 가져온 핵심 개념**:
  - **AgentCard**: 에이전트 자기소개 (name, description)
  - **Message**: 에이전트 간 통신 단위 (role, parts, messageId)
  - **Part**: 메시지 내용 유형 (TextPart, DataPart)
  - **AgentRole**: 에이전트 역할 구분 (JUDGE, DEBATER_PRO, DEBATER_CON)
- **핵심 설계 결정**:
  - **발언 순서**: 자유 신청 → 판사 선택 (균형 고려)
  - **Tool 범위**: Debater만 web_search (판사는 토론 내용으로만 판단)
  - **max_rounds**: 무제한 (판사가 충분하다고 판단할 때까지)
  - **메모리**: .md 파일로 실시간 저장 (개발자 가시성)
- **데모 주제**: "완전 원격 근무가 사무실 근무보다 생산적인가?"

#### Chapter 12: Production Backend Engineering for AI Agents
- **주제**: AI Agent 시스템을 위한 프로덕션급 백엔드 인프라 구축
- **파일**:
  - [app.py](chapter_12/app.py) - FastAPI 서버 (동기/비동기 감정 분석 API)
  - [worker.py](chapter_12/worker.py) - SQS Consumer (작업 처리 워커)
  - [config.py](chapter_12/config.py) - 환경 설정 (pydantic-settings)
  - [models.py](chapter_12/models.py) - Pydantic 모델 + MongoDB 스키마
  - [database.py](chapter_12/database.py) - MongoDB CRUD (pymongo 동기 클라이언트)
  - [queue_client.py](chapter_12/queue_client.py) - AWS SQS 클라이언트 (boto3)
  - [llm_client.py](chapter_12/llm_client.py) - OpenAI 클라이언트 (Rate Limit, Retry)
  - Dockerfile, Dockerfile.worker, docker-compose.yml - Docker 컨테이너화
- **학습 목표**:
  - **FastAPI API 서버**: 동기/비동기 엔드포인트 패턴 비교
  - **AWS SQS 기반 작업 큐**: 실제 AWS 서비스와 연동한 메시지 큐 구현
  - **MongoDB 작업 상태 관리**: Job 상태 추적 (PENDING → PROCESSING → COMPLETED/FAILED)
  - **Docker 컨테이너화**: 멀티 서비스 오케스트레이션 (API + Worker + MongoDB)
  - **프로덕션 패턴**: Rate Limiting, Exponential Backoff, Graceful Shutdown
- **아키텍처**:
  ```
  Client → FastAPI (app.py) → AWS SQS → Worker (worker.py) → MongoDB
                ↓                              ↓
          동기 API (즉시 응답)           비동기 처리 (Job 생성 → 폴링)
  ```
- **API 엔드포인트**:
  - `GET /health`: 헬스체크
  - `POST /api/v1/sentiment/sync`: 동기 감정 분석 (즉시 응답)
  - `POST /api/v1/sentiment/async`: 비동기 감정 분석 (Job ID 반환)
  - `GET /api/v1/jobs/{job_id}`: 작업 상태 조회 (폴링용)
- **핵심 설계 결정**:
  - **LLM Task**: 감정 분석 (Sentiment Analysis) - 단일 LLM 호출
  - **Rate Limit 처리**: Exponential Backoff (1s → 2s → 4s), 최대 3회 재시도
  - **SQS 설정**: Visibility Timeout, Long Polling은 큐 기본 설정 사용
  - **Graceful Shutdown**: SIGINT/SIGTERM 처리로 안전한 종료
  - **간결한 코드**: pymongo만 사용 (motor 비동기 제거), datetime 필드 제거
- **의존성**: `pip install fastapi uvicorn pymongo boto3 openai pydantic-settings`

## 개발 명령어

### 챕터별 실습 실행
```bash
# Chapter 0: Fact-Check Agent (무료 맛보기)
python chapter_0/main.py               # Plan → Analysis (web_search 활용)

# Chapter 1: 프롬프트 기반 파이프라인
python chapter_1/main.py

# Chapter 2: 실습 #1 (회의 메모 분석)
python chapter_2/exercise1_before.py   # Before: 간단한 프롬프트
python chapter_2/exercise1_after.py    # After: 구조화 + 검증

# Chapter 2: 실습 #2 (ROAS 계산)
python chapter_2/exercise2_before.py   # Before: 단순 프롬프트
python chapter_2/exercise2_after.py    # After: CoT + Self-Consistency

# Chapter 3: Prompt Chaining
python chapter_3/main.py               # 3단계 체인 실행 (PDF → 요약 → 트렌드 → 이메일)

# Chapter 3-2: Intent Routing - 다중 Router 방식 비교
python chapter_3-2/main.py             # 3가지 Router 비교 (LLM/Rule/Semantic + 성능 측정)

# Chapter 4: Planning 패턴
python chapter_4/main.py               # Planning 패턴 실행 (Plan → 실행)

# Chapter 4-2: Deep Research
python chapter_4-2/main.py             # Deep Research 실행 (Clarification → Rewriting → Research)

# Chapter 4-3: 요약 기반 메모리 관리
python chapter_4-3/main.py             # 메모리 관리 실습 (요약 기반 컨텍스트 압축)

# Chapter 5-1: Reflection Pattern
python chapter_5-1/single_pass.py      # 단일 루프 (1회 Reflection)
python chapter_5-1/iterative.py        # 반복 루프 (최대 3회)

# Chapter 5-2: Learning & Adaptation Pattern
python chapter_5-2/main.py             # ACE 단순화 버전 (멀티 태스크 학습)

# Chapter 7-1: Tool 컨셉 - 여행 준비 도우미
python chapter_7-1/main.py             # Tool Loop (날씨/환율 조회 에이전트)

# Chapter 7-2: Tool 통합 - 회식 코스 플래너
python chapter_7-2/main.py             # Tool 통합 (카카오 API + JSON 저장)

# Chapter 8-1: RAG Pipeline POC
python chapter_8-1/ingest.py           # 수집: Markdown → 청크 → 임베딩 → MongoDB
python chapter_8-1/query.py            # 질의: Vector Search → LLM 답변 (단일 실행)

# Chapter 9-1: Study Buddy Agent (MCP 연동)
python chapter_9-1/main.py             # MCP 연동 대화형 루프 (GITHUB_REPO_URL 변수 수정)

# Chapter 9-2: Calendar Agent (Local MCP Server) - 2개 터미널 필요
# 터미널 1: MCP 서버 실행
python chapter_9-2/server.py           # FastMCP 서버 (http://localhost:8000/sse)
# 터미널 2: Agent 실행
python chapter_9-2/main.py             # MCP Client + Function Calling + CLI 루프

# Chapter 10: Multi-Agent Collaboration - AI Development Team
# 의존성 설치 (최초 1회)
pip install playwright && playwright install chromium
# 실행
python chapter_10/main.py              # Supervisor 패턴 멀티 에이전트 (범용 웹앱 자동 생성)
# 결과물 확인
open chapter_10/output/app.html        # 생성된 웹앱 실행

# Chapter 11: Agentic Debate System (에이전틱 토론 시스템)
# 기본 데모 (원격 근무 주제)
python chapter_11/main.py
# 사용자 정의 주제
python chapter_11/main.py "AI가 인간의 일자리를 대체할 것인가?"
# 결과물 확인
cat chapter_11/memory/debate_history.md    # 전체 토론 기록
cat chapter_11/output/debate_summary.md    # 최종 판정 요약

# Chapter 12: Production Backend Engineering for AI Agents
# Docker Compose로 전체 스택 실행
cd chapter_12
docker-compose up -d --build

# API 테스트 (동기 감정 분석)
curl -X POST http://localhost:8000/api/v1/sentiment/sync \
  -H "Content-Type: application/json" \
  -d '{"text": "이 제품 정말 최고예요!"}'

# API 테스트 (비동기 감정 분석)
curl -X POST http://localhost:8000/api/v1/sentiment/async \
  -H "Content-Type: application/json" \
  -d '{"text": "서비스가 너무 느리고 불친절해서 실망했습니다."}'

# 작업 상태 조회
curl http://localhost:8000/api/v1/jobs/{job_id}

# 로컬 개발 모드 (터미널 2개 필요)
# 터미널 1: MongoDB 실행
docker run -d --name mongodb -p 27017:27017 mongo:latest
# 터미널 2: API 서버 실행
python chapter_12/app.py
# 터미널 3: Worker 실행
python chapter_12/worker.py

# 정리
docker-compose down -v
```

### 환경 변수 설정
```bash
# .env 파일 생성 (프로젝트 루트)
OPENAI_API_KEY=your_openai_api_key_here
KAKAO_REST_API_KEY=your_kakao_api_key_here  # Chapter 7-2 회식 코스 플래너용
MONGODB_URI=mongodb+srv://...  # Chapter 8-1 RAG Pipeline용

# Chapter 12: Production Backend Engineering
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-northeast-2
SQS_QUEUE_NAME=sentiment-analysis-queue
```

### 코드 품질 (선택사항)
```bash
# Ruff로 린트 및 포맷팅
ruff check chapter_1/ chapter_2/
ruff format chapter_1/ chapter_2/

# 타입 체크
mypy chapter_1/main.py chapter_2/
```

### 실험 및 프로토타입
```bash
# 실험 스크립트는 항상 scripts/ 폴더에서 생성하고 실행
python scripts/experiment_name.py
```

## 아키텍처 설계 가이드

### 에이전트 설계 원칙

1. **컨텍스트 우선 접근**
   - 하드코딩된 프롬프트보다 동적 컨텍스트 구성을 선호
   - 에이전트는 컨텍스트를 통해 행동을 조정해야 함
   - 컨텍스트는 명시적이고 검증 가능해야 함

2. **자기개선 메커니즘**
   - 에이전트는 자신의 성능을 평가하고 개선할 수 있어야 함
   - 프롬프트와 컨텍스트 자동 리팩토링 기능 포함
   - 실행 결과 기반 학습 루프 구현

3. **모듈형 워크플로우**
   - 각 에이전트는 단일 책임 원칙을 따름
   - 에이전트 간 통신은 명시적 인터페이스를 통해서만
   - 워크플로우는 조합 가능하고 재사용 가능해야 함

### LLM 통합 패턴

- **프로바이더 독립성**: OpenAI, Anthropic, 로컬 모델 등 쉽게 교체 가능
- **비용 최적화**: 작업별로 적절한 모델 크기 선택
- **에러 처리**: LLM 호출 실패 시 우아한 폴백 메커니즘
- **컨텍스트 윈도우 관리**: 자동 컨텍스트 압축 및 우선순위 설정

### 워크플로우 오케스트레이션

- **병렬 실행**: 독립적인 에이전트는 동시 실행
- **상태 관리**: 워크플로우 상태는 영속적이고 복구 가능
- **모니터링**: 각 단계의 성능 및 비용 추적
- **실패 복구**: 부분 실패 시 전체 워크플로우 재시작 없이 복구

## 코딩 규칙

### Import 문 정리
- **모든 `from` / `import` 구문은 파일 최상단에 선언**
- 표준 라이브러리 → 서드파티 → 로컬 순서로 그룹화
- `isort` 또는 `ruff`를 사용하여 자동 정렬

### 타입 힌팅
- 모든 함수 시그니처에 타입 힌트 필수
- 복잡한 데이터 구조는 `TypedDict` 또는 `dataclass` 사용
- `mypy` strict 모드 통과 목표

### 비동기 처리
- LLM 호출은 `async/await` 패턴 사용
- 멀티 에이전트 워크플로우는 `asyncio.gather()` 활용
- 모든 Job의 `run` 함수는 return 값이 없어야 함 (부작용만 수행)

### 테스트 (선택사항)
- 교육용 프로젝트이므로 테스트는 선택적으로 작성
- LLM 호출은 모킹하여 테스트 (실제 API 호출 최소화)
- **모든 테스트는 타임아웃을 설정하지 않거나 최대한 길게 설정** (LLM 응답 대기 시간 고려)

## 실습 스크립트 관리

- **모든 임시 테스트를 위한 실행 코드는 `scripts/` 폴더에서 생성하고 실행**
- 스크립트 파일명은 목적을 명확히: `experiment_context_injection.py`, `demo_self_improving_agent.py`
- 실습 후 정리: 일회성 스크립트는 삭제하거나 `scripts/archive/`로 이동

## 챕터 독립성 원칙

각 챕터는 다음 원칙을 따릅니다:

1. **독립 실행 가능**: 각 챕터는 독립적으로 실행 가능하며, 다른 챕터에 의존하지 않음
2. **자체 완결성**: 필요한 모든 코드와 설명이 해당 챕터 내에 포함
3. **순차 학습 권장**: 챕터 순서대로 학습하는 것을 권장하지만, 필수는 아님
4. **공통 패턴 중복 허용**: 학습 목적상 코드 중복을 허용하며, 각 챕터에서 개념을 재구현

## 실습 코드 특징

### 간결성 우선
- 모든 환경변수 하드코딩 (OPENAI_API_KEY 제외)
- temperature, timeout 등 옵션 제거
- try-except 최소화 (핵심 로직에 집중)
- 장문 문자열은 `"""` 사용

### CLI 출력 중심
- 모든 단계마다 진행 상황 출력
- 중간 결과(JSON) 전문 표시
- 이모지로 단계 구분 (📝, 🔍, ✅, 💡 등)

### Before/After 비교 학습
- Chapter 2의 모든 실습은 Before/After 쌍으로 구성
- 직접 실행하며 차이점 체험
- 출력 결과 비교를 통한 개선 효과 확인

## 참고 사항

- 이 프로젝트는 **교육용**이므로, 명확성과 이해도가 성능보다 우선
- 복잡한 추상화보다 **명시적이고 간단한 구현**을 선호
- 각 개념은 **독립적인 예제**로 실습 가능해야 함
- 프로덕션 배포는 고려하되, **학습 목적이 최우선**
- **챕터 간 코드 공유보다 각 챕터의 독립성을 우선**

## 문서 동기화 규칙

이 CLAUDE.md 파일은 프로젝트의 **단일 진실 공급원(Single Source of Truth)**입니다.
코드 변경 시 반드시 이 문서를 함께 업데이트해야 합니다.

### 동기화가 필요한 경우

#### 1. 새 챕터 추가 시
- [ ] **프로젝트 구조** 섹션: 디렉토리 트리에 새 챕터 폴더 추가
- [ ] **챕터 구성** 섹션: 새 챕터 설명 추가 (주제, 파일, 학습 목표)
- [ ] **개발 명령어** 섹션: 실행 명령어 추가

#### 2. 파일 추가/삭제 시
- [ ] **프로젝트 구조** 섹션: 파일 트리 업데이트
- [ ] **챕터 구성** 섹션: 파일 링크 및 설명 업데이트

#### 3. 실행 방식 변경 시
- [ ] **개발 명령어** 섹션: 명령어 업데이트
- [ ] **환경 설정** 섹션: 의존성 변경 시 반영

#### 4. 아키텍처 패턴 변경 시
- [ ] **아키텍처 설계 가이드** 섹션: 새로운 패턴 문서화
- [ ] **코딩 규칙** 섹션: 규칙 변경 사항 반영

### 동기화 체크리스트 예시

**새 챕터 추가 시**:
```bash
# 1. 코드 구현
# 2. CLAUDE.md 업데이트 (위 4개 섹션)
# 3. git commit -m "Add Chapter X: [주제]" (코드 + CLAUDE.md 함께 커밋)
```

**중요**: CLAUDE.md 업데이트 없이 코드만 커밋하지 마세요.
문서와 코드는 항상 동기화 상태를 유지해야 합니다.

## 추가 리소스

강의 과정에서 사용될 주요 개념:
- Context-driven design
- Self-improving agents
- Multi-agent workflows
- Prompt engineering vs. Context engineering
- Agentic system patterns
