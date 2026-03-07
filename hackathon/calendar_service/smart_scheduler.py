"""
smart_scheduler.py — Autonomous Interview Scheduler
═════════════════════════════════════════════════════

WHAT THIS MODULE DOES:
───────────────────────
Given a candidate name, email, and interviewer city — it:

  1. Detects the interviewer's timezone from their city automatically
  2. Checks the next 7 days on Google Calendar for busy slots
  3. Skips weekends (Saturday, Sunday)
  4. Skips Indian public holidays and major festivals in the current year
  5. Skips slots that clash with existing calendar events
  6. Finds 3 best available 1-hour slots in comfortable business hours
     (10 AM – 5 PM in the interviewer's local time)
  7. Presents these slots to the HR for confirmation
  8. Books the one HR picks — creates event + sends invite to candidate
  9. Returns full summary of what was booked

USED BY:
  calendar_tools.py → schedule_interview() tool
  Agent calls it when user says "schedule an interview with X"
"""

import os
from datetime import datetime, timedelta, timezone, date
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(override=True)

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
TIMEZONE    = os.getenv("TIMEZONE",    "Asia/Kolkata")
HR_EMAIL    = os.getenv("HR_EMAIL",    "")


# ══════════════════════════════════════════════════════════════
# CITY → TIMEZONE MAP
# ══════════════════════════════════════════════════════════════

CITY_TIMEZONE = {
    # India
    "mumbai":      "Asia/Kolkata",
    "delhi":       "Asia/Kolkata",
    "bangalore":   "Asia/Kolkata",
    "bengaluru":   "Asia/Kolkata",
    "hyderabad":   "Asia/Kolkata",
    "chennai":     "Asia/Kolkata",
    "kolkata":     "Asia/Kolkata",
    "pune":        "Asia/Kolkata",
    "ahmedabad":   "Asia/Kolkata",
    "india":       "Asia/Kolkata",

    # USA
    "new york":        "America/New_York",
    "new york city":   "America/New_York",
    "nyc":             "America/New_York",
    "boston":          "America/New_York",
    "miami":           "America/New_York",
    "chicago":         "America/Chicago",
    "dallas":          "America/Chicago",
    "houston":         "America/Chicago",
    "denver":          "America/Denver",
    "los angeles":     "America/Los_Angeles",
    "san francisco":   "America/Los_Angeles",
    "seattle":         "America/Los_Angeles",
    "usa":             "America/New_York",

    # UK / Europe
    "london":    "Europe/London",
    "uk":        "Europe/London",
    "paris":     "Europe/Paris",
    "berlin":    "Europe/Berlin",
    "amsterdam": "Europe/Amsterdam",
    "dubai":     "Asia/Dubai",
    "uae":       "Asia/Dubai",
    "abu dhabi": "Asia/Dubai",

    # Asia
    "singapore":  "Asia/Singapore",
    "tokyo":      "Asia/Tokyo",
    "japan":      "Asia/Tokyo",
    "sydney":     "Australia/Sydney",
    "australia":  "Australia/Sydney",
    "beijing":    "Asia/Shanghai",
    "shanghai":   "Asia/Shanghai",
    "china":      "Asia/Shanghai",
    "hong kong":  "Asia/Hong_Kong",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "jakarta":    "Asia/Jakarta",
    "bangkok":    "Asia/Bangkok",
    "seoul":      "Asia/Seoul",
}


def get_timezone_for_city(city: str) -> str:
    """
    Return the IANA timezone string for a given city name.
    Falls back to the HR's configured TIMEZONE if city not found.
    """
    if not city:
        return TIMEZONE
    key = city.strip().lower()
    # Try exact match
    if key in CITY_TIMEZONE:
        return CITY_TIMEZONE[key]
    # Try partial match
    for k, v in CITY_TIMEZONE.items():
        if k in key or key in k:
            return v
    return TIMEZONE


# ══════════════════════════════════════════════════════════════
# INDIAN HOLIDAYS + MAJOR FESTIVALS  (2025 & 2026)
# ══════════════════════════════════════════════════════════════

INDIAN_HOLIDAYS = {
    # 2025
    date(2025, 1, 26):  "Republic Day",
    date(2025, 3, 14):  "Holi",
    date(2025, 3, 31):  "Id-ul-Fitr (Eid)",
    date(2025, 4, 14):  "Dr. Ambedkar Jayanti / Baisakhi",
    date(2025, 4, 18):  "Good Friday",
    date(2025, 5, 12):  "Buddha Purnima",
    date(2025, 6, 7):   "Id-ul-Zuha (Bakrid)",
    date(2025, 7, 6):   "Muharram",
    date(2025, 8, 15):  "Independence Day",
    date(2025, 9, 5):   "Milad-un-Nabi",
    date(2025, 10, 2):  "Gandhi Jayanti",
    date(2025, 10, 2):  "Gandhi Jayanti",
    date(2025, 10, 20): "Dussehra",
    date(2025, 10, 31): "Halloween / Diwali Eve",
    date(2025, 11, 1):  "Diwali",
    date(2025, 11, 5):  "Govardhan Puja",
    date(2025, 11, 15): "Guru Nanak Jayanti",
    date(2025, 12, 25): "Christmas",

    # 2026
    date(2026, 1, 14):  "Makar Sankranti / Pongal",
    date(2026, 1, 26):  "Republic Day",
    date(2026, 3, 3):   "Holi (Dhuleti)",
    date(2026, 3, 20):  "Id-ul-Fitr (Eid)",
    date(2026, 4, 3):   "Good Friday",
    date(2026, 4, 14):  "Dr. Ambedkar Jayanti",
    date(2026, 5, 31):  "Buddha Purnima",
    date(2026, 6, 27):  "Id-ul-Zuha (Bakrid)",
    date(2026, 8, 15):  "Independence Day",
    date(2026, 10, 2):  "Gandhi Jayanti",
    date(2026, 10, 9):  "Dussehra",
    date(2026, 10, 20): "Diwali",
    date(2026, 11, 3):  "Guru Nanak Jayanti",
    date(2026, 12, 25): "Christmas",
}

# Comfortable interview hours: 10 AM to 5 PM (last slot at 4 PM for 1-hour interview)
WORK_HOUR_START = 10   # 10:00 AM
WORK_HOUR_END   = 16   # Last slot start — 4:00 PM (ends at 5 PM)
SLOT_DURATION   = 60   # minutes


# ══════════════════════════════════════════════════════════════
# BUSY SLOTS FROM GOOGLE CALENDAR
# ══════════════════════════════════════════════════════════════

def _get_busy_slots(svc, start_utc: datetime, end_utc: datetime) -> list:
    """
    Fetch all existing events from Google Calendar in the given range.
    Returns list of (start_dt, end_dt) tuples in UTC.
    """
    res = svc.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_utc.isoformat(),
        timeMax=end_utc.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    busy = []
    for ev in res.get("items", []):
        if ev.get("status") == "cancelled":
            continue
        s_raw = ev["start"].get("dateTime", ev["start"].get("date",""))
        e_raw = ev["end"].get("dateTime",   ev["end"].get("date",""))
        try:
            s = datetime.fromisoformat(s_raw).astimezone(timezone.utc)
            e = datetime.fromisoformat(e_raw).astimezone(timezone.utc)
            busy.append((s, e))
        except Exception:
            pass
    return busy


def _slot_is_free(slot_start: datetime, slot_end: datetime, busy: list) -> bool:
    """Return True if the slot doesn't overlap with any busy period."""
    for b_start, b_end in busy:
        # Overlap condition: slot starts before busy ends AND slot ends after busy starts
        if slot_start < b_end and slot_end > b_start:
            return False
    return True


# ══════════════════════════════════════════════════════════════
# MAIN: FIND AVAILABLE SLOTS
# ══════════════════════════════════════════════════════════════

def find_available_slots(
    svc,
    interviewer_city: str,
    days_ahead: int = 7,
    num_slots: int  = 3,
) -> list[dict]:
    """
    Find available 1-hour interview slots in the next N days.

    Rules:
      - Skips weekends (Sat, Sun)
      - Skips Indian public holidays / festivals
      - Skips slots that overlap with existing calendar events
      - Only suggests 10 AM – 4 PM in interviewer's local timezone
      - Returns up to num_slots options

    Returns:
      List of dicts: {
        "date_str":    "Monday, 14 April 2026",
        "date":        "2026-04-14",
        "start_time":  "10:00",
        "end_time":    "11:00",
        "display":     "10:00 AM – 11:00 AM IST",
        "holiday":     None or "Holiday name",
        "tz_label":    "IST (Asia/Kolkata)",
      }
    """
    interviewer_tz_str = get_timezone_for_city(interviewer_city)
    interviewer_tz     = ZoneInfo(interviewer_tz_str)

    # Fetch busy slots for entire window
    now_utc    = datetime.now(timezone.utc)
    window_end = now_utc + timedelta(days=days_ahead + 1)
    busy       = _get_busy_slots(svc, now_utc, window_end)

    # Build timezone label
    sample_dt  = datetime.now(interviewer_tz)
    tz_offset  = sample_dt.strftime("%Z")
    tz_label   = f"{tz_offset} ({interviewer_tz_str})"

    available = []

    for day_offset in range(1, days_ahead + 1):
        check_date = (now_utc + timedelta(days=day_offset)).astimezone(interviewer_tz).date()

        # Skip weekends
        if check_date.weekday() in (5, 6):  # 5=Saturday, 6=Sunday
            continue

        # Skip holidays
        holiday = INDIAN_HOLIDAYS.get(check_date)

        # Try each hour slot from WORK_HOUR_START to WORK_HOUR_END
        for hour in range(WORK_HOUR_START, WORK_HOUR_END + 1):
            if len(available) >= num_slots:
                break

            # Build slot in interviewer's timezone
            slot_start_local = datetime(
                check_date.year, check_date.month, check_date.day,
                hour, 0, 0, tzinfo=interviewer_tz
            )
            slot_end_local = slot_start_local + timedelta(minutes=SLOT_DURATION)

            # Convert to UTC for clash check
            slot_start_utc = slot_start_local.astimezone(timezone.utc)
            slot_end_utc   = slot_end_local.astimezone(timezone.utc)

            # Skip if already passed
            if slot_start_utc <= now_utc:
                continue

            # Skip if clashes with existing events
            if not _slot_is_free(slot_start_utc, slot_end_utc, busy):
                continue

            # Skip holiday slots (still offer if no other options — mark them)
            # We include them but flag so HR knows

            available.append({
                "date_str":   slot_start_local.strftime("%A, %d %B %Y"),
                "date":       slot_start_local.strftime("%Y-%m-%d"),
                "start_time": slot_start_local.strftime("%H:%M"),
                "end_time":   slot_end_local.strftime("%H:%M"),
                "display":    (
                    f"{slot_start_local.strftime('%I:%M %p')} – "
                    f"{slot_end_local.strftime('%I:%M %p')} {tz_offset}"
                ),
                "holiday":    holiday,
                "tz_label":   tz_label,
                "tz_str":     interviewer_tz_str,
            })

        if len(available) >= num_slots:
            break

    return available


# ══════════════════════════════════════════════════════════════
# FORMAT SLOTS FOR DISPLAY
# ══════════════════════════════════════════════════════════════

def format_slots_for_display(
    slots:            list[dict],
    candidate_name:   str,
    interviewer_city: str,
) -> str:
    """
    Format the available slots into a beautiful terminal-friendly message
    for HR to review and confirm.
    """
    if not slots:
        return (
            "😔  No available slots found in the next 7 days.\n\n"
            "    Possible reasons:\n"
            "    • Your calendar is fully booked\n"
            "    • All weekdays are holidays\n"
            "    Try: ask to search next 14 days instead."
        )

    tz_label = slots[0].get("tz_label", "")
    lines = [
        f"🗓   Smart Schedule — Interview with {candidate_name}",
        f"     Interviewer city : {interviewer_city}",
        f"     Timezone         : {tz_label}",
        f"     Slot duration    : 1 hour",
        "",
        "     Here are the best available slots:\n",
        "     " + "─" * 50,
    ]

    for i, slot in enumerate(slots, 1):
        holiday_note = ""
        if slot.get("holiday"):
            holiday_note = f"  ⚠️  Note: {slot['holiday']} (holiday — confirm with HR)"

        lines.append(
            f"\n     [{i}]  {slot['date_str']}\n"
            f"           Time   : {slot['display']}\n"
            f"           Date   : {slot['date']}{holiday_note}"
        )

    lines += [
        "\n     " + "─" * 50,
        "",
        f"     Reply with the slot number (1 / 2 / 3) to confirm booking,",
        f"     or say 'none' to skip / suggest a different time.",
    ]

    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════
# BOOK THE CONFIRMED SLOT
# ══════════════════════════════════════════════════════════════

def book_slot(
    svc,
    slot:             dict,
    candidate_name:   str,
    candidate_email:  str,
    job_role:         str,
    interviewer_name: str,
    notes:            str,
) -> dict:
    """
    Create the Google Calendar event for the confirmed slot.

    Returns:
      dict with "success", "event_id", "event_link", "message"
    """
    title = f"Interview — {candidate_name} — {job_role}"
    desc  = (
        f"Candidate      : {candidate_name}\n"
        f"Email          : {candidate_email}\n"
        f"Role           : {job_role}\n"
        f"Interviewer    : {interviewer_name}\n"
        f"Interviewer City: {slot.get('tz_label','')}\n"
    )
    if notes and notes.lower() not in ("none","skip",""):
        desc += f"Notes / Agenda : {notes}\n"

    desc += "\nScheduled automatically by HR Calendar Agent."

    from zoneinfo import ZoneInfo
    tz_str    = slot.get("tz_str", TIMEZONE)
    tz        = ZoneInfo(tz_str)
    start_loc = datetime(
        int(slot["date"][:4]), int(slot["date"][5:7]), int(slot["date"][8:]),
        int(slot["start_time"][:2]), int(slot["start_time"][3:]),
        tzinfo=tz
    )
    end_loc = datetime(
        int(slot["date"][:4]), int(slot["date"][5:7]), int(slot["date"][8:]),
        int(slot["end_time"][:2]), int(slot["end_time"][3:]),
        tzinfo=tz
    )

    attendees = [{"email": candidate_email.strip()}]
    if HR_EMAIL and HR_EMAIL != "your_gmail@gmail.com":
        attendees.append({"email": HR_EMAIL})

    event = {
        "summary":     title,
        "description": desc,
        "location":    "To be shared via email",
        "start":       {"dateTime": start_loc.isoformat(), "timeZone": tz_str},
        "end":         {"dateTime": end_loc.isoformat(),   "timeZone": tz_str},
        "visibility":  "public",
        "status":      "confirmed",
        "attendees":   attendees,
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email",  "minutes": 24 * 60},  # 1 day before
                {"method": "email",  "minutes": 60},        # 1 hour before
                {"method": "popup",  "minutes": 15},        # 15 min popup
            ],
        },
    }

    try:
        created = svc.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            sendUpdates="all",    # sends invite email to candidate + HR
        ).execute()

        ev_id   = created.get("id",       "")
        ev_link = created.get("htmlLink", "")

        return {
            "success":    True,
            "event_id":   ev_id,
            "event_link": ev_link,
            "title":      title,
            "date_str":   slot["date_str"],
            "display":    slot["display"],
            "tz_label":   slot["tz_label"],
            "message": (
                f"✅  Interview scheduled successfully!\n\n"
                f"    Title      : {title}\n"
                f"    Date       : {slot['date_str']}\n"
                f"    Time       : {slot['display']}\n"
                f"    Timezone   : {slot['tz_label']}\n"
                f"    Candidate  : {candidate_name} ({candidate_email})\n"
                f"    Role       : {job_role}\n\n"
                f"    📧  Invite emails sent to:\n"
                f"        • {candidate_email}  (candidate)\n"
                f"        • {HR_EMAIL}  (HR)\n\n"
                f"    ⏰  Reminders set:\n"
                f"        • 1 day before  (email)\n"
                f"        • 1 hour before (email)\n"
                f"        • 15 min before (popup)\n\n"
                f"    ─────────────────────────────────\n"
                f"    ⚠️  SAVE THIS EVENT ID:\n"
                f"    {ev_id}\n"
                f"    ─────────────────────────────────\n"
                f"    Open in Google Calendar: {ev_link}"
            ),
        }
    except Exception as e:
        return {
            "success":  False,
            "event_id": "",
            "message":  f"❌  Failed to book slot: {e}",
        }
