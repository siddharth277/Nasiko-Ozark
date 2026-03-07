"""
auth.py — Google OAuth2 Login (fixed)
"""

import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv(override=True)

CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE       = os.getenv("TOKEN_FILE",        "token.json")
SCOPES           = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Return an authenticated Google Calendar service. Opens browser on first run."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄  Refreshing Google token…")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"\n❌  '{CREDENTIALS_FILE}' not found!\n"
                    "    Steps to fix:\n"
                    "    1. Go to: https://console.cloud.google.com\n"
                    "    2. Create project → Enable Google Calendar API\n"
                    "    3. Credentials → + CREATE CREDENTIALS → OAuth client ID\n"
                    "    4. Application type: Desktop app → CREATE\n"
                    "    5. DOWNLOAD JSON → rename file to: credentials.json\n"
                    "    6. Place credentials.json in this project folder\n"
                    "    7. Run again\n"
                )
            print("🌐  Opening browser for Google login (one-time only)…")
            flow  = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅  Login successful!")

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"💾  Token saved to {TOKEN_FILE}")

    return build("calendar", "v3", credentials=creds)
