# 🔧 TROUBLESHOOTING: "Draft Emails with AI" Not Working

## ❌ **THE PROBLEM**

When you click "Draft Emails with AI" button, nothing happens or you get an error.

**Screenshot shows:**
- Email Center page is open
- Interview date/time is set: `12-03-2026 10:00`
- Meeting link: `xyz`
- Button: "🤖 Draft Emails with AI"
- **BUT: No emails are being drafted!**

---

## 🔍 **ROOT CAUSE**

The email drafting feature **requires shortlisted candidates** to work!

**What the system does:**
1. Looks for shortlisted candidates in memory
2. If none found → **Button fails silently or shows error**
3. If candidates found → Drafts personalized emails for each

**Your current state:**
- ✅ Server is running
- ✅ Email Center page loaded
- ✅ Date & time entered
- ❌ **NO SHORTLISTED CANDIDATES**

---

## ✅ **THE FIX - Step by Step**

### **IMPORTANT: Follow this EXACT sequence**

Don't skip to Email Center! You must build up the workflow:

```
JD Generator → Resume Screening → Shortlist → THEN Email Center
```

---

### **Step 1: Generate Job Description**

1. Click **"JD Generator"** tab (top of page)
2. Enter a role name: `Software Engineer`
3. Select style: `Standard` (or any style)
4. Click **"🎯 Generate JD"**
5. **Wait 5-10 seconds** for AI to generate
6. ✅ You'll see the job description appear

**What happens:**
- Role is saved to session: `current_role = "Software Engineer"`
- JD is saved to session: `current_jd = "...text..."`

---

### **Step 2: Upload Resumes**

1. Click **"Resume Screening"** tab
2. **Option A:** Click **"Use Sample Resumes"** (if available)
   - This loads resumes from `/data/resumes/` folder
   
   **Option B:** Click **"📁 Upload Resume"**
   - Select a PDF resume from your computer
   - Upload 2-3 resumes for testing

3. ✅ You'll see uploaded resumes listed

**What happens:**
- Resumes are added to session: `resumes = [resume1, resume2, ...]`

---

### **Step 3: Screen Resumes with AI**

1. Still in **"Resume Screening"** tab
2. Click **"🔍 Screen All"** button
3. **Wait 10-20 seconds** for AI to analyze each resume
4. ✅ You'll see:
   - Each candidate's match score (e.g., "85% match")
   - Skills extracted
   - Summary of experience
   - Ranking by relevance

**What happens:**
- AI compares each resume to the JD
- Generates match scores
- Extracts skills and projects
- Results saved to session: `screened = [...]`

---

### **Step 4: Shortlist Candidates**

**THIS IS THE CRITICAL STEP YOU'RE MISSING!**

1. Still in **"Resume Screening"** tab
2. Look at the screened candidates
3. **Check the checkbox** next to 2-3 top candidates
4. Click **"✅ Shortlist Selected"** button
5. ✅ You'll see a success message: "X candidates shortlisted"

**What happens:**
- Selected candidates moved to: `shortlisted = [candidate1, candidate2, ...]`
- **This is what Email Center needs!**

**Example:**
```
☑ Aryan Kumar - 92% match
☑ Priya Sharma - 88% match
☐ Rahul Singh - 75% match
```
Click "Shortlist Selected" → 2 candidates shortlisted

---

### **Step 5: Draft Emails (NOW IT WORKS!)**

1. **NOW** click **"Email Center"** tab
2. Set interview date & time: `2026-03-12 10:00`
3. Enter meeting link: `https://meet.google.com/xyz-abc-def`
4. Click **"🤖 Draft Emails with AI"**
5. **Wait 5-10 seconds** for AI to generate emails
6. ✅ **SUCCESS!** You'll see:
   - Personalized email for each shortlisted candidate
   - Subject line
   - Email body with interview details
   - Preview option

**What happens:**
- AI generates a unique email for each shortlisted candidate
- Uses candidate name, role, interview time
- Saves drafts to session: `draft_emails = {...}`

---

### **Step 6: Preview & Send**

1. Click **"👁 Preview"** on any email to read it
2. Review all emails
3. Click **"📧 Send Emails to All"**
4. Confirm the popup
5. ✅ Emails sent via Gmail!

**What happens:**
- Connects to Gmail SMTP
- Sends each email
- Shows success/failure for each

---

## 🎯 **VISUAL WORKFLOW**

```
┌─────────────────────────────────────────────┐
│  CORRECT SEQUENCE (Must follow in order!)  │
└─────────────────────────────────────────────┘

1. JD GENERATOR
   └─→ Generate JD for "Software Engineer"
   └─→ ✓ Role & JD saved to session

2. RESUME SCREENING
   └─→ Upload 3 resumes (or use samples)
   └─→ Click "Screen All"
   └─→ ✓ AI analyzes resumes
   └─→ Shows match scores
   
3. SHORTLIST (⚠️ YOU SKIPPED THIS!)
   └─→ Check boxes next to top 2-3 candidates
   └─→ Click "Shortlist Selected"
   └─→ ✓ Candidates saved to shortlist

4. EMAIL CENTER (⚠️ This is where you are!)
   └─→ Set interview date/time
   └─→ Click "Draft Emails with AI"
   └─→ ✓ Emails generated for shortlisted candidates
   └─→ Preview emails
   └─→ Send to all

5. CALENDAR (Automatic)
   └─→ Interview auto-scheduled in Google Calendar
   └─→ ✓ Calendar invites sent
```

---

## 🔍 **HOW TO CHECK IF SHORTLIST IS EMPTY**

Open browser console (F12 → Console tab) and type:

```javascript
console.log(state.shortlisted);
```

**If it shows:**
- `undefined` or `null` or `[]` → **NO SHORTLISTED CANDIDATES** (you need to shortlist!)
- `[{...}, {...}]` → **CANDIDATES EXIST** (email drafting should work!)

---

## ❓ **COMMON QUESTIONS**

### Q: Why can't I just draft emails without screening?
**A:** The system needs candidate details (name, email, skills) to personalize each email. These come from the screening step.

### Q: Can I manually add candidates?
**A:** Not through the UI. You must upload resumes → screen → shortlist.

### Q: I don't have resumes, what do I do?
**A:** Use the sample resumes in `/data/resumes/` folder! Just click "Use Sample Resumes" button.

### Q: The "Shortlist Selected" button isn't showing
**A:** Make sure you've clicked "Screen All" first. The shortlist button only appears after screening.

---

## 🧪 **QUICK TEST SEQUENCE (Copy-Paste)**

Follow this exact sequence:

1. **JD Tab** → Role: `Software Engineer` → Click Generate → Wait
2. **Resume Tab** → Click "Use Sample Resumes" → Wait
3. **Resume Tab** → Click "Screen All" → Wait 15 seconds
4. **Resume Tab** → Check boxes next to top 2 candidates → Click "Shortlist Selected"
5. **Email Tab** → Date: `2026-03-15 14:00` → Link: `https://meet.google.com/test`
6. **Email Tab** → Click "Draft Emails with AI" → Wait
7. ✅ **Emails appear!**

---

## 🆘 **STILL NOT WORKING?**

### Check 1: Is GROQ_API_KEY in .env?
```bash
# Open .env and verify:
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

### Check 2: Check browser console for errors
1. Press F12
2. Click Console tab
3. Look for red error messages
4. Share the error with me!

### Check 3: Check server terminal for errors
Look at the terminal where `python main.py` is running.
Any red errors? Share them!

### Check 4: Restart server
```bash
# Press Ctrl+C to stop
# Then restart:
python main.py
```

---

## ✅ **SUCCESS INDICATORS**

You'll know it's working when:

1. ✅ JD Generator shows generated text
2. ✅ Resume Screening shows match scores
3. ✅ "X candidates shortlisted" message appears
4. ✅ Email drafts appear with candidate names
5. ✅ Preview shows personalized email content
6. ✅ "Emails sent successfully" message

---

## 🎓 **KEY TAKEAWAY**

**The "Draft Emails with AI" button REQUIRES shortlisted candidates.**

You can't skip the screening step!

**Think of it like this:**
- Email drafting is step 4 of a 5-step process
- You tried to do step 4 without doing steps 1-3
- Go back and complete steps 1-3, then step 4 will work!

---

**Good luck! Follow the steps IN ORDER and it will work perfectly!** 🚀
