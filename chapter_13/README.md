# Chapter 13: Agent Workflow Evaluation Pipeline

Production Ready Agent를 위한 평가 파이프라인 구축 - A/B 비교 평가

## 개요

chapter_0의 Fact-Check Agent를 두 가지 버전으로 구현하고, 동일한 데이터셋으로 평가하여 성능을 비교합니다.

### 학습 목표

1. **에이전트 시스템의 비결정적 특성 이해**: 동일 입력에 다른 출력 가능
2. **다층 평가 설계**: 중간 산출물(체크리스트) + 최종 출력(verdict) 동시 평가
3. **LLM-as-Judge 패턴**: gpt-5.1로 체크리스트 품질/근거 충분성 평가
4. **Confidence Calibration**: ECE(Expected Calibration Error)로 신뢰도 검증
5. **A/B 비교**: Before/After 성능 비교로 개선 효과 정량화

## 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    Evaluation Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐                                                │
│  │  Dataset     │  eval_data.jsonl (12 cases)                   │
│  │  (JSONL)     │  - claim: "검증할 정보"                        │
│  └──────┬───────┘  - ground_truth: TRUE/FALSE/PARTIALLY_TRUE/UNVERIFIABLE
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                                │
│  │ Fact-Checker │  Ver 1 (gpt-4o) vs Ver 2 (gpt-5.1)            │
│  │   Agent      │  - Plan: checklist 생성                       │
│  └──────┬───────┘  - Analysis: verdict + confidence + evidence  │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              Multi-Level Evaluation                   │       │
│  ├──────────────────────────────────────────────────────┤       │
│  │  [L1] Accuracy: verdict == ground_truth (Exact)      │       │
│  │  [L2] Checklist Quality: LLM-as-Judge (1-5점)        │       │
│  │  [L3] Evidence Quality: LLM-as-Judge (1-5점)         │       │
│  │  [L4] Confidence Calibration: ECE 분석               │       │
│  └──────────────────────────────────────────────────────┘       │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐                                                │
│  │   Report     │  - A/B 비교 리포트                             │
│  │  Generator   │  - 케이스별 상세 결과                          │
│  └──────────────┘  - 개선 효과 정량화                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 파일 구조

```
chapter_13/
├── main.py                 # A/B 비교 평가 오케스트레이션
├── dataset.py              # EvalCase 데이터 모델 + 로더
├── eval_data.jsonl         # 평가 데이터셋 (12개 케이스)
├── report.py               # 평가 리포트 생성
├── fact_checkers/
│   ├── __init__.py         # 팩트체커 export
│   ├── v1.py               # Ver 1: Baseline (gpt-4o, 원본 프롬프트)
│   └── v2.py               # Ver 2: Improved (gpt-5.1, Structured Output)
├── evaluators/
│   ├── __init__.py         # 평가기 export
│   ├── accuracy.py         # L1: Exact Match 평가
│   ├── llm_judge.py        # L2, L3: LLM-as-Judge 평가
│   └── calibration.py      # L4: Confidence Calibration
└── README.md               # 이 파일
```

## A/B 비교 설계

| 구분 | Ver 1 (Baseline) | Ver 2 (Improved) |
|------|------------------|------------------|
| **모델** | gpt-4o | gpt-5.1 |
| **프롬프트** | chapter_0 원본 | 개선된 프롬프트 |
| **출력** | 텍스트 파싱 | Structured Output |

### Ver 2 개선 사항

1. **Structured Output**: `response_format` 파라미터로 JSON 스키마 강제
2. **명시적 CoT**: 체크리스트 항목별 검증 근거 명시
3. **Confidence 가이드라인**: 신뢰도 판단 기준 명시 (0.0~1.0)
4. **UNVERIFIABLE 인식**: 검증 불가 케이스 처리 로직 강화

### V1 vs V2 구현 상세 비교

#### 프롬프트 비교

**Plan 프롬프트:**

| 항목 | V1 | V2 |
|------|----|----|
| 출력 형식 | 불릿 리스트 (`- 포인트`) | Structured Output (JSON Schema) |
| 출처 유형 | 없음 | `official`/`academic`/`news`/`database` 분류 |
| 검증가능성 | 간단한 언급 | 구체적 기준 제시 |

**Analysis 프롬프트:**

| 항목 | V1 | V2 |
|------|----|----|
| 검증 프로세스 | 암묵적 | 명시적 CoT (검색 → 기록 → 판단) |
| Confidence 기준 | 없음 | 5단계 가이드라인 (0.9-1.0, 0.7-0.9, ...) |
| UNVERIFIABLE | 간단한 옵션 | 3가지 판단 기준 명시 |

#### 데이터 모델 비교

**V1 (ChecklistItem):**
```python
class ChecklistItem(BaseModel):
    point: str      # 검증 포인트
    result: str     # 확인 결과
```

**V2 (ChecklistItemV2):**
```python
class ChecklistItemV2(BaseModel):
    point: str        # 검증 포인트
    source_type: str  # 출처 유형 (official/academic/news/database)
    result: str       # 확인 결과
    source_found: str # 실제 찾은 출처
```

| 필드 | V1 | V2 | 설명 |
|------|:--:|:--:|------|
| `source_type` | ❌ | ✅ | 필요한 출처 유형 명시 |
| `source_found` | ❌ | ✅ | 실제 찾은 출처 기록 |
| `confidence_reasoning` | ❌ | ✅ | 신뢰도 판단 근거 |

#### 출력 파싱 방식

| 항목 | V1 | V2 |
|------|----|----|
| 방식 | Regex (`re.search`) | Structured Output |
| JSON 추출 | ```json``` 블록 또는 `{...}` 패턴 | API가 JSON 보장 |
| 파싱 실패 | UNVERIFIABLE 반환 | 발생하지 않음 |
| 의존성 | `json`, `re` 모듈 | Pydantic 스키마 |

#### 코드 복잡도

| 항목 | V1 | V2 |
|------|----|----|
| `_analyze()` 라인 수 | ~70줄 | ~50줄 |
| JSON 파싱 코드 | 20줄+ (regex + try-except) | 2줄 (Pydantic) |
| 에러 처리 | 명시적 fallback | 불필요 |

## 평가 계층

| 계층 | 평가 항목 | 방법 | 기준 |
|------|----------|------|------|
| **L1** | Accuracy | Exact Match | verdict == ground_truth |
| **L2** | Checklist Quality | LLM-as-Judge | 구체성, 포괄성, 검증가능성, 관련성 (1-5점) |
| **L3** | Evidence Quality | LLM-as-Judge | 충분성, 신뢰성, 논리성, 명확성 (1-5점) |
| **L4** | Calibration | ECE 분석 | confidence와 실제 정확도 일치도 |

### ECE (Expected Calibration Error)

- **0.00 ~ 0.05**: 매우 좋음 (Well-calibrated)
- **0.05 ~ 0.10**: 좋음
- **0.10 ~ 0.15**: 보통
- **0.15 이상**: 개선 필요 (Miscalibrated)

## 실행 방법

### 환경 변수 설정

```bash
# .env 파일 (프로젝트 루트)
OPENAI_API_KEY=your_openai_api_key_here
```

### A/B 비교 평가 실행

```bash
python main.py
```

두 버전(Ver 1, Ver 2)을 동일 데이터셋으로 평가하고 비교 리포트를 생성합니다.

## 출력 예시

### A/B 비교 리포트

```
============================================================
📊 A/B 성능 비교: Ver 1 vs Ver 2
============================================================

[Ver 1 - Baseline (gpt-4o)]
  정확도: 70.0% (7/10)
  체크리스트 품질: 3.8/5
  근거 충분성: 3.5/5
  Calibration ECE: 0.18

[Ver 2 - Improved (gpt-5.1)]
  정확도: 90.0% (9/10)
  체크리스트 품질: 4.5/5
  근거 충분성: 4.2/5
  Calibration ECE: 0.08

[개선 효과]
  정확도: +20.0%p (개선)
  체크리스트: +0.7점 (개선)
  근거: +0.7점 (개선)
  Calibration: -0.10 (개선)
```

## 데이터셋 (eval_data.jsonl)

12개 케이스로 구성:

| 분포 | 구성 |
|------|------|
| **난이도** | easy(3), medium(6), hard(3) |
| **정답** | TRUE(4), FALSE(5), PARTIALLY_TRUE(1), UNVERIFIABLE(2) |

### 케이스 예시

```jsonl
{"claim": "대한민국의 수도는 서울이다", "ground_truth": "TRUE", "difficulty": "easy", "category": "상식"}
{"claim": "만리장성은 우주에서 육안으로 보인다", "ground_truth": "FALSE", "difficulty": "medium", "category": "상식"}
{"claim": "비타민C는 감기를 예방한다", "ground_truth": "PARTIALLY_TRUE", "difficulty": "hard", "category": "건강"}
{"claim": "2030년에 한국의 인구는 5천만 명을 넘을 것이다", "ground_truth": "UNVERIFIABLE", "difficulty": "medium", "category": "사회"}
{"claim": "모차르트는 베토벤보다 더 위대한 작곡가였다", "ground_truth": "UNVERIFIABLE", "difficulty": "hard", "category": "예술"}
```

### UNVERIFIABLE 케이스 설계 의도

- **미래 예측**: 현재 시점에서 검증 불가 (예: "2030년에...")
- **주관적 비교**: 객관적 기준 없는 가치 판단 (예: "더 위대한...")

## 핵심 설계 결정

1. **커스텀 파이프라인 선택**: OpenAI Evals API 대신 커스텀 구현
   - 중간 산출물(체크리스트) 평가 필요
   - 교육적 가치 (평가 시스템 이해)

2. **LLM-as-Judge**: gpt-5.1 사용
   - 일관된 평가 기준 적용
   - 구조화된 점수 + 근거 출력

3. **실제 web_search 호출**: Mock 데이터 대신 실제 API
   - 실제 동작 평가
   - 비결정적 특성 체험

4. **12개 케이스**: 빠른 실습 + API 비용 최소화
   - 다양한 난이도와 카테고리 포함
   - 4가지 verdict 유형 모두 포함 (TRUE, FALSE, PARTIALLY_TRUE, UNVERIFIABLE)
   - 확장 가능한 JSONL 포맷

## 의존성

```bash
pip install openai pydantic python-dotenv
```

## 참고

- chapter_0의 Fact-Check Agent 기반
- OpenAI Responses API + web_search 도구 활용
- Pydantic을 활용한 Structured Output
