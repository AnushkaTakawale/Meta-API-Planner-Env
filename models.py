import sys
import os
from typing import Literal, Union
from pydantic import BaseModel
# Force OpenEnv imports to work across Python 3.11 and 3.14
try:
    from openenv.core.env_server.types import Action, Field, Observation
except ImportError:
    # Fallback for different library structures
    from openenv.core.env_server import Action, Field, Observation

# ---------------------------------------------------------------------------
# Core Data Models
# ---------------------------------------------------------------------------

class ApiWorkflowAction(Action):
    type: Literal["ApiWorkflowAction"] = "ApiWorkflowAction"
    message: str = Field(..., description="Message to echo back")

class ApiWorkflowObservation(Observation):
    echoed_message: str = Field(default="", description="The echoed message")
    message_length: int = Field(default=0, description="Length of the echoed message")

# ---------------------------------------------------------------------------
# Level 1: Calendar Tool
# ---------------------------------------------------------------------------

class AddCalendarEvent(Action):
    type: Literal["AddCalendarEvent"] = "AddCalendarEvent"
    title: str = Field(..., description="Title of the calendar event")
    date: str = Field(..., description="Date of the event (YYYY-MM-DD)")
    time: str = Field(..., description="Time of the event (HH:MM, 24-hour)")

class CalendarObservation(Observation):
    success: bool = Field(default=False, description="Whether the event was stored")
    event_count: int = Field(default=0, description="Total events stored so far")
    message: str = Field(default="", description="Human-readable status message")

# ---------------------------------------------------------------------------
# Level 2: Search Tool
# ---------------------------------------------------------------------------

class SearchContact(Action):
    type: Literal["SearchContact"] = "SearchContact"
    name: str = Field(..., description="Name of the contact to search for")

class ContactObservation(Observation):
    email: str = Field(default="", description="The found email address")
    success: bool = Field(default=False, description="Whether the contact was found")

# ---------------------------------------------------------------------------
# Level 3: Advanced Scheduling Tool
# ---------------------------------------------------------------------------

class ScheduleMeeting(Action):
    type: Literal["ScheduleMeeting"] = "ScheduleMeeting"
    title: str = Field(..., description="Title of the meeting")
    date: str = Field(..., description="Date of the meeting")
    time: str = Field(default="", description="Time of the meeting")
    location: str = Field(..., description="Location of the meeting")
    email: str = Field(default="", description="Email of the attendee")