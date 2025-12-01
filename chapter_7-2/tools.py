"""
Chapter 7-2: Tool 통합 - 회식 코스 플래너

도구에서 생성되는 과도한 컨텍스트를 방지하기 위해
여러 API를 기능별로 그룹화하여 통합 도구로 제공합니다.

1. get_place_info (READ): 카카오 로컬 API 통합
2. manage_course (WRITE): JSON 파일 기반 코스 관리

실제 API: 카카오 로컬 API
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# Tool 정의 (OpenAI Function Calling 스키마)
# ============================================================

TOOLS = [
    # READ Tool: 장소 정보 조회 (카카오 API)
    {
        "type": "function",
        "function": {
            "name": "get_place_info",
            "description": "카카오 로컬 API를 통해 장소 정보를 조회합니다. action 파라미터로 조회 유형을 선택합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["keyword_search", "category_search", "coord_to_address", "coord_to_region"],
                        "description": "keyword_search: 키워드 검색, category_search: 카테고리 검색, coord_to_address: 좌표→주소, coord_to_region: 좌표→행정구역",
                    },
                    "query": {
                        "type": "string",
                        "description": "[keyword_search용] 검색 키워드 (예: '강남역', '삼겹살')",
                    },
                    "category_code": {
                        "type": "string",
                        "description": "[category_search용] 카테고리 코드 (FD6: 음식점, CE7: 카페, CT1: 문화시설)",
                    },
                    "x": {
                        "type": "string",
                        "description": "[category_search/coord_to_*용] 경도 (longitude)",
                    },
                    "y": {
                        "type": "string",
                        "description": "[category_search/coord_to_*용] 위도 (latitude)",
                    },
                    "radius": {
                        "type": "integer",
                        "description": "[category_search용] 검색 반경 (미터, 기본값 500)",
                    },
                },
                "required": ["action"],
            },
        },
    },
    # WRITE Tool: 코스 관리 (JSON 파일)
    {
        "type": "function",
        "function": {
            "name": "manage_course",
            "description": "회식 코스를 관리합니다. 코스 정보는 JSON 파일에 저장됩니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["add", "remove", "list", "clear"],
                        "description": "add: 코스에 장소 추가, remove: 장소 제거, list: 코스 목록 조회, clear: 코스 초기화",
                    },
                    "place_id": {
                        "type": "string",
                        "description": "[add/remove용] 장소 ID",
                    },
                    "place_name": {
                        "type": "string",
                        "description": "[add용] 장소 이름",
                    },
                    "step": {
                        "type": "string",
                        "description": "[add용] 코스 순서 (예: '1차', '2차', '3차')",
                    },
                    "address": {
                        "type": "string",
                        "description": "[add용] 장소 주소",
                    },
                    "category": {
                        "type": "string",
                        "description": "[add용] 장소 카테고리",
                    },
                },
                "required": ["action"],
            },
        },
    },
]

# ============================================================
# 카카오 API 설정
# ============================================================

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_BASE_URL = "https://dapi.kakao.com/v2/local"

# JSON 파일 경로
COURSE_FILE = Path(__file__).parent / "course_data.json"

# ============================================================
# READ Tool 구현: get_place_info (카카오 API)
# ============================================================


def _kakao_request(endpoint: str, params: dict) -> dict:
    """카카오 API 공통 요청 함수"""
    if not KAKAO_API_KEY:
        return {"error": "KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다."}

    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    url = f"{KAKAO_BASE_URL}/{endpoint}"

    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def keyword_search(query: str, x: str | None = None, y: str | None = None) -> dict:
    """키워드로 장소 검색"""
    params = {"query": query, "size": 5}
    if x and y:
        params["x"] = x
        params["y"] = y
        params["radius"] = 1000

    data = _kakao_request("search/keyword.json", params)
    if "error" in data:
        return data

    results = []
    for doc in data.get("documents", []):
        results.append({
            "place_id": doc.get("id"),
            "name": doc.get("place_name"),
            "category": doc.get("category_name", "").split(" > ")[-1],
            "address": doc.get("road_address_name") or doc.get("address_name"),
            "phone": doc.get("phone", ""),
            "x": doc.get("x"),
            "y": doc.get("y"),
            "distance": doc.get("distance", ""),
        })

    return {"query": query, "count": len(results), "places": results}


def category_search(category_code: str, x: str, y: str, radius: int = 500) -> dict:
    """카테고리로 장소 검색"""
    params = {
        "category_group_code": category_code,
        "x": x,
        "y": y,
        "radius": radius,
        "size": 5,
        "sort": "distance",
    }

    data = _kakao_request("search/category.json", params)
    if "error" in data:
        return data

    results = []
    for doc in data.get("documents", []):
        results.append({
            "place_id": doc.get("id"),
            "name": doc.get("place_name"),
            "category": doc.get("category_name", "").split(" > ")[-1],
            "address": doc.get("road_address_name") or doc.get("address_name"),
            "phone": doc.get("phone", ""),
            "x": doc.get("x"),
            "y": doc.get("y"),
            "distance": doc.get("distance", ""),
        })

    return {"category_code": category_code, "count": len(results), "places": results}


def coord_to_address(x: str, y: str) -> dict:
    """좌표를 주소로 변환"""
    params = {"x": x, "y": y}

    data = _kakao_request("geo/coord2address.json", params)
    if "error" in data:
        return data

    documents = data.get("documents", [])
    if not documents:
        return {"error": "해당 좌표의 주소를 찾을 수 없습니다."}

    doc = documents[0]
    result = {"x": x, "y": y}

    if doc.get("road_address"):
        result["road_address"] = doc["road_address"].get("address_name")
    if doc.get("address"):
        result["jibun_address"] = doc["address"].get("address_name")

    return result


def coord_to_region(x: str, y: str) -> dict:
    """좌표를 행정구역으로 변환"""
    params = {"x": x, "y": y}

    data = _kakao_request("geo/coord2regioncode.json", params)
    if "error" in data:
        return data

    documents = data.get("documents", [])
    if not documents:
        return {"error": "해당 좌표의 행정구역을 찾을 수 없습니다."}

    result = {"x": x, "y": y, "regions": []}
    for doc in documents:
        result["regions"].append({
            "type": doc.get("region_type"),
            "name": doc.get("address_name"),
            "code": doc.get("code"),
        })

    return result


def get_place_info(action: str, **kwargs) -> dict:
    """장소 정보 조회 통합 함수 (READ Tool)"""
    if action == "keyword_search":
        query = kwargs.get("query")
        if not query:
            return {"error": "keyword_search action에는 query 파라미터가 필요합니다."}
        return keyword_search(query, kwargs.get("x"), kwargs.get("y"))

    elif action == "category_search":
        category_code = kwargs.get("category_code")
        x = kwargs.get("x")
        y = kwargs.get("y")
        if not all([category_code, x, y]):
            return {"error": "category_search action에는 category_code, x, y 파라미터가 필요합니다."}
        return category_search(category_code, x, y, kwargs.get("radius", 500))

    elif action == "coord_to_address":
        x = kwargs.get("x")
        y = kwargs.get("y")
        if not all([x, y]):
            return {"error": "coord_to_address action에는 x, y 파라미터가 필요합니다."}
        return coord_to_address(x, y)

    elif action == "coord_to_region":
        x = kwargs.get("x")
        y = kwargs.get("y")
        if not all([x, y]):
            return {"error": "coord_to_region action에는 x, y 파라미터가 필요합니다."}
        return coord_to_region(x, y)

    else:
        return {"error": f"알 수 없는 action입니다: {action}"}


# ============================================================
# WRITE Tool 구현: manage_course (JSON 파일)
# ============================================================


def _load_course() -> dict:
    """JSON 파일에서 코스 데이터 로드"""
    if COURSE_FILE.exists():
        with open(COURSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"places": []}


def _save_course(data: dict) -> None:
    """코스 데이터를 JSON 파일에 저장 (places만 저장)"""
    clean_data = {"places": data.get("places", [])}
    with open(COURSE_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)


def manage_course(action: str, **kwargs) -> dict:
    """코스 관리 통합 함수 (WRITE Tool)"""
    course = _load_course()

    if action == "add":
        place_id = kwargs.get("place_id")
        place_name = kwargs.get("place_name")
        step = kwargs.get("step")

        if not all([place_id, place_name, step]):
            return {"error": "add action에는 place_id, place_name, step 파라미터가 필요합니다."}

        # 중복 체크
        if any(p["place_id"] == place_id for p in course["places"]):
            return {"error": f"이미 코스에 추가된 장소입니다: {place_name}"}

        place = {
            "place_id": place_id,
            "place_name": place_name,
            "step": step,
            "address": kwargs.get("address", ""),
            "category": kwargs.get("category", ""),
        }
        course["places"].append(place)
        _save_course(course)

        return {
            "status": "success",
            "message": f"'{place_name}'이(가) {step}로 추가되었습니다.",
            "place": place,
        }

    elif action == "remove":
        place_id = kwargs.get("place_id")
        if not place_id:
            return {"error": "remove action에는 place_id 파라미터가 필요합니다."}

        original_count = len(course["places"])
        course["places"] = [p for p in course["places"] if p["place_id"] != place_id]

        if len(course["places"]) == original_count:
            return {"error": f"해당 place_id({place_id})가 코스에 없습니다."}

        _save_course(course)
        return {"status": "success", "message": "장소가 코스에서 제거되었습니다."}

    elif action == "list":
        # step 순서로 정렬
        places = sorted(course["places"], key=lambda x: x.get("step", ""))
        return {
            "status": "success",
            "count": len(places),
            "places": places,
            "file_path": str(COURSE_FILE),
        }

    elif action == "clear":
        course["places"] = []
        _save_course(course)
        return {"status": "success", "message": "코스가 초기화되었습니다."}

    else:
        return {"error": f"알 수 없는 action입니다: {action}"}


# ============================================================
# Tool 실행 디스패처
# ============================================================


def execute_tool(name: str, arguments: dict) -> str:
    """Tool 이름과 인자를 받아 실행하고 JSON 문자열을 반환합니다."""
    if name == "get_place_info":
        action = arguments.pop("action")
        result = get_place_info(action, **arguments)
    elif name == "manage_course":
        action = arguments.pop("action")
        result = manage_course(action, **arguments)
    else:
        result = {"error": f"알 수 없는 Tool입니다: {name}"}

    return json.dumps(result, ensure_ascii=False)
