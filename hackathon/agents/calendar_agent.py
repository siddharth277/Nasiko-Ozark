"""
Calendar Agent - Google Calendar Integration
Uses real Google Calendar API instead of in-memory mock
"""
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

# Import the calendar service functions
from calendar_service import (
    get_calendar_service,
    find_available_slots,
    format_slots_for_display,
    book_slot,
    get_timezone_for_city,
)

load_dotenv()

# Configuration from environment
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
HR_EMAIL = os.getenv("HR_EMAIL", "")


# Event type colors/labels (for compatibility with frontend)
EVENT_TYPES = {
    "interview": {"label": "Interview", "color": "#6366f1"},
    "followup": {"label": "Follow-up", "color": "#f59e0b"},
    "offer": {"label": "Offer", "color": "#10b981"},
}


def get_all_events() -> list[dict]:
    """Return all upcoming events from Google Calendar."""
    try:
        from datetime import timedelta, timezone
        
        svc = get_calendar_service()
        now_utc = datetime.now(timezone.utc)
        t_start = now_utc - timedelta(hours=1)
        t_end = now_utc + timedelta(days=90)  # Next 3 months
        
        res = svc.events().list(
            calendarId=CALENDAR_ID,
            timeMin=t_start.isoformat(),
            timeMax=t_end.isoformat(),
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        
        events = res.get("items", [])
        
        # Convert to frontend-compatible format
        result = []
        for ev in events:
            start_raw = ev["start"].get("dateTime", ev["start"].get("date", ""))
            end_raw = ev["end"].get("dateTime", ev["end"].get("date", ""))
            
            # Extract candidate info from description if available
            desc = ev.get("description", "")
            candidate_email = ""
            candidate_name = ""
            if "Email" in desc:
                for line in desc.split("\n"):
                    if "Email" in line and ":" in line:
                        candidate_email = line.split(":", 1)[1].strip()
                    elif "Candidate" in line and ":" in line:
                        candidate_name = line.split(":", 1)[1].strip()
            
            result.append({
                "id": ev.get("id", "")[:8],  # Shortened ID for display
                "title": ev.get("summary", "Untitled"),
                "datetime_str": start_raw,
                "event_type": "interview",  # Default type
                "candidate_name": candidate_name,
                "candidate_email": candidate_email,
                "notes": desc,
                "duration_minutes": 60,  # Default
                "created_at": ev.get("created", ""),
                "type_info": EVENT_TYPES["interview"],
                "full_event_id": ev.get("id", ""),  # Store full ID for operations
            })
        
        return sorted(result, key=lambda e: e.get("datetime_str", ""))
    
    except Exception as e:
        print(f"[Calendar] Error fetching events: {e}")
        return []


def get_events_for_month(year: int, month: int) -> list[dict]:
    """Return events for a specific month from Google Calendar."""
    all_events = get_all_events()
    prefix = f"{year}-{month:02d}"
    return [e for e in all_events if e.get("datetime_str", "").startswith(prefix)]


def add_event(
    title: str,
    datetime_str: str,
    event_type: str = "interview",
    candidate_name: str = "",
    candidate_email: str = "",
    notes: str = "",
    duration_minutes: int = 60
) -> dict:
    """
    Add a new event to Google Calendar.
    
    Args:
        title: Event title
        datetime_str: Start datetime in ISO format (YYYY-MM-DDTHH:MM:SS)
        event_type: Type of event (interview, followup, offer)
        candidate_name: Candidate's name
        candidate_email: Candidate's email
        notes: Additional notes
        duration_minutes: Duration in minutes
    
    Returns:
        dict with event details
    """
    try:
        from datetime import timedelta
        from zoneinfo import ZoneInfo
        
        svc = get_calendar_service()
        tz = ZoneInfo(TIMEZONE)
        
        # Parse the datetime string
        start_dt = datetime.fromisoformat(datetime_str.replace("Z", "")).replace(tzinfo=tz)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Build description
        description = notes
        if candidate_name:
            description = f"Candidate: {candidate_name}\n" + description
        if candidate_email:
            description = f"Email: {candidate_email}\n" + description
        
        # Prepare attendees
        attendees = []
        if candidate_email and candidate_email.strip():
            attendees.append({"email": candidate_email.strip()})
        if HR_EMAIL and HR_EMAIL != "your_gmail@gmail.com":
            attendees.append({"email": HR_EMAIL})
        
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
            "visibility": "public",
            "status": "confirmed",
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 15},
                ],
            },
        }
        
        if attendees:
            event["attendees"] = attendees
        
        created = svc.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            sendUpdates="all" if attendees else "none",
        ).execute()
        
        event_id = created.get("id", "")
        
        print(f"[Calendar] Event created: {title} on {datetime_str}")
        
        return {
            "id": event_id[:8],
            "title": title,
            "datetime_str": datetime_str,
            "event_type": event_type,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "notes": notes,
            "duration_minutes": duration_minutes,
            "created_at": datetime.now().isoformat(),
            "type_info": EVENT_TYPES.get(event_type, EVENT_TYPES["interview"]),
            "full_event_id": event_id,
        }
    
    except Exception as e:
        print(f"[Calendar] Error creating event: {e}")
        raise


def delete_event(event_id: str) -> bool:
    """
    Delete an event by ID from Google Calendar.
    
    Args:
        event_id: The event ID (can be short or full ID)
    
    Returns:
        bool: True if deleted successfully
    """
    try:
        svc = get_calendar_service()
        
        # If we have a short ID, we need to find the full ID
        if len(event_id) <= 8:
            all_events = get_all_events()
            for ev in all_events:
                if ev.get("id") == event_id:
                    event_id = ev.get("full_event_id", event_id)
                    break
        
        svc.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        print(f"[Calendar] Event deleted: {event_id}")
        return True
    
    except Exception as e:
        print(f"[Calendar] Error deleting event: {e}")
        return False


def schedule_interview(
    candidate: dict,
    datetime_str: str,
    role: str,
    duration_minutes: int = 60,
    meeting_link: str = ""
) -> dict:
    """
    Schedule an interview using the smart scheduler.
    This is the main function called from the email agent flow.
    
    Args:
        candidate: dict with 'name' and 'email'
        datetime_str: Preferred datetime (can be used to guide slot search)
        role: Job role
        duration_minutes: Interview duration
        meeting_link: Optional meeting link
    
    Returns:
        dict with status, event_id, event_link, and message
    """
    try:
        candidate_name = candidate.get("name", "")
        candidate_email = candidate.get("email", "")
        
        # If datetime_str is provided and specific, use it directly
        if datetime_str and "T" in datetime_str:
            # Direct scheduling with specified time
            title = f"Interview: {candidate_name} — {role}"
            notes = f"Role: {role}\nEmail: {candidate_email}"
            if meeting_link:
                notes += f"\nMeeting: {meeting_link}"
            
            event = add_event(
                title=title,
                datetime_str=datetime_str,
                event_type="interview",
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                notes=notes,
                duration_minutes=duration_minutes,
            )
            
            return {
                "status": "created",
                "event_id": event["id"],
                "event_link": f"https://calendar.google.com/calendar/event?eid={event['full_event_id']}",
                "message": f"Interview scheduled for {candidate_name} on {datetime_str}",
                "full_event": event
            }
        
        else:
            # Use smart scheduler to find available slots
            svc = get_calendar_service()
            interviewer_city = "India"  # Default to India/IST
            
            # Find 3 available slots
            slots = find_available_slots(
                svc=svc,
                interviewer_city=interviewer_city,
                days_ahead=7,
                num_slots=3,
            )
            
            if not slots:
                return {
                    "status": "no_slots",
                    "message": "No available slots found in the next 7 days. Calendar is fully booked."
                }
            
            # Auto-book the first available slot
            chosen_slot = slots[0]
            
            notes = f"Role: {role}\nEmail: {candidate_email}"
            if meeting_link:
                notes += f"\nMeeting: {meeting_link}"
            
            result = book_slot(
                svc=svc,
                slot=chosen_slot,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_role=role,
                interviewer_name="HR Team",
                notes=notes,
            )
            
            if result["success"]:
                return {
                    "status": "created",
                    "event_id": result["event_id"][:8],
                    "event_link": result["event_link"],
                    "message": f"Interview scheduled for {candidate_name} on {chosen_slot['date_str']} at {chosen_slot['display']}",
                    "slot_info": chosen_slot
                }
            else:
                return {
                    "status": "error",
                    "message": result["message"]
                }
    
    except Exception as e:
        print(f"[Calendar] Error scheduling interview: {e}")
        return {
            "status": "error",
            "event_id": "",
            "event_link": "",
            "message": f"Failed to schedule interview: {str(e)}"
        }

def auto_schedule_interviews(
    candidates: list[dict],
    role: str,
    duration_minutes: int = 45,
    max_per_day: int = 4
) -> dict:
    """
    Auto-schedule non-overlapping interviews for all shortlisted candidates.
    Uses the smart scheduler to find contiguous or next available slots.
    
    Args:
        candidates: List of candidate dictionaries containing 'name' and 'email'
        role: The job role
        duration_minutes: Duration of each interview (default 45 mins)
        max_per_day: Maximum allowed interviews per day
    """
    print(f"[Calendar] Auto-scheduling {len(candidates)} candidates for {role}...")
    try:
        svc = get_calendar_service()
        
        # Get a larger pool of available slots to ensure we can accommodate all candidates
        # We request len(candidates) * 2 to be safe
        slots = find_available_slots(
            svc=svc,
            interviewer_city="India",
            days_ahead=14,
            num_slots=max(len(candidates) * 2, 10),
        )
        
        if len(slots) < len(candidates):
            return {
                "status": "error",
                "message": f"Only found {len(slots)} slots, but need {len(candidates)}. Please manually clear your calendar."
            }

        results = []
        booked_count = 0
        
        for candidate in candidates:
            # Pop the first available slot that hasn't been used
            chosen_slot = slots.pop(0)
            
            c_name = candidate.get("name", "Unknown Candidate")
            c_email = candidate.get("email", "")
            
            notes = f"Auto-scheduled Interview\nRole: {role}\nEmail: {c_email}"
            
            res = book_slot(
                svc=svc,
                slot=chosen_slot,
                candidate_name=c_name,
                candidate_email=c_email,
                job_role=role,
                interviewer_name="HR Team",
                notes=notes,
            )
            
            if res["success"]:
                results.append({
                    "candidate_name": c_name,
                    "status": "created",
                    "event_link": res["event_link"],
                    "time": f"{chosen_slot['date_str']} at {chosen_slot['display']}"
                })
                booked_count += 1
            else:
                results.append({
                    "candidate_name": c_name,
                    "status": "error",
                    "error": res.get("message", "Unknown error")
                })

        return {
            "status": "success",
            "message": f"Successfully auto-scheduled {booked_count} out of {len(candidates)} candidates.",
            "details": results
        }
    
    except Exception as e:
        print(f"[Calendar] Auto-schedule error: {e}")
        return {
            "status": "error",
            "message": f"Failed to run auto-scheduler: {str(e)}"
        }
