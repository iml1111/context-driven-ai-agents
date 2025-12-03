"""
Chapter 9-2: Mock Calendar MCP Server

FastMCP로 구현한 로컬 MCP 서버.
일정 조회, 추가, 수정, 삭제 기능을 제공합니다.

실행: python server.py
"""

import json
import uvicorn
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calendar")

# ============================================================
# Mock 데이터 (인메모리)
# ============================================================

MOCK_NOW = {"date": "12-04", "time": "09:30"}

CALENDAR_EVENTS = [
    {
        "id": "evt_001",
        "title": "팀 주간 회의",
        "date": "12-04",
        "time": "10:00",
        "duration": 60,
        "location": "회의실 A",
        "description": "주간 업무 공유 및 이슈 논의",
    },
    {
        "id": "evt_002",
        "title": "점심 약속",
        "date": "12-04",
        "time": "12:30",
        "duration": 90,
        "location": "강남역 근처",
        "description": "친구와 점심 식사",
    },
    {
        "id": "evt_003",
        "title": "프로젝트 마감",
        "date": "12-05",
        "time": "18:00",
        "duration": 0,
        "location": "",
        "description": "Q4 프로젝트 최종 제출",
    },
    {
        "id": "evt_004",
        "title": "치과 예약",
        "date": "12-06",
        "time": "14:00",
        "duration": 30,
        "location": "서울치과의원",
        "description": "정기 검진",
    },
]


# ============================================================
# MCP Tools 정의
# ============================================================


@mcp.tool()
def get_current_datetime() -> str:
    """
    현재 날짜와 시간을 조회합니다 (Mock 데이터).

    Returns:
        현재 날짜/시간 JSON 문자열
    """
    return json.dumps(
        {"date": MOCK_NOW["date"], "time": MOCK_NOW["time"], "message": f"현재 {MOCK_NOW['date']} {MOCK_NOW['time']}입니다."},
        ensure_ascii=False,
    )


@mcp.tool()
def list_events(date: str | None = None) -> str:
    """
    일정 목록을 조회합니다.

    Args:
        date: 특정 날짜 (MM-DD 형식). 생략 시 전체 일정 반환.

    Returns:
        일정 목록 JSON 문자열
    """
    if date:
        events = [e for e in CALENDAR_EVENTS if e["date"] == date]
    else:
        events = CALENDAR_EVENTS

    return json.dumps(
        {"count": len(events), "events": sorted(events, key=lambda x: (x["date"], x["time"]))},
        ensure_ascii=False,
    )


@mcp.tool()
def get_event(event_id: str) -> str:
    """
    특정 일정의 상세 정보를 조회합니다.

    Args:
        event_id: 일정 ID (예: evt_001)

    Returns:
        일정 상세 정보 JSON 문자열
    """
    for event in CALENDAR_EVENTS:
        if event["id"] == event_id:
            return json.dumps({"status": "found", "event": event}, ensure_ascii=False)

    return json.dumps({"status": "not_found", "error": f"일정을 찾을 수 없습니다: {event_id}"}, ensure_ascii=False)


@mcp.tool()
def add_event(
    title: str,
    date: str,
    time: str,
    duration: int = 60,
    location: str = "",
    description: str = "",
) -> str:
    """
    새 일정을 추가합니다.

    Args:
        title: 일정 제목
        date: 날짜 (MM-DD 형식)
        time: 시간 (HH:MM 형식)
        duration: 소요 시간 (분, 기본값 60)
        location: 장소 (선택)
        description: 설명 (선택)

    Returns:
        추가된 일정 정보 JSON 문자열
    """
    new_id = f"evt_{len(CALENDAR_EVENTS) + 1:03d}"
    new_event = {
        "id": new_id,
        "title": title,
        "date": date,
        "time": time,
        "duration": duration,
        "location": location,
        "description": description,
    }
    CALENDAR_EVENTS.append(new_event)

    return json.dumps(
        {"status": "created", "message": f"'{title}' 일정이 추가되었습니다.", "event": new_event},
        ensure_ascii=False,
    )


@mcp.tool()
def update_event(
    event_id: str,
    title: str | None = None,
    date: str | None = None,
    time: str | None = None,
    duration: int | None = None,
    location: str | None = None,
    description: str | None = None,
) -> str:
    """
    기존 일정을 수정합니다.

    Args:
        event_id: 수정할 일정 ID
        title: 새 제목 (선택)
        date: 새 날짜 (선택)
        time: 새 시간 (선택)
        duration: 새 소요 시간 (선택)
        location: 새 장소 (선택)
        description: 새 설명 (선택)

    Returns:
        수정된 일정 정보 JSON 문자열
    """
    for event in CALENDAR_EVENTS:
        if event["id"] == event_id:
            if title is not None:
                event["title"] = title
            if date is not None:
                event["date"] = date
            if time is not None:
                event["time"] = time
            if duration is not None:
                event["duration"] = duration
            if location is not None:
                event["location"] = location
            if description is not None:
                event["description"] = description

            return json.dumps(
                {"status": "updated", "message": f"'{event['title']}' 일정이 수정되었습니다.", "event": event},
                ensure_ascii=False,
            )

    return json.dumps({"status": "not_found", "error": f"일정을 찾을 수 없습니다: {event_id}"}, ensure_ascii=False)


@mcp.tool()
def delete_event(event_id: str) -> str:
    """
    일정을 삭제합니다.

    Args:
        event_id: 삭제할 일정 ID

    Returns:
        삭제 결과 JSON 문자열
    """
    global CALENDAR_EVENTS

    for i, event in enumerate(CALENDAR_EVENTS):
        if event["id"] == event_id:
            deleted = CALENDAR_EVENTS.pop(i)
            return json.dumps(
                {"status": "deleted", "message": f"'{deleted['title']}' 일정이 삭제되었습니다."},
                ensure_ascii=False,
            )

    return json.dumps({"status": "not_found", "error": f"일정을 찾을 수 없습니다: {event_id}"}, ensure_ascii=False)


if __name__ == "__main__":
    print("🚀 Calendar MCP Server starting...")
    print("📍 Endpoint: http://localhost:8000/sse")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8000)
