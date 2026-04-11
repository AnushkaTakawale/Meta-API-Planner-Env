# task.py
# Task definitions with graders for the API Workflow Environment

from typing import Any

# ─────────────────────────────────────────────
# Task 1: Search Contact
# ─────────────────────────────────────────────
TASK_1 = {
    "task_id": "search_contact",
    "description": "Find the email address of Rahul using the search contact tool.",
    "difficulty": "easy",
}

def grade_task_1(trajectory: list[dict[str, Any]]) -> float:
    """
    Grade: did the agent successfully find Rahul's email?
    Returns a score strictly between 0 and 1.
    """
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            if obs.get("success") and obs.get("email") == "rahul@meta.com":
                return 0.9
    return 0.1


# ─────────────────────────────────────────────
# Task 2: Add Calendar Event
# ─────────────────────────────────────────────
TASK_2 = {
    "task_id": "add_calendar_event",
    "description": "Add a calendar event titled 'Team Standup' on 2026-05-01 at 09:00.",
    "difficulty": "easy",
}

def grade_task_2(trajectory: list[dict[str, Any]]) -> float:
    """
    Grade: did the agent successfully add the calendar event?
    Returns a score strictly between 0 and 1.
    """
    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            if obs.get("success") and obs.get("event_count", 0) >= 1:
                return 0.9
    return 0.1


# ─────────────────────────────────────────────
# Task 3: Schedule Meeting
# ─────────────────────────────────────────────
TASK_3 = {
    "task_id": "schedule_meeting",
    "description": (
        "Schedule a meeting with Rahul for 2026-05-02 at 11:00 "
        "at Meta Office. Find his email first and use it."
    ),
    "difficulty": "medium",
}

def grade_task_3(trajectory: list[dict[str, Any]]) -> float:
    """
    Grade: did the agent schedule a meeting with a valid email?
    Returns a score strictly between 0 and 1.
    """
    found_email = False
    scheduled_meeting = False

    for step in trajectory:
        obs = step.get("observation", {})
        if isinstance(obs, dict):
            # Check if contact was searched
            if obs.get("email") == "rahul@meta.com":
                found_email = True
            # Check if meeting was scheduled
            if obs.get("success") and obs.get("event_count", 0) >= 1 and found_email:
                scheduled_meeting = True

    if scheduled_meeting and found_email:
        return 0.85
    elif found_email:
        return 0.4
    return 0.1


# ─────────────────────────────────────────────
# Task 4: Handle Conflict and Reschedule
# ─────────────────────────────────────────────
TASK_4 = {
    "task_id": "reschedule_meeting",
    "description": (
        "Try to schedule a meeting on 2026-04-12 at 10:00 (which is busy). "
        "Handle the conflict and reschedule to a different time."
    ),
    "difficulty": "hard",
}

def grade_task_4(trajectory: list[dict[str, Any]]) -> float:
    """
    Grade: did the agent handle conflict and successfully reschedule?
    Returns a score strictly between 0 and 1.
    """
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


# ─────────────────────────────────────────────
# All Tasks + Graders Registry
# ─────────────────────────────────────────────
TASKS = [
    {"task": TASK_1, "grader": grade_task_1},
    {"task": TASK_2, "grader": grade_task_2},
    {"task": TASK_3, "grader": grade_task_3},
    {"task": TASK_4, "grader": grade_task_4},
]

# Default task description (used by inference.py)
TASK_DESCRIPTION = TASK_3["description"]
