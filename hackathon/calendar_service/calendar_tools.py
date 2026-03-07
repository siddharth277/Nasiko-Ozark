"""
calendar_tools.py — HR Calendar Agent Tools
─────────────────────────────────────────────
Tools:
  1. create_event         — Create a calendar event manually
  2. list_events          — List upcoming events
  3. get_event            — Full details of one event
  4. update_event         — Edit / reschedule an event
  5. delete_event         — Delete / cancel an event
  6. search_events        — Search events by keyword
  7. list_calendars       — List all Google Calendars
  8. send_day_reminders   — Send day-of reminder emails to HR + attendees
  9. find_interview_slots — NEW: Find available interview slots (smart)
  10. book_interview_slot — NEW: Book a confirmed slot after HR picks it
"""

import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from langchain_core.tools import tool
from .auth import get_calendar_service

load_dotenv(override=True)

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
TIMEZONE    = os.getenv("TIMEZONE",    "Asia/Kolkata")
HR_EMAIL    = os.getenv("HR_EMAIL",    "")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_iso(date: str, time: str) -> str:
    try:
        tz       = ZoneInfo(TIMEZONE)
        local_dt = datetime.fromisoformat(f"{date}T{time}:00").replace(tzinfo=tz)
        return local_dt.isoformat()
    except Exception:
        return f"{date}T{time}:00"


def _fmt_dt(raw: str) -> str:
    try:
        if "T" in raw:
            dt = datetime.fromisoformat(raw)
            return dt.strftime("%d %b %Y  %I:%M %p")
        else:
            dt = datetime.strptime(raw, "%Y-%m-%d")
            return dt.strftime("%d %b %Y  (all day)")
    except Exception:
        return raw


# ══════════════════════════════════════════════════════════════
# 1. CREATE EVENT (manual)
# ══════════════════════════════════════════════════════════════

@tool
def create_event(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    description: str,
    attendee_email: str,
    location: str,
) -> str:
    """
    Create a new Google Calendar event manually.

    Ask the user for ALL fields before calling:
      title          : event title
      date           : YYYY-MM-DD
      start_time     : HH:MM 24-hour
      end_time       : HH:MM 24-hour
      description    : notes — use "none" if skipped
      attendee_email : email to invite — use "none" if nobody
      location       : place — use "none" if not mentioned

    After creating, show the event_id prominently.
    For interviews, prefer using find_interview_slots + book_interview_slot
    instead of this manual create_event.
    """
    try:
        svc = get_calendar_service()

        start_iso = _to_utc_iso(date, start_time)
        end_iso   = _to_utc_iso(date, end_time)

        event = {
            "summary":     title,
            "description": "" if description.lower() in ("none","skip","") else description,
            "location":    "" if location.lower()    in ("none","skip","") else location,
            "start":       {"dateTime": start_iso, "timeZone": TIMEZONE},
            "end":         {"dateTime": end_iso,   "timeZone": TIMEZONE},
            "visibility":  "public",
            "status":      "confirmed",
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email",  "minutes": 60},
                    {"method": "popup",  "minutes": 15},
                ],
            },
        }

        has_attendee = attendee_email.lower() not in ("none","skip","","no","n/a")
        if has_attendee:
            event["attendees"] = [{"email": attendee_email.strip()}]

        created = svc.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            sendUpdates="all" if has_attendee else "none",
        ).execute()

        ev_id   = created.get("id",       "")
        ev_link = created.get("htmlLink", "")

        msg = (
            f"✅  Event created!\n\n"
            f"    Title    : {title}\n"
            f"    Date     : {date}\n"
            f"    Time     : {start_time} → {end_time}  ({TIMEZONE})\n"
            f"    Location : {location if location.lower() not in ('none','skip','') else '—'}\n"
            f"    Attendee : {attendee_email if has_attendee else '—'}\n\n"
            f"    ─────────────────────────────────\n"
            f"    ⚠️  SAVE THIS EVENT ID:\n"
            f"    {ev_id}\n"
            f"    ─────────────────────────────────\n"
            f"    Link: {ev_link}"
        )
        return msg

    except Exception as e:
        return f"❌  create_event failed: {e}"


# ══════════════════════════════════════════════════════════════
# 2. LIST EVENTS
# ══════════════════════════════════════════════════════════════

@tool
def list_events(days_ahead: int) -> str:
    """
    List upcoming Google Calendar events.
    Ask: "How many days ahead?" — 1=today, 7=week, 30=month.
    """
    try:
        svc     = get_calendar_service()
        now_utc = _now_utc()
        t_start = now_utc - timedelta(hours=1)
        t_end   = now_utc + timedelta(days=max(days_ahead, 1))

        res = svc.events().list(
            calendarId=CALENDAR_ID,
            timeMin=t_start.isoformat(),
            timeMax=t_end.isoformat(),
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = res.get("items", [])
        if not events:
            return f"📅  No events in the next {days_ahead} day(s). Try 'next 60 days'."

        lines = [f"📅  {len(events)} event(s) — next {days_ahead} day(s):\n", "─"*55]
        for i, ev in enumerate(events, 1):
            start_raw = ev["start"].get("dateTime", ev["start"].get("date","?"))
            end_raw   = ev["end"].get("dateTime",   ev["end"].get("date","?"))
            title     = ev.get("summary",  "Untitled")
            ev_id     = ev.get("id",       "")
            location  = ev.get("location", "")
            attendees = ", ".join(a.get("email","") for a in ev.get("attendees",[]))

            lines.append(f"\n  [{i}]  {title}")
            lines.append(f"        Start    : {_fmt_dt(start_raw)}")
            lines.append(f"        End      : {_fmt_dt(end_raw)}")
            lines.append(f"        Event ID : {ev_id}")
            if location:  lines.append(f"        Location : {location}")
            if attendees: lines.append(f"        Attendees: {attendees}")

        lines.append("\n" + "─"*55)
        return "\n".join(lines)

    except Exception as e:
        return f"❌  list_events failed: {e}"


# ══════════════════════════════════════════════════════════════
# 3. GET EVENT
# ══════════════════════════════════════════════════════════════

@tool
def get_event(event_id: str) -> str:
    """Get full details of one event. Ask for event_id first."""
    try:
        svc = get_calendar_service()
        ev  = svc.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        title     = ev.get("summary",    "Untitled")
        start_raw = ev["start"].get("dateTime", ev["start"].get("date","?"))
        end_raw   = ev["end"].get("dateTime",   ev["end"].get("date","?"))
        desc      = ev.get("description","")
        location  = ev.get("location",  "")
        status    = ev.get("status",    "")
        link      = ev.get("htmlLink",  "")
        attendees = ev.get("attendees", [])

        lines = [
            f"\n📌  Event Details", "─"*50,
            f"  Title    : {title}",
            f"  Start    : {_fmt_dt(start_raw)}",
            f"  End      : {_fmt_dt(end_raw)}",
            f"  Location : {location or '—'}",
            f"  Status   : {status}",
            f"  Event ID : {event_id}",
            f"  Link     : {link}",
        ]
        if desc:
            lines.append(f"  Notes    : {desc}")
        if attendees:
            lines.append(f"\n  Attendees ({len(attendees)}):")
            for a in attendees:
                lines.append(f"    •  {a.get('email','')}  [RSVP: {a.get('responseStatus','?')}]")
        return "\n".join(lines)

    except Exception as e:
        return f"❌  get_event failed: {e}"


# ══════════════════════════════════════════════════════════════
# 4. UPDATE EVENT
# ══════════════════════════════════════════════════════════════

@tool
def update_event(
    event_id: str,
    new_title: str,
    new_date: str,
    new_start_time: str,
    new_end_time: str,
    new_description: str,
    new_location: str,
) -> str:
    """
    Update an existing event. Use "skip" for unchanged fields.
    Ask for event_id first.
    """
    try:
        svc = get_calendar_service()
        ev  = svc.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        if new_title.lower()       != "skip": ev["summary"]     = new_title
        if new_description.lower() != "skip": ev["description"] = new_description
        if new_location.lower()    != "skip": ev["location"]    = new_location

        if any(x.lower() != "skip" for x in [new_date, new_start_time, new_end_time]):
            try:
                tz       = ZoneInfo(TIMEZONE)
                ds_local = datetime.fromisoformat(ev["start"]["dateTime"]).astimezone(tz)
                de_local = datetime.fromisoformat(ev["end"]["dateTime"]).astimezone(tz)
                cur_d    = ds_local.strftime("%Y-%m-%d")
                cur_st   = ds_local.strftime("%H:%M")
                cur_et   = de_local.strftime("%H:%M")
            except Exception:
                cur_d, cur_st, cur_et = "2025-01-01", "09:00", "10:00"

            nd  = new_date       if new_date.lower()       != "skip" else cur_d
            nst = new_start_time if new_start_time.lower() != "skip" else cur_st
            net = new_end_time   if new_end_time.lower()   != "skip" else cur_et

            ev["start"] = {"dateTime": _to_utc_iso(nd, nst), "timeZone": TIMEZONE}
            ev["end"]   = {"dateTime": _to_utc_iso(nd, net), "timeZone": TIMEZONE}

        updated = svc.events().update(
            calendarId=CALENDAR_ID, eventId=event_id,
            body=ev, sendUpdates="all",
        ).execute()

        return (
            f"✅  Event updated!\n"
            f"    Title : {updated.get('summary','')}\n"
            f"    Start : {_fmt_dt(updated['start'].get('dateTime',''))}\n"
            f"    End   : {_fmt_dt(updated['end'].get('dateTime',''))}\n"
            f"    Link  : {updated.get('htmlLink','')}"
        )
    except Exception as e:
        return f"❌  update_event failed: {e}"


# ══════════════════════════════════════════════════════════════
# 5. DELETE EVENT
# ══════════════════════════════════════════════════════════════

@tool
def delete_event(event_id: str, notify_attendees: bool) -> str:
    """
    Delete a calendar event. ALWAYS confirm with user before calling.
    Ask: "Are you sure? (yes/no)"
    """
    try:
        svc = get_calendar_service()
        try:
            ev    = svc.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
            title = ev.get("summary","Untitled")
        except Exception:
            title = event_id

        svc.events().delete(
            calendarId=CALENDAR_ID, eventId=event_id,
            sendUpdates="all" if notify_attendees else "none",
        ).execute()

        note = "Attendees notified." if notify_attendees else "No notification sent."
        return f"✅  '{title}' deleted.\n    {note}"

    except Exception as e:
        return f"❌  delete_event failed: {e}"


# ══════════════════════════════════════════════════════════════
# 6. SEARCH EVENTS
# ══════════════════════════════════════════════════════════════

@tool
def search_events(keyword: str, days_ahead: int) -> str:
    """Search events by keyword. Ask for keyword and days to search."""
    try:
        svc     = get_calendar_service()
        now_utc = _now_utc()

        res = svc.events().list(
            calendarId=CALENDAR_ID,
            q=keyword,
            timeMin=(now_utc - timedelta(days=7)).isoformat(),
            timeMax=(now_utc + timedelta(days=days_ahead)).isoformat(),
            maxResults=20, singleEvents=True, orderBy="startTime",
        ).execute()

        events = res.get("items", [])
        if not events:
            return f"🔎  No events matching '{keyword}' in next {days_ahead} days."

        lines = [f"🔎  {len(events)} event(s) matching '{keyword}':\n"]
        for i, ev in enumerate(events, 1):
            start_raw = ev["start"].get("dateTime", ev["start"].get("date","?"))
            lines.append(f"  [{i}]  {ev.get('summary','Untitled')}")
            lines.append(f"        When     : {_fmt_dt(start_raw)}")
            lines.append(f"        Event ID : {ev.get('id','')}\n")
        return "\n".join(lines)

    except Exception as e:
        return f"❌  search_events failed: {e}"


# ══════════════════════════════════════════════════════════════
# 7. LIST CALENDARS
# ══════════════════════════════════════════════════════════════

@tool
def list_calendars() -> str:
    """List all Google Calendars. No input needed."""
    try:
        svc  = get_calendar_service()
        cals = svc.calendarList().list().execute().get("items", [])
        if not cals:
            return "📅  No calendars found."
        lines = [f"📅  Your Google Calendars ({len(cals)}):\n"]
        for cal in cals:
            name     = cal.get("summary", "Unnamed")
            cal_id   = cal.get("id", "")
            primary  = "  ← PRIMARY" if cal.get("primary") else ""
            selected = "  ← ✅ IN USE" if cal_id == CALENDAR_ID else ""
            lines.append(f"  •  {name}{primary}{selected}")
            lines.append(f"     ID: {cal_id}\n")
        return "\n".join(lines)
    except Exception as e:
        return f"❌  list_calendars failed: {e}"


# ══════════════════════════════════════════════════════════════
# 8. SEND DAY-OF REMINDERS
# ══════════════════════════════════════════════════════════════

@tool
def send_day_reminders() -> str:
    """
    Send day-of reminder emails to HR + all attendees for today's events.
    Call when user says "send reminders for today" or similar.
    No input needed.
    """
    try:
        from .reminder_service import send_reminders_for_today
        return send_reminders_for_today()
    except ImportError:
        return "❌  reminder_service.py not found in this folder!"
    except Exception as e:
        return f"❌  send_day_reminders failed: {e}"


# ══════════════════════════════════════════════════════════════
# 9. FIND INTERVIEW SLOTS  ← NEW
# ══════════════════════════════════════════════════════════════

@tool
def find_interview_slots(
    candidate_name:   str,
    candidate_email:  str,
    job_role:         str,
    interviewer_city: str,
) -> str:
    """
    Autonomously find the best available interview slots in the next 7 days.

    Call this when user wants to schedule an interview.
    Collect from user before calling:
      candidate_name   : full name of the candidate
      candidate_email  : candidate's email address
      job_role         : position they're interviewing for, e.g. "Software Engineer"
      interviewer_city : city/country of the interviewer, e.g. "Mumbai", "London"
                         (used to show times in their local timezone)

    This tool will:
      - Check your Google Calendar for busy slots
      - Skip weekends and Indian public holidays / festivals
      - Find 3 best 1-hour slots in comfortable business hours (10 AM – 4 PM local)
      - Show them clearly with timezone info
      - Ask HR to confirm which slot to book

    After showing slots, wait for user to reply with "1", "2", or "3"
    then call book_interview_slot with the chosen slot number.

    IMPORTANT: Store the slots result in conversation context so
    book_interview_slot can reference it.
    """
    try:
        from .smart_scheduler import find_available_slots, format_slots_for_display
        svc   = get_calendar_service()
        slots = find_available_slots(
            svc=svc,
            interviewer_city=interviewer_city,
            days_ahead=7,
            num_slots=3,
        )

        display = format_slots_for_display(slots, candidate_name, interviewer_city)

        # Encode slots data compactly so agent can pass to book_interview_slot
        import json
        slots_json = json.dumps(slots)

        return (
            f"{display}\n\n"
            f"SLOTS_DATA:{slots_json}"   # agent picks this up from context
        )

    except Exception as e:
        return f"❌  find_interview_slots failed: {e}"


# ══════════════════════════════════════════════════════════════
# 10. BOOK INTERVIEW SLOT  ← NEW
# ══════════════════════════════════════════════════════════════

@tool
def book_interview_slot(
    slot_number:      int,
    candidate_name:   str,
    candidate_email:  str,
    job_role:         str,
    interviewer_name: str,
    notes:            str,
    slots_data:       str,
) -> str:
    """
    Book the interview slot that HR confirmed.

    Call this AFTER find_interview_slots, once HR has chosen a slot.

    Parameters:
      slot_number      : 1, 2, or 3 — which slot HR picked
      candidate_name   : candidate's full name
      candidate_email  : candidate's email
      job_role         : job position
      interviewer_name : HR/interviewer's name (ask if not given)
      notes            : any agenda/notes — use "none" if not mentioned
      slots_data       : the SLOTS_DATA JSON string from find_interview_slots output
                         (copy it exactly from the previous tool response)

    This will:
      - Create the Google Calendar event
      - Send invite emails to candidate AND HR
      - Set reminders: 1 day before, 1 hour before, 15 min popup
      - Return confirmation with event ID
    """
    try:
        import json
        from .smart_scheduler import book_slot
        from .auth import get_calendar_service as _get_svc

        # Parse slots
        try:
            slots = json.loads(slots_data)
        except Exception:
            return (
                "❌  Could not parse slot data.\n"
                "    Please run 'find interview slots' again first."
            )

        idx = slot_number - 1
        if idx < 0 or idx >= len(slots):
            return (
                f"❌  Slot {slot_number} is not valid.\n"
                f"    Available slots: 1 to {len(slots)}"
            )

        chosen_slot = slots[idx]
        svc         = _get_svc()

        result = book_slot(
            svc=svc,
            slot=chosen_slot,
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            job_role=job_role,
            interviewer_name=interviewer_name,
            notes=notes,
        )

        return result["message"]

    except Exception as e:
        return f"❌  book_interview_slot failed: {e}"


# ── All tools ─────────────────────────────────────────────────
ALL_TOOLS = [
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
]
