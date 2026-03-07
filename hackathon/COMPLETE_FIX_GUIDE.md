# 🚀 COMPLETE FIX GUIDE - Zero to Hero
## Nasiko Hackathon HR AI Agent - All Issues Fixed

### 📋 **Current Issues Identified:**
1. ✅ Interview agent syntax error (FIXED - file provided)
2. ⚠️ Email drafting not working (missing shortlisted candidates)
3. ⚠️ Calendar integration setup needed
4. ⚠️ Missing environment variables

---

## 🎯 **STEP-BY-STEP SOLUTION**

### **PHASE 1: Fix Python Syntax Error**

#### Step 1: Replace interview_agent.py
1. Download the fixed `interview_agent.py` file I provided earlier
2. Navigate to: `C:\Users\Asus\Downloads\hackathon-integrated\hackathon\agents\`
3. Delete the old `interview_agent.py`
4. Copy the new fixed version

**OR use this code:**

```python
# File: agents/interview_agent.py
"""
Interview Agent - Generates personalized interview questions
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_interview_questions(jd: str, candidate_summary: str, candidate_skills: list, candidate_projects: list) -> str:
    """Generate 5 tailored interview questions based on JD and Resume."""
    
    # Format projects properly without backslash in f-string
    projects_text = 'None provided'
    if candidate_projects:
        projects_list = '\n- '.join(candidate_projects)
        projects_text = f'- {projects_list}'
    
    prompt = f"""You are an expert technical recruiter preparing an interviewer for an upcoming interview.
Based on the provided Job Description and Candidate Profile, generate exactly 5 interview questions.
Make them highly personalized. Do not ask generic questions like "What are your strengths?".
Instead, ask about specific gaps between their skills and the JD, or ask them to elaborate on a specific project they listed.

JOB DESCRIPTION:
{jd[:1500]}

CANDIDATE SUMMARY:
{candidate_summary}

CANDIDATE SKILLS:
{', '.join(candidate_skills)}

CANDIDATE PROJECTS:
{projects_text}

Format the output as a Markdown numbered list, with a brief 1-sentence explanation of *why* the interviewer should ask this question.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Interview questions error: {e}")
        return "Failed to generate interview questions. Please try again."
```

---

### **PHASE 2: Complete Environment Setup**

#### Step 2: Create/Update .env File

Navigate to: `C:\Users\Asus\Downloads\hackathon-integrated\hackathon\`

Create/Edit `.env` file with these values:

```env
# ============================================
# COMPLETE .ENV CONFIGURATION
# ============================================

# --- AI API Keys ---
GROQ_API_KEY=your_actual_groq_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here

# --- Google Calendar (for interview scheduling) ---
CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json
CALENDAR_ID=primary
TIMEZONE=Asia/Kolkata
HR_EMAIL=siddharthshukla840@gmail.com

# --- Gmail SMTP (for sending emails) ---
GMAIL_ADDRESS=siddharthshukla840@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password_here

# --- LLM Settings ---
MODEL_NAME=gpt-4o
MAX_TOKENS=4096

# --- Telegram (Optional - for job posting) ---
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**IMPORTANT:** Replace these placeholder values:
- `your_actual_groq_api_key_here` → Your real Groq API key
- `your_actual_openai_api_key_here` → Your real OpenAI API key
- `your_16_character_app_password_here` → Gmail App Password (see below)

---

### **PHASE 3: Setup Gmail App Password (for sending emails)**

#### Step 3: Generate Gmail App Password

**Why needed:** To send interview invitation emails

**Steps:**
1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other (Custom name)** → Type: "HR Agent"
6. Click **Generate**
7. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
8. Remove spaces: `abcdefghijklmnop`
9. Add to `.env` as `GMAIL_APP_PASSWORD=abcdefghijklmnop`

---

### **PHASE 4: Fix Email Drafting Workflow**

#### Step 4: Understanding the Correct Workflow

The "Draft Emails with AI" button fails because you need shortlisted candidates first!

**CORRECT WORKFLOW:**

```
1. Generate JD → 2. Upload Resumes → 3. Screen → 4. Shortlist → 5. Draft Emails ✅
```

**What you're doing (WRONG):**
```
1. [Skip everything] → 2. Draft Emails ❌ (No candidates!)
```

---

### **PHASE 5: Complete End-to-End Test**

#### Step 5: Follow This Exact Sequence

**Open terminal:**
```bash
cd C:\Users\Asus\Downloads\hackathon-integrated\hackathon
python main.py
```

**Open browser:** http://localhost:8000

**Now follow this sequence IN ORDER:**

---

#### **5.1 - JD Generator**
1. Click **"JD Generator"** tab
2. Enter role: `Software Engineer`
3. Click **"Generate JD"**
4. Wait for AI to generate
5. ✅ JD appears in the box

---

#### **5.2 - Resume Screening**
1. Click **"Resume Screening"** tab
2. Click **"Upload Resume"** or **"Use Sample Resumes"**
3. Click **"Screen All"**
4. Wait for AI to analyze
5. ✅ You'll see candidates with match scores

---

#### **5.3 - Shortlist Candidates**
1. Still in **"Resume Screening"** tab
2. Check the boxes next to 2-3 top candidates
3. Click **"Shortlist Selected"**
4. ✅ Confirmation: "X candidates shortlisted"

---

#### **5.4 - Draft Interview Emails** (NOW IT WILL WORK!)
1. Click **"Email Center"** tab
2. Set interview date & time: `2026-03-12 10:00`
3. Enter meeting link: `https://meet.google.com/xyz`
4. Click **"🤖 Draft Emails with AI"**
5. ✅ AI-generated emails appear for each shortlisted candidate!

---

#### **5.5 - Preview & Send Emails**
1. Click **"👁 Preview"** to read each email
2. Click **"📧 Send Emails to All"**
3. Confirm the popup
4. ✅ Emails sent via Gmail SMTP!

---

### **PHASE 6: Calendar Integration (Optional but Recommended)**

#### Step 6: Setup Google Calendar

This automatically schedules interviews in your Google Calendar.

**Quick Setup:**
1. Go to: https://console.cloud.google.com
2. Enable **Google Calendar API**
3. Create **OAuth 2.0 Client ID** (Desktop app)
4. Download `credentials.json`
5. Place in: `C:\Users\Asus\Downloads\hackathon-integrated\hackathon\`
6. Run: `python -m calendar_service.diagnose`
7. Follow browser login (add yourself as test user first!)

---

### **PHASE 7: Verification Checklist**

#### Step 7: Test Everything

Run this test script:

```bash
python test_integration.py
```

**Expected results:**
- ✅ All imports successful
- ✅ Dependencies installed
- ✅ .env configured
- ✅ Google Calendar connected (if setup)

---

## 🐛 **COMMON ERRORS & FIXES**

### Error 1: "Draft failed: No shortlisted candidates"
**Fix:** You MUST shortlist candidates first!
1. Go to Resume Screening tab
2. Upload resumes
3. Screen them
4. Shortlist 2-3 candidates
5. THEN go to Email Center

---

### Error 2: "GROQ_API_KEY not found"
**Fix:** 
1. Check `.env` file exists in hackathon folder
2. Make sure it has: `GROQ_API_KEY=your_key`
3. Restart `python main.py`

---

### Error 3: "Email send failed"
**Fix:** 
1. Check `GMAIL_ADDRESS` in `.env`
2. Check `GMAIL_APP_PASSWORD` in `.env`
3. Make sure you generated App Password (not regular password!)
4. Make sure Gmail 2FA is enabled

---

### Error 4: "ModuleNotFoundError"
**Fix:**
```bash
pip install -r requirements.txt
pip install reportlab pillow beautifulsoup4 lxml
```

---

### Error 5: "Calendar authentication failed"
**Fix:**
1. Add yourself as test user in Google Cloud Console
2. OAuth consent screen → Test users → Add your email
3. Run: `python -m calendar_service.diagnose`
4. Click "Advanced" → "Go to calendar (unsafe)" in browser

---

## 📊 **COMPLETE WORKFLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────┐
│           NASIKO HR AI AGENT WORKFLOW               │
└─────────────────────────────────────────────────────┘

1️⃣  JD GENERATOR
    └─→ Input: Role name
    └─→ Output: AI-generated job description
    └─→ Status: Saved to session

2️⃣  RESUME SCREENING
    └─→ Upload resumes (PDF)
    └─→ AI analyzes each resume
    └─→ Output: Match scores, skills, summary
    └─→ Action: Check boxes to SHORTLIST

3️⃣  EMAIL CENTER (Requires shortlisted candidates!)
    └─→ Input: Interview datetime, meeting link
    └─→ AI drafts personalized emails
    └─→ Preview emails
    └─→ Send via Gmail SMTP
    └─→ Output: Emails sent to candidates

4️⃣  CALENDAR (Auto-scheduled)
    └─→ Google Calendar creates event
    └─→ Sends calendar invites
    └─→ Sets reminders
    └─→ Output: Interview scheduled!

5️⃣  INTERVIEW QUESTIONS
    └─→ AI generates 5 personalized questions
    └─→ Based on JD + candidate profile

6️⃣  ONBOARDING
    └─→ Send welcome email
    └─→ Attach handbook, offer letter
```

---

## 🎯 **FINAL CHECKLIST**

Before submitting your hackathon project:

- [ ] `.env` file configured with all API keys
- [ ] `interview_agent.py` fixed (no syntax errors)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Gmail App Password generated and added
- [ ] Google Calendar setup (optional but impressive)
- [ ] Test complete workflow: JD → Screen → Shortlist → Email
- [ ] Server starts without errors: `python main.py`
- [ ] Dashboard loads: http://localhost:8000
- [ ] Email drafting works (after shortlisting!)
- [ ] Emails actually send (check spam folder!)

---

## 💡 **PRO TIPS**

1. **Always shortlist candidates BEFORE drafting emails**
2. **Use sample resumes in `/data/resumes/` folder for testing**
3. **Check server terminal for error messages**
4. **Gmail App Password ≠ Regular Password (must be 16 chars)**
5. **Calendar invites might take 1-2 minutes to appear**
6. **Test with your own email first before demo**

---

## 🆘 **EMERGENCY FIXES**

If nothing works:

```bash
# Nuclear option - Fresh install
cd C:\Users\Asus\Downloads\hackathon-integrated\hackathon

# Delete old venv if exists
rmdir /s venv

# Create fresh virtual environment
python -m venv venv
venv\Scripts\activate

# Install everything fresh
pip install --upgrade pip
pip install -r requirements.txt
pip install reportlab pillow beautifulsoup4 lxml

# Run
python main.py
```

---

## ✨ **YOU'RE READY!**

Follow the steps IN ORDER and your hackathon project will work perfectly!

**Key takeaway:** The email drafting REQUIRES shortlisted candidates. That's why it wasn't working - you skipped the screening step!

Good luck with your hackathon! 🚀
