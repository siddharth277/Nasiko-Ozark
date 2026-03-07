"""
reminder_service.py — Day-of-Event Email Reminder System
══════════════════════════════════════════════════════════

HOW IT WORKS:
─────────────
When you create an event, Google Calendar already sends:
  • A popup reminder  15 minutes before  (to calendar owner)
  • An email reminder 60 minutes before  (to calendar owner)

But the attendee only gets the initial invite — NOT a day-of reminder.

This module adds:
  ✅  A "morning of" email reminder to BOTH the HR (calendar owner)
      AND the attendee — sent at 8:00 AM on the day of the event.
  ✅  Uses Gmail API (same Google account, no extra setup needed)
  ✅  Beautiful HTML email with all event details
  ✅  Works by scanning today's events each morning and sending reminders

TWO WAYS TO USE:
────────────────
  1. Manual trigger (inside agent):
       User says "send reminders for today" → agent calls send_day_reminders()

  2. Automatic (run once every morning):
       python reminder_service.py
       → Finds all events happening today
       → Sends reminder emails to HR + all attendees
       → Schedule this with Windows Task Scheduler to run at 8:00 AM daily

REQUIREMENTS:
─────────────
  • Gmail API must be enabled in your Google Cloud Console
  • token.json must include Gmail scope (delete token.json once, re-login)
  • Add to .env:  HR_EMAIL=your_gmail@gmail.com
"""

import os
import base64
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv(override=True)

# ── Config ────────────────────────────────────────────────────
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE       = os.getenv("TOKEN_FILE",        "token.json")
CALENDAR_ID      = os.getenv("CALENDAR_ID",       "primary")
TIMEZONE         = os.getenv("TIMEZONE",           "Asia/Kolkata")
HR_EMAIL         = os.getenv("HR_EMAIL",           "")

# IMPORTANT: Both scopes needed — Calendar to read events, Gmail to send emails
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]


# ── Auth (supports both scopes) ───────────────────────────────

def get_services():
    """
    Get both Calendar and Gmail API services.
    If token.json was created with only the Calendar scope,
    it will re-authenticate to add Gmail scope automatically.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄  Refreshing token…")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"❌  {CREDENTIALS_FILE} not found.\n"
                    "    Download from Google Cloud Console → credentials.json"
                )
            print("🌐  Opening browser for Google login (adding Gmail permission)…")
            flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅  Login successful!")

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    calendar_svc = build("calendar", "v3", credentials=creds)
    gmail_svc    = build("gmail",    "v1", credentials=creds)
    return calendar_svc, gmail_svc


# ── Email builder ─────────────────────────────────────────────

def _build_email(
    to_email:   str,
    from_email: str,
    role:       str,          # "HR" or "Attendee"
    title:      str,
    date_str:   str,
    start_time: str,
    end_time:   str,
    location:   str,
    description: str,
    other_person: str,        # attendee email if role=HR, HR email if role=Attendee
) -> dict:
    """Build a beautiful HTML reminder email and return it as a Gmail API message dict."""

    role_color  = "#1A56DB" if role == "HR" else "#0B6E4F"
    role_label  = "HR Manager" if role == "HR" else "Meeting Participant"
    other_label = "Attendee"   if role == "HR" else "HR Manager"

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body       {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f5f7fa; margin:0; padding:20px; }}
    .container {{ max-width:580px; margin:0 auto; background:#fff;
                  border-radius:12px; overflow:hidden;
                  box-shadow:0 2px 12px rgba(0,0,0,0.10); }}
    .header    {{ background:{role_color}; padding:28px 32px; }}
    .header h1 {{ color:#fff; margin:0; font-size:22px; font-weight:700; }}
    .header p  {{ color:rgba(255,255,255,0.85); margin:6px 0 0; font-size:14px; }}
    .badge     {{ display:inline-block; background:rgba(255,255,255,0.2);
                  color:#fff; padding:3px 12px; border-radius:20px;
                  font-size:12px; font-weight:600; margin-bottom:10px; }}
    .body      {{ padding:28px 32px; }}
    .row       {{ display:flex; margin-bottom:14px; align-items:flex-start; }}
    .icon      {{ width:36px; height:36px; border-radius:8px; background:#EBF2FF;
                  display:flex; align-items:center; justify-content:center;
                  font-size:18px; flex-shrink:0; margin-right:14px; line-height:36px;
                  text-align:center; }}
    .label     {{ font-size:11px; color:#6B7280; font-weight:600;
                  text-transform:uppercase; letter-spacing:0.5px; }}
    .value     {{ font-size:15px; color:#111827; font-weight:500; margin-top:2px; }}
    .divider   {{ border:none; border-top:1px solid #E5E7EB; margin:20px 0; }}
    .footer    {{ background:#F9FAFB; padding:18px 32px;
                  font-size:12px; color:#9CA3AF; text-align:center; }}
    .reminder-box {{ background:#FEF3C7; border-left:4px solid #F59E0B;
                     border-radius:0 8px 8px 0; padding:12px 16px;
                     margin:18px 0; }}
    .reminder-box p {{ margin:0; color:#92400E; font-size:13px; font-weight:500; }}
  </style>
</head>
<body>
  <div class="container">

    <div class="header">
      <div class="badge">📅 Day-of Reminder</div>
      <h1>You have an event today</h1>
      <p>This is your morning reminder as {role_label}</p>
    </div>

    <div class="body">

      <div class="reminder-box">
        <p>⏰  <strong>{title}</strong> is scheduled for today.
        Please prepare accordingly.</p>
      </div>

      <div class="row">
        <div class="icon">📌</div>
        <div>
          <div class="label">Event</div>
          <div class="value">{title}</div>
        </div>
      </div>

      <div class="row">
        <div class="icon">📆</div>
        <div>
          <div class="label">Date</div>
          <div class="value">{date_str}</div>
        </div>
      </div>

      <div class="row">
        <div class="icon">🕐</div>
        <div>
          <div class="label">Time</div>
          <div class="value">{start_time} → {end_time}  ({TIMEZONE})</div>
        </div>
      </div>

      {"" if not location or location.lower() in ("none","—","") else f'''
      <div class="row">
        <div class="icon">📍</div>
        <div>
          <div class="label">Location</div>
          <div class="value">{location}</div>
        </div>
      </div>
      '''}

      <div class="row">
        <div class="icon">👤</div>
        <div>
          <div class="label">{other_label}</div>
          <div class="value">{other_person if other_person else "—"}</div>
        </div>
      </div>

      {"" if not description or description.lower() in ("none","") else f'''
      <hr class="divider">
      <div class="row">
        <div class="icon">📝</div>
        <div>
          <div class="label">Notes / Agenda</div>
          <div class="value">{description}</div>
        </div>
      </div>
      '''}

    </div>

    <div class="footer">
      This reminder was sent automatically by your Google Calendar Agent.<br>
      Sent to: {to_email} · {role_label}
    </div>

  </div>
</body>
</html>
"""

    # Build plain-text fallback
    plain = (
        f"DAY-OF REMINDER — {title}\n\n"
        f"Date     : {date_str}\n"
        f"Time     : {start_time} → {end_time} ({TIMEZONE})\n"
        f"Location : {location or '—'}\n"
        f"{other_label}: {other_person or '—'}\n"
    )
    if description and description.lower() not in ("none",""):
        plain += f"Notes    : {description}\n"

    # Assemble MIME message
    msg = MIMEMultipart("alternative")
    msg["To"]      = to_email
    msg["From"]    = from_email
    msg["Subject"] = f"⏰ Today's Reminder: {title}"
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    # Encode for Gmail API
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


# ── Core reminder logic ────────────────────────────────────────

def _get_today_events(calendar_svc) -> list:
    """Fetch all events happening today in the configured timezone."""
    tz      = ZoneInfo(TIMEZONE)
    now_utc = datetime.now(timezone.utc)

    # Today's range in local timezone → convert to UTC for API
    today_local = now_utc.astimezone(tz)
    day_start   = today_local.replace(hour=0,  minute=0,  second=0,  microsecond=0)
    day_end     = today_local.replace(hour=23, minute=59, second=59, microsecond=0)

    result = calendar_svc.events().list(
        calendarId=CALENDAR_ID,
        timeMin=day_start.isoformat(),
        timeMax=day_end.isoformat(),
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return result.get("items", [])


def _format_local_time(raw: str) -> tuple[str, str, str]:
    """
    Parse a Google dateTime string and return (date_str, start_str, end_str).
    Returns formatted local-time strings.
    """
    try:
        dt  = datetime.fromisoformat(raw)
        tz  = ZoneInfo(TIMEZONE)
        loc = dt.astimezone(tz)
        return (
            loc.strftime("%A, %d %B %Y"),
            loc.strftime("%I:%M %p"),
            "",
        )
    except Exception:
        return (raw, "", "")


def send_reminders_for_today() -> str:
    """
    Main function: scan today's events and send reminder emails.

    Sends to:
      1. HR (calendar owner) — from HR_EMAIL in .env
      2. Each attendee on the event

    Returns a summary string of what was sent.
    """
    hr_email = HR_EMAIL.strip()
    if not hr_email:
        return (
            "❌  HR_EMAIL not set in .env!\n"
            "    Add this line to your .env file:\n"
            "    HR_EMAIL=your_gmail@gmail.com\n"
            "    (Use the same Gmail account connected to Google Calendar)"
        )

    try:
        calendar_svc, gmail_svc = get_services()
    except Exception as e:
        return f"❌  Could not connect to Google services: {e}"

    events = _get_today_events(calendar_svc)

    if not events:
        return "📅  No events found for today — no reminders sent."

    sent     = []
    skipped  = []
    errors   = []

    for ev in events:
        title       = ev.get("summary",     "Untitled Event")
        description = ev.get("description", "")
        location    = ev.get("location",    "")
        status      = ev.get("status",      "")
        attendees   = ev.get("attendees",   [])

        # Skip cancelled events
        if status == "cancelled":
            skipped.append(f"{title} (cancelled)")
            continue

        # Parse times
        start_raw = ev["start"].get("dateTime", ev["start"].get("date", ""))
        end_raw   = ev["end"].get("dateTime",   ev["end"].get("date",   ""))

        try:
            tz        = ZoneInfo(TIMEZONE)
            start_dt  = datetime.fromisoformat(start_raw).astimezone(tz)
            end_dt    = datetime.fromisoformat(end_raw).astimezone(tz)
            date_str  = start_dt.strftime("%A, %d %B %Y")
            start_str = start_dt.strftime("%I:%M %p")
            end_str   = end_dt.strftime("%I:%M %p")
        except Exception:
            date_str  = start_raw
            start_str = ""
            end_str   = ""

        # Collect attendee emails (exclude the HR/calendar owner)
        attendee_emails = [
            a.get("email", "")
            for a in attendees
            if a.get("email", "").lower() != hr_email.lower()
               and a.get("email", "")
        ]

        # ── Send to HR ────────────────────────────────────────
        try:
            other = attendee_emails[0] if attendee_emails else "No attendees"
            msg   = _build_email(
                to_email     = hr_email,
                from_email   = hr_email,
                role         = "HR",
                title        = title,
                date_str     = date_str,
                start_time   = start_str,
                end_time     = end_str,
                location     = location,
                description  = description,
                other_person = other,
            )
            gmail_svc.users().messages().send(userId="me", body=msg).execute()
            sent.append(f"HR ({hr_email}) ← '{title}'")
        except Exception as e:
            errors.append(f"HR email failed for '{title}': {e}")

        # ── Send to each attendee ─────────────────────────────
        for att_email in attendee_emails:
            try:
                msg = _build_email(
                    to_email     = att_email,
                    from_email   = hr_email,
                    role         = "Attendee",
                    title        = title,
                    date_str     = date_str,
                    start_time   = start_str,
                    end_time     = end_str,
                    location     = location,
                    description  = description,
                    other_person = hr_email,
                )
                gmail_svc.users().messages().send(userId="me", body=msg).execute()
                sent.append(f"Attendee ({att_email}) ← '{title}'")
            except Exception as e:
                errors.append(f"Attendee email failed for '{att_email}': {e}")

    # ── Build summary ─────────────────────────────────────────
    lines = [f"📧  Reminder Summary for Today ({len(events)} event(s) found):\n"]

    if sent:
        lines.append(f"  ✅  Sent ({len(sent)}):")
        for s in sent:
            lines.append(f"      • {s}")

    if skipped:
        lines.append(f"\n  ⏭   Skipped ({len(skipped)}):")
        for s in skipped:
            lines.append(f"      • {s}")

    if errors:
        lines.append(f"\n  ❌  Errors ({len(errors)}):")
        for e in errors:
            lines.append(f"      • {e}")

    if not sent and not errors:
        lines.append("  ℹ️   No reminders needed (no attendees on today's events).")

    return "\n".join(lines)


# ── Run directly ──────────────────────────────────────────────

if __name__ == "__main__":
    """
    Run this every morning at 8:00 AM to send day-of reminders.

    Schedule on Windows (Task Scheduler):
      Action   : Start a program
      Program  : python
      Arguments: C:\\path\\to\\your\\project\\reminder_service.py
      Trigger  : Daily at 08:00 AM

    Schedule on Mac/Linux (cron):
      0 8 * * * cd /path/to/project && python reminder_service.py
    """
    print("\n" + "="*55)
    print("  Google Calendar — Day-of Reminder Service")
    print("="*55)
    print(f"\n  Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Timezone  : {TIMEZONE}")
    print(f"  HR Email  : {HR_EMAIL or 'NOT SET — add HR_EMAIL to .env'}")
    print()

    result = send_reminders_for_today()
    print(result)
    print()
