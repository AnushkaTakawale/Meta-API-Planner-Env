# task_definitions.py
from typing import Any, Dict, List

def grade_search_contact(trajectory: List[Dict[str, Any]]) -> float:
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            if obs.get("success") and obs.get("email") == "rahul@meta.com":
                return 0.9
    return 0.1

def grade_add_calendar_event(trajectory: List[Dict[str, Any]]) -> float:
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            if obs.get("success") and obs.get("event_count", 0) >= 1:
                return 0.9
    return 0.1

def grade_schedule_meeting(trajectory: List[Dict[str, Any]]) -> float:
    found_email = False
    scheduled = False
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            if obs.get("email") == "rahul@meta.com":
                found_email = True
            if obs.get("success") and obs.get("event_count", 0) >= 1 and found_email:
                scheduled = True
    if scheduled and found_email:
        return 0.85
    elif found_email:
        return 0.4
    return 0.1

def grade_reschedule_meeting(trajectory: List[Dict[str, Any]]) -> float:
    hit_conflict = False
    rescheduled = False
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            msg = obs.get("message", "")
            if "409" in msg or "already booked" in msg.lower():
                hit_conflict = True
            if obs.get("success") and hit_conflict:
                rescheduled = True
    if rescheduled and hit_conflict:
        return 0.95
    elif hit_conflict:
        return 0.3
    return 0.1

TASKS = [
    {
        "task_id": "search_contact",
        "description": "Find the email address of Rahul using the search contact tool.",
        "difficulty": "easy",
        "grader": grade_search_contact,
    },
    {
        "task_id": "add_calendar_event",
        "description": "Add a calendar event titled 'Team Standup' on 2026-05-01 at 09:00.",
        "difficulty": "easy",
        "grader": grade_add_calendar_event,
    },
    {
        "task_id": "schedule_meeting",
        "description": "Schedule a meeting with Rahul for 2026-05-02 at 11:00 at Meta Office.",
        "difficulty": "medium",
        "grader": grade_schedule_meeting,
    },
    {
        "task_id": "reschedule_meeting",
        "description": "Try to schedule on 2026-04-12 at 10:00 (busy). Handle conflict and reschedule.",
        "difficulty": "hard",
        "grader": grade_reschedule_meeting,
    },
]

TASK_DESCRIPTION = TASKS[2]["description"]
