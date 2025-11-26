"""
Chapter 7-1: Tool 정의 및 Mock 구현

여행 준비 도우미 에이전트를 위한 Tool 정의:
1. get_weather: 도시별 날씨 조회
2. get_exchange_rate: 통화별 환율 조회

Mock 데이터로 실제 API 호출 없이 동작 시연
"""

import json

# ============================================================
# Mock 데이터 (서울, 도쿄, 상하이)
# ============================================================

WEATHER_DATA = {
    "seoul": {
        "city": "서울",
        "temp": 12,
        "condition": "맑음",
        "humidity": 45,
        "wind": "북서풍 3m/s",
    },
    "tokyo": {
        "city": "도쿄",
        "temp": 18,
        "condition": "흐림",
        "humidity": 60,
        "wind": "남풍 2m/s",
    },
    "shanghai": {
        "city": "상하이",
        "temp": 22,
        "condition": "비",
        "humidity": 80,
        "wind": "동풍 5m/s",
    },
}

EXCHANGE_RATE_DATA = {
    "KRW": {"name": "한국 원", "rate_to_usd": 1350.0, "symbol": "₩"},
    "JPY": {"name": "일본 엔", "rate_to_usd": 155.0, "symbol": "¥"},
    "CNY": {"name": "중국 위안", "rate_to_usd": 7.25, "symbol": "¥"},
}

# ============================================================
# Tool 정의 (OpenAI Function Calling 스키마)
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 도시의 현재 날씨 정보를 조회합니다. 지원 도시: 서울(seoul), 도쿄(tokyo), 상하이(shanghai)",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "도시 이름 (영문): seoul, tokyo, shanghai 중 하나",
                        "enum": ["seoul", "tokyo", "shanghai"],
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "통화의 현재 환율을 조회합니다. USD 기준 환율을 반환합니다. 지원 통화: KRW(한국 원), JPY(일본 엔), CNY(중국 위안)",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "통화 코드: KRW, JPY, CNY 중 하나",
                        "enum": ["KRW", "JPY", "CNY"],
                    }
                },
                "required": ["currency"],
            },
        },
    },
]

# ============================================================
# Tool 실행 함수들
# ============================================================


def get_weather(city: str) -> dict:
    """
    도시의 날씨 정보를 반환합니다.

    Args:
        city: 도시 코드 (seoul, tokyo, shanghai)

    Returns:
        날씨 정보 딕셔너리
    """
    if city not in WEATHER_DATA:
        return {"error": f"지원하지 않는 도시입니다: {city}"}

    return WEATHER_DATA[city]


def get_exchange_rate(currency: str) -> dict:
    """
    통화의 환율 정보를 반환합니다.

    Args:
        currency: 통화 코드 (KRW, JPY, CNY)

    Returns:
        환율 정보 딕셔너리
    """
    if currency not in EXCHANGE_RATE_DATA:
        return {"error": f"지원하지 않는 통화입니다: {currency}"}

    return EXCHANGE_RATE_DATA[currency]


def execute_tool(name: str, arguments: dict) -> str:
    """
    Tool 이름과 인자를 받아 실행하고 JSON 문자열을 반환합니다.

    Args:
        name: Tool 이름 (get_weather, get_exchange_rate)
        arguments: Tool 인자 딕셔너리

    Returns:
        실행 결과 JSON 문자열
    """
    if name == "get_weather":
        result = get_weather(arguments["city"])
    elif name == "get_exchange_rate":
        result = get_exchange_rate(arguments["currency"])
    else:
        result = {"error": f"알 수 없는 Tool입니다: {name}"}

    return json.dumps(result, ensure_ascii=False)
