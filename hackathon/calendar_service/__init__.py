"""
Calendar Service Module
Provides Google Calendar integration for the HR Agent system.
"""

from .auth import get_calendar_service
from .calendar_tools import (
    create_event,
    list_events,
    get_event,
    update_event,
    delete_event,
    search_events,
    list_calendars,
    send_day_reminders,
    find_interview_slots,
    book_interview_slot,
)
from .smart_scheduler import (
    find_available_slots,
    format_slots_for_display,
    book_slot,
    get_timezone_for_city,
)
from .reminder_service import send_reminders_for_today

__all__ = [
    "get_calendar_service",
    "create_event",
    "list_events",
    "get_event",
    "update_event",
    "delete_event",
    "search_events",
    "list_calendars",
    "send_day_reminders",
    "find_interview_slots",
    "book_interview_slot",
    "find_available_slots",
    "format_slots_for_display",
    "book_slot",
    "get_timezone_for_city",
    "send_reminders_for_today",
]
