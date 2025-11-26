"""
Chapter 7-2: Tool 통합 - BTC 투자 도우미

도구에서 생성되는 과도한 컨텍스트를 방지하기 위해
여러 API를 기능별로 그룹화하여 통합 도구로 제공합니다.

1. get_btc_info (READ): 가격 조회 + 캔들 조회를 하나의 도구로 통합
2. execute_btc_order (WRITE): 매수/매도를 하나의 도구로 통합 (Mock)

실제 API: 빗썸 공개 API (인증 불필요)
"""

import json
import uuid
from datetime import datetime

import requests

# ============================================================
# Tool 정의 (OpenAI Function Calling 스키마)
# ============================================================

TOOLS = [
    # READ Tool: 정보 조회 (action으로 조회 유형 선택)
    {
        "type": "function",
        "function": {
            "name": "get_btc_info",
            "description": "BTC 투자 관련 정보를 조회합니다. action 파라미터로 조회 유형을 선택합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["price", "candles"],
                        "description": "price: 현재 가격 조회, candles: 최근 20일 일봉 캔들 조회",
                    }
                },
                "required": ["action"],
            },
        },
    },
    # WRITE Tool: 주문 실행 (Mock)
    {
        "type": "function",
        "function": {
            "name": "execute_btc_order",
            "description": "BTC 매수 또는 매도 주문을 실행합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "buy: 매수, sell: 매도",
                    },
                    "amount_krw": {
                        "type": "number",
                        "description": "주문 금액 (KRW 단위)",
                    },
                },
                "required": ["action", "amount_krw"],
            },
        },
    },
]

# ============================================================
# 빗썸 API 엔드포인트
# ============================================================

BITHUMB_TICKER_URL = "https://api.bithumb.com/v1/ticker"
BITHUMB_CANDLES_URL = "https://api.bithumb.com/v1/candles/days"

# ============================================================
# READ Tool 구현: get_btc_info
# ============================================================


def get_btc_price() -> dict:
    """
    빗썸 API를 통해 BTC 현재 가격을 조회합니다.

    Returns:
        가격 정보 딕셔너리
    """
    params = {"markets": "KRW-BTC"}
    response = requests.get(BITHUMB_TICKER_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    if data:
        ticker = data[0]
        return {
            "market": ticker.get("market", "KRW-BTC"),
            "trade_price": ticker.get("trade_price"),
            "signed_change_rate": ticker.get("signed_change_rate"),
            "signed_change_price": ticker.get("signed_change_price"),
            "acc_trade_volume_24h": ticker.get("acc_trade_volume_24h"),
            "timestamp": ticker.get("timestamp"),
        }

    return {"error": "데이터를 가져올 수 없습니다."}


def get_btc_candles() -> dict:
    """
    빗썸 API를 통해 BTC 최근 20일 일봉 캔들을 조회합니다.

    Returns:
        캔들 데이터 리스트
    """
    params = {"market": "KRW-BTC", "count": 20}
    response = requests.get(BITHUMB_CANDLES_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    if data:
        # 필요한 필드만 추출하여 컨텍스트 크기 최적화
        candles = []
        for candle in data:
            candles.append(
                {
                    "date": candle.get("candle_date_time_kst", "")[:10],
                    "open": candle.get("opening_price"),
                    "high": candle.get("high_price"),
                    "low": candle.get("low_price"),
                    "close": candle.get("trade_price"),
                    "volume": candle.get("candle_acc_trade_volume"),
                }
            )
        return {"market": "KRW-BTC", "candles": candles, "count": len(candles)}

    return {"error": "데이터를 가져올 수 없습니다."}


def get_btc_info(action: str) -> dict:
    """
    BTC 정보 조회 통합 함수 (READ Tool)

    Args:
        action: "price" 또는 "candles"

    Returns:
        조회 결과 딕셔너리
    """
    if action == "price":
        return get_btc_price()
    elif action == "candles":
        return get_btc_candles()
    else:
        return {"error": f"알 수 없는 action입니다: {action}"}


# ============================================================
# WRITE Tool 구현: execute_btc_order (Mock)
# ============================================================


def execute_btc_order(action: str, amount_krw: float) -> dict:
    """
    BTC 주문 실행 Mock 함수 (WRITE Tool)

    실제로 주문을 실행하지 않고, 성공 응답만 반환합니다.

    Args:
        action: "buy" 또는 "sell"
        amount_krw: 주문 금액 (KRW)

    Returns:
        Mock 주문 결과 딕셔너리
    """
    if action not in ["buy", "sell"]:
        return {"error": f"알 수 없는 action입니다: {action}"}

    if amount_krw <= 0:
        return {"error": "주문 금액은 0보다 커야 합니다."}

    # 현재 가격을 조회하여 Mock 체결 수량 계산
    price_info = get_btc_price()
    current_price = price_info.get("trade_price", 145000000)

    btc_amount = amount_krw / current_price

    return {
        "status": "success",
        "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
        "action": action,
        "amount_krw": amount_krw,
        "executed_price": current_price,
        "btc_amount": round(btc_amount, 8),
        "timestamp": datetime.now().isoformat(),
        "message": f"[Mock] {action.upper()} 주문이 성공적으로 체결되었습니다.",
    }


# ============================================================
# Tool 실행 디스패처
# ============================================================


def execute_tool(name: str, arguments: dict) -> str:
    """
    Tool 이름과 인자를 받아 실행하고 JSON 문자열을 반환합니다.

    Args:
        name: Tool 이름 (get_btc_info, execute_btc_order)
        arguments: Tool 인자 딕셔너리

    Returns:
        실행 결과 JSON 문자열
    """
    if name == "get_btc_info":
        result = get_btc_info(arguments["action"])
    elif name == "execute_btc_order":
        result = execute_btc_order(arguments["action"], arguments["amount_krw"])
    else:
        result = {"error": f"알 수 없는 Tool입니다: {name}"}

    return json.dumps(result, ensure_ascii=False)
