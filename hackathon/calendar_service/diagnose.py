"""
diagnose.py
───────────
Run this FIRST. It tells you EXACTLY what is wrong and what to fix.

    python diagnose.py

It will check:
  1. Your .env settings
  2. credentials.json file
  3. token.json file
  4. Google Calendar API connection
  5. Whether events actually exist on your calendar
  6. What timezone your events are in vs what Python uses
  7. Whether the CALENDAR_ID points to the right calendar
"""

import os, sys
from datetime import datetime, timedelta, timezone

print()
print("=" * 60)
print("  GOOGLE CALENDAR — FULL DIAGNOSIS")
print("=" * 60)

PASS = "  ✅"
FAIL = "  ❌"
WARN = "  ⚠️ "
INFO = "  ℹ️ "

errors = []

# ── Step 1: .env ─────────────────────────────────────────────
print("\n── STEP 1: .env file ───────────────────────────────────")

if not os.path.exists(".env"):
    print(f"{FAIL}  .env file not found in this folder!")
    print(f"       → Create .env in the same folder as this script")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(override=True)

GROQ_KEY      = os.getenv("GROQ_API_KEY", "")
CREDS_FILE    = os.getenv("CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE    = os.getenv("TOKEN_FILE",        "token.json")
CALENDAR_ID   = os.getenv("CALENDAR_ID",       "primary")
TIMEZONE      = os.getenv("TIMEZONE",          "Asia/Kolkata")

print(f"{PASS}  .env found")
print(f"{INFO}  GROQ_API_KEY   = {'SET ✓' if GROQ_KEY and GROQ_KEY != 'your_groq_api_key_here' else 'NOT SET ← fix this'}")
print(f"{INFO}  CREDENTIALS_FILE = {CREDS_FILE}")
print(f"{INFO}  TOKEN_FILE       = {TOKEN_FILE}")
print(f"{INFO}  CALENDAR_ID      = {CALENDAR_ID}")
print(f"{INFO}  TIMEZONE         = {TIMEZONE}")


# ── Step 2: Credential files ──────────────────────────────────
print("\n── STEP 2: Google credential files ─────────────────────")

if os.path.exists(CREDS_FILE):
    print(f"{PASS}  {CREDS_FILE} found")
else:
    print(f"{FAIL}  {CREDS_FILE} NOT FOUND!")
    print(f"       → Download from: console.cloud.google.com")
    print(f"       → Credentials → OAuth 2.0 Client ID → Desktop app → Download JSON")
    print(f"       → Rename file to: {CREDS_FILE}")
    print(f"       → Place it in the SAME folder as this script")
    errors.append("credentials.json missing")

if os.path.exists(TOKEN_FILE):
    print(f"{PASS}  {TOKEN_FILE} found")

    # Check if token is expired
    import json
    try:
        with open(TOKEN_FILE) as f:
            t = json.load(f)
        expiry_str = t.get("expiry", "")
        if expiry_str:
            # Google token expiry format: 2025-04-15T10:30:00.000000Z
            exp = datetime.fromisoformat(expiry_str.replace("Z","").split(".")[0])
            now = datetime.utcnow()
            if exp < now:
                print(f"{WARN}  Token is EXPIRED — will auto-refresh on next run (this is normal)")
            else:
                remaining = exp - now
                print(f"{PASS}  Token is valid for {int(remaining.total_seconds()/60)} more minutes")
    except Exception:
        print(f"{INFO}  Could not read token expiry (this is fine)")
else:
    print(f"{WARN}  {TOKEN_FILE} not found — browser will open on first run")
    print(f"       → This is NORMAL if you haven't run the agent yet")
    print(f"       → Run: python main.py  and log in when the browser opens")


# ── Step 3: Connect to Google Calendar ───────────────────────
print("\n── STEP 3: Connect to Google Calendar API ───────────────")

if errors:
    print(f"{WARN}  Skipping — fix errors above first")
else:
    try:
        from .auth import get_calendar_service
        svc = get_calendar_service()
        print(f"{PASS}  Connected to Google Calendar API!")
    except FileNotFoundError as e:
        print(f"{FAIL}  credentials.json error: {e}")
        errors.append("auth failed")
        svc = None
    except Exception as e:
        print(f"{FAIL}  Connection error: {e}")
        errors.append("auth failed")
        svc = None


# ── Step 4: List ALL calendars ───────────────────────────────
print("\n── STEP 4: Your Google Calendars ───────────────────────")

if not errors and svc:
    try:
        result = svc.calendarList().list().execute()
        cals   = result.get("items", [])
        print(f"{PASS}  Found {len(cals)} calendar(s):\n")

        found_calendar_id = False
        for cal in cals:
            name      = cal.get("summary",         "Unnamed")
            cal_id    = cal.get("id",              "")
            primary   = cal.get("primary",         False)
            cal_tz    = cal.get("timeZone",        "unknown")
            selected  = (cal_id == CALENDAR_ID or (CALENDAR_ID == "primary" and primary))

            marker = "  ← ✅ THIS IS THE ONE BEING USED" if selected else ""
            p_mark = "  [PRIMARY]" if primary else ""

            print(f"       Name     : {name}{p_mark}{marker}")
            print(f"       ID       : {cal_id}")
            print(f"       Timezone : {cal_tz}")
            print()

            if selected:
                found_calendar_id = True

        if not found_calendar_id:
            print(f"{WARN}  CALENDAR_ID='{CALENDAR_ID}' was NOT found in your calendars!")
            print(f"       → Change CALENDAR_ID in .env to one of the IDs listed above")
            print(f"       → Or use CALENDAR_ID=primary")
            errors.append("wrong CALENDAR_ID")

    except Exception as e:
        print(f"{FAIL}  Could not list calendars: {e}")
        errors.append("calendar list failed")


# ── Step 5: Check events (WIDE time window) ──────────────────
print("\n── STEP 5: Check for events on your calendar ────────────")

if not errors and svc:
    try:
        # Use timezone-aware UTC now
        now_utc = datetime.now(timezone.utc)
        # Look 30 days BACK and 60 days FORWARD to find any events
        start   = now_utc - timedelta(days=30)
        end     = now_utc + timedelta(days=60)

        result  = svc.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = result.get("items", [])

        if not events:
            print(f"{WARN}  NO EVENTS FOUND in the ±60 day window!")
            print(f"\n       Possible reasons:")
            print(f"       1. You have no events on this calendar in that period")
            print(f"       2. Wrong CALENDAR_ID — events are on a DIFFERENT calendar")
            print(f"       3. Events are on Google Calendar but in a different account")
            print(f"\n       Try this fix:")
            print(f"       → Open Google Calendar in your browser")
            print(f"       → Create a test event manually (e.g. tomorrow at 3pm)")
            print(f"       → Then run this script again to confirm it shows up here")
        else:
            print(f"{PASS}  Found {len(events)} event(s) in next 60 days:\n")
            for ev in events:
                start_raw = ev["start"].get("dateTime", ev["start"].get("date","?"))
                title     = ev.get("summary", "Untitled")
                ev_id     = ev.get("id","")
                print(f"       [{title}]")
                print(f"         Start    : {start_raw}")
                print(f"         Event ID : {ev_id}")
                print()

    except Exception as e:
        print(f"{FAIL}  Could not list events: {e}")
        errors.append("events list failed")


# ── Step 6: Timezone check ───────────────────────────────────
print("\n── STEP 6: Timezone check ───────────────────────────────")

print(f"{INFO}  Your .env TIMEZONE    = {TIMEZONE}")
print(f"{INFO}  System local time     = {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{INFO}  System UTC time       = {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

# Check if TIMEZONE value is valid
try:
    import zoneinfo
    tz_obj = zoneinfo.ZoneInfo(TIMEZONE)
    local_now = datetime.now(tz_obj)
    print(f"{PASS}  TIMEZONE '{TIMEZONE}' is valid")
    print(f"{INFO}  Current time in {TIMEZONE}: {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
except Exception:
    try:
        import pytz
        tz_obj = pytz.timezone(TIMEZONE)
        print(f"{PASS}  TIMEZONE '{TIMEZONE}' is valid (via pytz)")
    except Exception:
        print(f"{WARN}  Could not validate timezone '{TIMEZONE}'")
        print(f"       → Common valid values: Asia/Kolkata, America/New_York, Europe/London")


# ── SUMMARY ──────────────────────────────────────────────────
print()
print("=" * 60)
if not errors:
    print("  ✅  DIAGNOSIS COMPLETE — No critical errors found!")
    print()
    print("  If events still don't show in the agent, the issue is:")
    print("  → Events were created in a DIFFERENT Google account")
    print("  → Events are on a DIFFERENT calendar (wrong CALENDAR_ID)")
    print("  → The agent is searching the wrong date range")
    print()
    print("  QUICK TEST: Create a manual event in Google Calendar")
    print("  (browser), then ask the agent: 'show me next 30 days'")
else:
    print(f"  ❌  {len(errors)} issue(s) found:")
    for i, e in enumerate(errors, 1):
        print(f"      {i}. {e}")
    print()
    print("  Fix the issues above, then run: python diagnose.py again")
print("=" * 60)
print()
