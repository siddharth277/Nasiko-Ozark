# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 min)
```bash
cd hackathon
pip install -r requirements.txt
```

### Step 2: Setup Google Calendar API (2 mins)
1. Visit: https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable **Google Calendar API**
4. Go to **Credentials** → Create OAuth 2.0 Client ID
5. Choose **Desktop app** → Download JSON
6. Save as `credentials.json` in the `hackathon/` folder

### Step 3: Configure Environment (1 min)
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your API keys:
nano .env  # or use any text editor
```

**Required values:**
```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HR_EMAIL=your_gmail@gmail.com
```

### Step 4: Verify Setup (30 seconds)
```bash
# Run the diagnostic tool
python -m calendar_service.diagnose
```

Expected output:
```
✅  .env found
✅  credentials.json found
✅  Connected to Google Calendar API!
✅  Found N calendar(s)
```

### Step 5: Start the Server (30 seconds)
```bash
python main.py
```

On first run:
- Browser opens automatically
- Log in with your Google account
- Grant calendar permissions
- `token.json` is created (subsequent runs won't need login)

### Step 6: Access the Dashboard
Open your browser to: **http://localhost:8000**

---

## 📋 Common Commands

### Start Server
```bash
python main.py
```

### Run Diagnostics
```bash
python -m calendar_service.diagnose
```

### Install/Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

---

## 🎯 Test the Calendar Integration

### Test 1: List Events
```bash
curl http://localhost:8000/api/calendar/events
```

### Test 2: Create Event
```bash
curl -X POST http://localhost:8000/api/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Interview",
    "datetime_str": "2026-03-10T14:00:00",
    "candidate_name": "John Doe",
    "candidate_email": "john@test.com"
  }'
```

### Test 3: Schedule Interview (Smart)
Use the web interface at `http://localhost:8000` or call from Python:

```python
from agents.calendar_agent import schedule_interview

result = schedule_interview(
    candidate={"name": "Jane Smith", "email": "jane@example.com"},
    datetime_str="",  # Auto-find best slot
    role="Software Engineer"
)
print(result)
```

---

## ⚠️ Troubleshooting

### "ImportError: No module named X"
```bash
pip install -r requirements.txt
```

### "Authentication failed"
1. Delete `token.json`
2. Restart `python main.py`
3. Browser will open for re-authentication

### "No events showing"
```bash
# Run diagnostics to check setup
python -m calendar_service.diagnose

# Check if CALENDAR_ID is correct in .env
```

### "Calendar API not enabled"
1. Go to https://console.cloud.google.com
2. Select your project
3. **APIs & Services** → **Library**
4. Search "Google Calendar API" → Enable

---

## 📚 What's Next?

- Read the full **README.md** for detailed documentation
- Check **INTEGRATION_SUMMARY.md** for technical details
- Explore the web dashboard at `http://localhost:8000`
- Try the smart scheduler features
- Set up automated email reminders

---

## 🆘 Need Help?

1. **Setup Issues**: Run `python -m calendar_service.diagnose`
2. **API Questions**: See README.md → API Endpoints section
3. **Calendar Features**: See README.md → Calendar Features section
4. **Configuration**: Check `.env.example` for all options

---

**You're all set! Start using the HR AI Agent with real Google Calendar integration. 🎉**
