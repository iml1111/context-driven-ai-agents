"""
Chapter 11: Agentic Debate System (에이전틱 토론 시스템)

멀티 에이전트 토론 시스템.
판사(Supervisor)와 두 토론자(PRO/CON)가 자유 형식으로 토론을 진행.

실행:
    python chapter_11/main.py

데모 주제: "완전 원격 근무가 사무실 근무보다 생산적인가?"
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from factory import DebateFactory
from protocol import DebateConfig

# 환경 변수 로드
load_dotenv()


def main() -> None:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 경로 설정
    base_dir = Path(__file__).parent
    memory_dir = base_dir / "memory"
    output_dir = base_dir / "output"

    # 데모 토론 주제
    topic = "완전 원격 근무가 사무실 근무보다 생산적인가?"

    print(f"📋 토론 주제: {topic}\n")
    print(f"📁 메모리 디렉토리: {memory_dir}")
    print(f"📁 출력 디렉토리: {output_dir}\n")

    # 토론 설정
    config = DebateConfig(
        topic=topic,
        summary_threshold=10000,  # 10,000자 초과 시 요약
        max_speaking_turns=20,    # 안전장치: 최대 20회 발언
    )

    # Factory로 의존성 조립
    factory = DebateFactory(
        client=client,
        config=config,
        memory_dir=memory_dir,
        output_dir=output_dir,
    )

    # 오케스트레이터 생성 (모든 의존성 주입)
    orchestrator = factory.create_orchestrator()

    orchestrator.run()

if __name__ == "__main__":
    main()
