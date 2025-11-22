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
│   ├── main.py                  # Intent Routing 오케스트레이션
│   ├── router.py               # Intent Classifier (사용자 입력 분류)
│   ├── module_faq.py           # FAQ 모듈 (제품 관련 질문 답변)
│   ├── module_order.py         # Order 모듈 (주문 조회, Mock DB)
│   └── module_human.py         # Human 모듈 (상담사 연결, Mock 티켓)
├── chapter_4/
│   ├── main.py                  # Planning 패턴 오케스트레이션
│   ├── agent_planner.py        # Planner 에이전트 (요약 계획 생성)
│   └── agent_writer.py         # Writer 에이전트 (계획 기반 요약 작성)
└── scripts/                     # 유틸리티 및 실험 스크립트
```

### 공유 리소스 (assets/)

**assets/** 디렉토리는 여러 챕터에서 공통으로 사용하는 리소스를 관리합니다:
- **sample.pdf**: Chapter 3 및 기타 챕터에서 사용하는 PDF 샘플 파일
- 다른 챕터에서 접근 시: `Path(__file__).parent.parent / "assets" / "파일명"`

### 챕터 구성

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

#### Chapter 3-2: Intent Routing
- **주제**: 사용자 입력 분류 및 조건부 라우팅 (Intent → FAQ/Order/Human)
- **파일**:
  - [main.py](chapter_3-2/main.py) - Intent Routing 오케스트레이션
  - [router.py](chapter_3-2/router.py) - Intent Classifier (사용자 입력 분류)
  - [module_faq.py](chapter_3-2/module_faq.py) - FAQ 모듈 (제품 질문 답변)
  - [module_order.py](chapter_3-2/module_order.py) - Order 모듈 (주문 조회, Mock DB)
  - [module_human.py](chapter_3-2/module_human.py) - Human 모듈 (상담사 연결, Mock 티켓)
- **학습 목표**:
  - Intent Routing 패턴 이해
  - 조건부 분기 구현 (`in` 연산자로 안전한 체크)
  - Mock 함수로 외부 시스템 시뮬레이션
  - 모듈별 역할 분리 설계
  - 3개 시나리오 테스트 (FAQ, Order, Human)

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

## 개발 명령어

### 챕터별 실습 실행
```bash
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

# Chapter 3-2: Intent Routing
python chapter_3-2/main.py             # Intent Routing 실행 (3개 시나리오 테스트)

# Chapter 4: Planning 패턴
python chapter_4/main.py               # Planning 패턴 실행 (Plan → 실행)
```

### 환경 변수 설정
```bash
# .env 파일 생성 (프로젝트 루트)
OPENAI_API_KEY=your_openai_api_key_here
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
