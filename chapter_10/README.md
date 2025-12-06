# Chapter 10: Multi-Agent Collaboration - AI Development Team

Supervisor 패턴 기반의 멀티 에이전트 협업 시스템으로, TODO List 웹앱을 자동 설계/개발/테스트합니다.

## 실습 목표

- **Supervisor 패턴**: 중앙 집중식 에이전트 조율 방식 이해
- **자율 문제 해결 루프**: 선형 워크플로우가 아닌 피드백 기반 재시도 구조
- **Function Calling 확장**: 서브 에이전트를 Tool로 표현하는 패턴
- **Web Search 통합**: OpenAI Responses API의 web_search 활용
- **E2E 테스트**: Playwright로 생성된 웹앱 자동 검증

## 환경 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Playwright 브라우저 설치 (필수)

```bash
playwright install chromium
```

> Playwright는 Python 패키지와 별개로 브라우저 바이너리가 필요합니다.

### 3. 환경변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정합니다:

```bash
# chapter_10/.env
OPENAI_API_KEY=your_openai_api_key_here
```

## 실행 방법

```bash
python main.py
```

## 에이전트 구성

| 에이전트 | 역할 | 특수 기능 |
|---------|------|----------|
| **PM (Supervisor)** | 요구사항 추출, 워크플로우 조율, README 작성 | 자율 루프 제어 |
| **Designer** | UI/UX 디자인 기획서 작성 | web_search |
| **Architect** | HTML/CSS/JS 코드 생성 | web_search |
| **Tester** | E2E 테스트 수행 | Playwright |
