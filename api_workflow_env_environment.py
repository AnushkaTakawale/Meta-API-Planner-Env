# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Api Workflow Env Environment Implementation.

Supports two action types:
  - ApiWorkflowAction : legacy echo action (kept for backward compatibility).
  - AddCalendarEvent  : stores a calendar event and returns a binary reward.

Reward logic
------------
  - 1.0  if the agent supplies a valid AddCalendarEvent with all three
         required fields (title, date, time) present and non-empty.
  - 0.0  if any required field is missing or empty, or if the legacy
         echo action is used (no calendar event stored).
"""

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import (
        AddCalendarEvent,
        ApiWorkflowAction,
        ApiWorkflowObservation,
        CalendarObservation,
        ContactObservation,
        ScheduleMeeting,
        SearchContact,
    )
except ImportError:
    from api_workflow_env.models import (  # noqa: E402
        AddCalendarEvent,
        ApiWorkflowAction,
        ApiWorkflowObservation,
        CalendarObservation,
        ContactObservation,
        ScheduleMeeting,
        SearchContact,
    )


class ApiWorkflowEnvironment(Environment):
    """
    API Workflow environment with calendar scheduling support.

    The environment accepts two kinds of actions:

    1. **AddCalendarEvent** – the primary task action.  The agent must
       provide *title*, *date*, and *time*.  A reward of **1.0** is given
       when all fields are present and non-empty; **0.0** otherwise.
       Successfully added events are stored in ``self.calendar``.

    2. **ApiWorkflowAction** – legacy echo action retained for backward
       compatibility.  Always returns reward **0.0**.

    Example::

        env = ApiWorkflowEnvironment()
        obs = env.reset()

        # Successful calendar event
        obs = env.step(AddCalendarEvent(
            title="Team Standup",
            date="2025-05-01",
            time="09:30",
        ))
        assert obs.reward == 1.0
        assert len(env.calendar) == 1

        # Missing field → reward 0.0
        obs = env.step(AddCalendarEvent(title="Lunch", date="", time=""))
        assert obs.reward == 0.0
    """

    # Allow multiple simultaneous WebSocket sessions.
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self) -> None:
        """Initialize the environment with an empty calendar."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count: int = 0
        # Stores successfully added calendar events as plain dicts.
        self.calendar: list[dict] = []
        self.meetings: list[dict] = []
        self.contacts: dict[str, str] = {
            'Rahul': 'rahul@meta.com', 
            'Anjali': 'anjali@ai.io'
        }
        self.busy_slots: list[str] = ['2026-04-12 10:00', '2026-04-12 14:00']
        self._hit_conflict: bool = False

    # ------------------------------------------------------------------
    # Environment lifecycle
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        **kwargs: object,
    ) -> CalendarObservation:
        """
        Reset the environment and clear the calendar.

        Args:
            seed:       Optional RNG seed (unused, reserved for compatibility).
            episode_id: Optional episode identifier override.
            **kwargs:   Additional keyword arguments (ignored).

        Returns:
            CalendarObservation signalling the environment is ready.
        """
        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )
        self._reset_count += 1
        self.calendar = []
        self.meetings = []
        self._hit_conflict = False

        return CalendarObservation(
            success=False,
            event_count=0,
            message="Api Workflow Env environment ready! Calendar cleared.",
            done=False,
            reward=0.0,
        )

    # ------------------------------------------------------------------
    # Step
    # ------------------------------------------------------------------

    def step(
        self,
        action: ApiWorkflowAction | AddCalendarEvent | ScheduleMeeting | SearchContact,
        timeout_s: float | None = None,
        **kwargs: object,
    ) -> CalendarObservation | ApiWorkflowObservation:  # type: ignore[override]
        """
        Execute one environment step.

        Dispatches to the appropriate handler based on the action type.

        Args:
            action:    Either an ``AddCalendarEvent`` or legacy
                       ``ApiWorkflowAction``.
            timeout_s: Optional timeout in seconds (unused, reserved for
                       compatibility with the base class signature).
            **kwargs:  Additional keyword arguments (ignored).

        Returns:
            * ``CalendarObservation`` for calendar actions.
            * ``ApiWorkflowObservation`` for legacy echo actions.
        """
        self._state.step_count += 1

        if isinstance(action, AddCalendarEvent):
            return self._handle_calendar_event(action)
            
        if isinstance(action, ScheduleMeeting):
            return self._handle_schedule_meeting(action)

        if isinstance(action, SearchContact):
            return self._handle_search_contact(action)

        # Legacy echo path
        return self._handle_echo(action)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _handle_calendar_event(self, action: AddCalendarEvent) -> CalendarObservation:
        """
        Handle an AddCalendarEvent action.

        Reward logic:
          - 1.0 → all three fields (title, date, time) are non-empty strings.
          - 0.0 → one or more fields are missing or blank.

        The event is stored in ``self.calendar`` **only** on success.

        Args:
            action: The calendar event action from the agent.

        Returns:
            CalendarObservation with reward 1.0 on success, 0.0 on failure.
        """
        # Validate that every required field is present and non-empty.
        missing = [
            field
            for field, value in [
                ("title", action.title),
                ("date", action.date),
                ("time", action.time),
            ]
            if not value or not value.strip()
        ]

        if missing:
            # Agent missed one or more fields → reward 0.0, nothing stored.
            return CalendarObservation(
                success=False,
                event_count=len(self.calendar),
                message=(
                    f"Event NOT added. Missing or empty field(s): "
                    f"{', '.join(missing)}."
                ),
                done=False,
                reward=0.0,
                metadata={"step": self._state.step_count, "missing_fields": missing},
            )

        # All fields valid → store the event and reward the agent.
        event = {
            "title": action.title.strip(),
            "date": action.date.strip(),
            "time": action.time.strip(),
        }
        self.calendar.append(event)

        return CalendarObservation(
            success=True,
            event_count=len(self.calendar),
            message=(
                f"Event '{event['title']}' added for {event['date']} "
                f"at {event['time']}."
            ),
            done=False,
            reward=1.0,
            metadata={"step": self._state.step_count, "event": event},
        )

    def _handle_echo(self, action: ApiWorkflowAction) -> ApiWorkflowObservation:
        """
        Handle a legacy echo action (reward always 0.0).

        Args:
            action: Legacy echo action.

        Returns:
            ApiWorkflowObservation echoing the message.
        """
        message = action.message
        return ApiWorkflowObservation(
            echoed_message=message,
            message_length=len(message),
            done=False,
            reward=0.0,
            metadata={"step": self._state.step_count},
        )

    def _handle_schedule_meeting(self, action: ScheduleMeeting) -> CalendarObservation:
        missing = [
            field
            for field, value in [
                ("title", action.title),
                ("date", action.date),
                ("location", action.location),
                ("email", action.email),
            ]
            if not value or not getattr(value, "strip", lambda: value)()
        ]

        if missing:
            return CalendarObservation(
                success=False,
                event_count=len(self.meetings),
                message=f"Error: Missing or empty field(s): {', '.join(missing)}.",
                done=False,
                reward=0.0,
            )

        # Check for conflicts
        slot_candidate = f"{action.date.strip()} {action.time.strip()}" if action.time else action.date.strip()
        is_conflict = slot_candidate in self.busy_slots or any(bs in action.date for bs in self.busy_slots)
        
        if is_conflict:
            self._hit_conflict = True
            return CalendarObservation(
                success=False,
                event_count=len(self.meetings),
                message="Status 409: Slot already booked. Please suggest an alternative time.",
                done=False,
                reward=0.0,
            )

        meeting = {
            "title": action.title,
            "date": action.date,
            "time": action.time,
            "location": action.location,
            "email": action.email,
        }
        self.meetings.append(meeting)
        
        # Reward +1.0 for completing the meeting with the valid email included.
        # Hard level: Double Reward (+2.0) if successfully rescheduled after hitting a conflict.
        has_val_email = action.email in self.contacts.values()
        
        if self._hit_conflict:
            reward = 2.0
        else:
            reward = 1.0 if has_val_email else 0.0

        return CalendarObservation(
            success=True,
            event_count=len(self.meetings),
            message="Meeting scheduled successfully.",
            done=False,
            reward=reward,
        )

    def _handle_search_contact(self, action: SearchContact) -> ContactObservation:
        email = self.contacts.get(action.name)
        if email:
            return ContactObservation(
                email=email,
                success=True,
                done=False,
                reward=0.5,
                metadata={"step": self._state.step_count}
            )
        return ContactObservation(
            email="",
            success=False,
            done=False,
            reward=0.0,
            metadata={"step": self._state.step_count}
        )



    # ------------------------------------------------------------------
    # State property
    # ------------------------------------------------------------------

    @property
    def state(self) -> State:
        """Return the current episode state."""
        return self._state
