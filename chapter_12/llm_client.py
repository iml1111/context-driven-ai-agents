"""
Chapter 12: Production Backend Engineering - LLM Client

OpenAI 클라이언트 래퍼
- Exponential Backoff 재시도 로직
- Rate Limit 자동 처리
- 감정 분석 전용 프롬프트
"""

import json
import time
from typing import Optional

from openai import APIError, OpenAI, RateLimitError

# 시스템 프롬프트: 감정 분석 전문가
SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analysis expert.
Analyze the given text and classify it as one of: positive, negative, neutral.

Respond ONLY with a JSON object in this exact format:
{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}

Guidelines:
- "positive": Text expresses satisfaction, happiness, approval, or optimism
- "negative": Text expresses dissatisfaction, anger, disappointment, or pessimism
- "neutral": Text is factual, balanced, or lacks clear emotional content
- "confidence": Your certainty level (0.0 = uncertain, 1.0 = very confident)

Be precise and consistent. Do not include any explanation, only the JSON."""


class LLMClient:
    """
    OpenAI 클라이언트 래퍼

    Exponential Backoff 재시도 로직이 포함된 LLM 호출 클라이언트
    Rate Limit 및 일시적 API 오류를 자동으로 처리
    """

    def __init__(
        self,
        api_key: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        model: str = "gpt-5.1",
    ):
        """
        Args:
            api_key: OpenAI API 키
            max_retries: 최대 재시도 횟수
            base_delay: 기본 대기 시간 (초)
            model: 사용할 모델
        """
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.model = model

    def analyze_sentiment(self, text: str) -> dict:
        """
        텍스트 감정 분석

        Exponential Backoff 재시도 로직이 적용됨:
        - 1차 시도 실패: 1초 대기
        - 2차 시도 실패: 2초 대기
        - 3차 시도 실패: 4초 대기 후 예외 발생

        Args:
            text: 분석할 텍스트 (최대 2000자로 자동 절삭)

        Returns:
            {"sentiment": str, "confidence": float}

        Raises:
            Exception: 최대 재시도 횟수 초과 시
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                # 텍스트 길이 제한 (토큰 절약)
                truncated_text = text[:2000]

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SENTIMENT_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Analyze: {truncated_text}"},
                    ],
                    response_format={"type": "json_object"},
                )

                # JSON 파싱
                content = response.choices[0].message.content
                result = json.loads(content)

                # 결과 검증 및 정규화
                sentiment = result.get("sentiment", "neutral").lower()
                if sentiment not in ("positive", "negative", "neutral"):
                    sentiment = "neutral"

                confidence = float(result.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))  # 0.0 ~ 1.0 범위 제한

                return {"sentiment": sentiment, "confidence": confidence}

            except RateLimitError as e:
                last_error = e
                delay = self.base_delay * (2**attempt)  # 1s, 2s, 4s
                print(
                    f"   ⚠️ Rate limit hit. Retrying in {delay}s... "
                    f"(attempt {attempt + 1}/{self.max_retries})"
                )
                time.sleep(delay)

            except APIError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    print(f"   ⚠️ API error: {e}. Retrying in {delay}s...")
                    time.sleep(delay)

            except json.JSONDecodeError as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    print(f"   ⚠️ JSON parse error. Retrying in {delay}s...")
                    time.sleep(delay)

        # 모든 재시도 실패
        raise Exception(f"Max retries ({self.max_retries}) exceeded. Last error: {last_error}")
