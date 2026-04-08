# 🧪 Local Testing Guide

Complete guide for testing the AI Employee system locally.

## 📋 Prerequisites

### Required Software
- Python 3.13+
- Git

### Required Credentials

1. **Gmail Account** (for email detection and sending)
   - Gmail address
   - App Password (not regular password)

2. **LinkedIn API** (for posting - optional)
   - Developer account at https://www.linkedin.com/developers/
   - Access token

---

## 🔧 Setup

### 1. Set Environment Variables

```bash
# Required for email detection and sending
export SMTP_USER='your-email@gmail.com'
export SMTP_PASS='your-app-password'

# Optional for LinkedIn posting
export LINKEDIN_ACCESS_TOKEN='your_linkedin_token'
export LINKEDIN_PERSON_URN='urn:li:person:your_id'
```

### 2. Get Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and your device
3. Click "Generate"
4. Copy the 16-character password
5. Use this password (NOT your regular Gmail password)

---

## 🚀 Running Tests

### Quick Start - Run All Tests

```bash
python run_all_tests.py
```

This will run all 4 tests in sequence:
1. Email Detection
2. Email Sending
3. LinkedIn Content Creation
4. LinkedIn Posting (dry run)

### Individual Tests

#### Test 1: Email Detection

```bash
python test_email_detection.py
```

**What it does:**
- Connects to Gmail via IMAP
- Lists unread emails
- Creates approval file in vault

**Expected output:**
```
✅ Connected to Gmail as: your-email@gmail.com
✅ Inbox selected
📧 Found X unread emails
✅ Email detection test PASSED
```

---

#### Test 2: Email Sending

```bash
python test_email_sender.py
```

**What it does:**
- Tests SMTP email sending via Gmail
- Sends test email to your inbox

**Expected output:**
```
[OK] Email sent successfully via SMTP (SSL port 465)
[INBOX] Check your inbox: your-email@gmail.com
```

---

#### Test 3: LinkedIn Content Creation

```bash
python test_linkedin_content.py
```

**What it does:**
- Generates 3 LinkedIn post templates
- Creates approval files in vault
- Shows content preview

**Expected output:**
```
📝 Generated LinkedIn Content:
POST 1: ACHIEVEMENT
POST 2: EDUCATIONAL
POST 3: TECHNICAL
✅ Created: LINKEDIN_POST_20260407_123456_1.md
```

**Files created:**
- `AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md`

---

#### Test 4: LinkedIn Posting

```bash
# Dry run (no actual posting)
DRY_RUN=true python test_linkedin_poster.py

# Live posting (requires LinkedIn API credentials)
DRY_RUN=false python test_linkedin_poster.py
```

**What it does:**
- Checks for approved posts in vault
- Posts to LinkedIn (if not dry run)
- Moves completed posts to Done folder

**Expected output (dry run):**
```
⚠️ DRY RUN MODE - No actual posting
✅ Dry run successful - content validated
```

---

## 📁 Workflow

### Complete Email Workflow

1. **Detection:**
   ```bash
   python test_email_detection.py
   ```
   Creates: `AI_Employee_Vault/Pending_Approval/EMAIL_TEST_*.md`

2. **Review:**
   - Open the approval file
   - Edit if needed
   - Move to `AI_Employee_Vault/Approved/` to approve

3. **Sending:**
   ```bash
   python test_email_sender.py
   ```
   Sends the approved email

### Complete LinkedIn Workflow

1. **Content Creation:**
   ```bash
   python test_linkedin_content.py
   ```
   Creates: `AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md`

2. **Review:**
   - Open the approval files
   - Edit content if needed
   - Move to `AI_Employee_Vault/Approved/` to approve

3. **Posting (Dry Run):**
   ```bash
   DRY_RUN=true python test_linkedin_poster.py
   ```
   Validates content without posting

4. **Posting (Live):**
   ```bash
   DRY_RUN=false python test_linkedin_poster.py
   ```
   Posts to LinkedIn and moves to Done

---

## 🔍 Troubleshooting

### Email Detection Issues

**Problem:** "Authentication failed"
- **Solution:** Use App Password, not regular Gmail password
- **Get it:** https://myaccount.google.com/apppasswords

**Problem:** "No unread emails found"
- **Solution:** Send yourself a test email first

### Email Sending Issues

**Problem:** "SMTP connection failed"
- **Solution:** Check Gmail App Password is correct
- **Solution:** Try both SSL (port 465) and TLS (port 587)
- **Solution:** Verify 2-factor authentication is enabled on Gmail

### LinkedIn Issues

**Problem:** "LINKEDIN_ACCESS_TOKEN not set"
- **Solution:** Get token from LinkedIn Developer Portal
- **URL:** https://www.linkedin.com/developers/

**Problem:** "API connection failed"
- **Solution:** Token may be expired, generate new one

---

## 📊 Expected Results

### Successful Test Run

```
✅ Email Detection: PASSED
✅ Email Sending: PASSED
✅ LinkedIn Content: PASSED
✅ LinkedIn Posting: PASSED (DRY RUN)

🎉 ALL TESTS PASSED!
```

### Files Created

```
AI_Employee_Vault/
├── Pending_Approval/
│   ├── EMAIL_TEST_20260407_123456.md
│   ├── LINKEDIN_POST_20260407_123456_1.md
│   ├── LINKEDIN_POST_20260407_123456_2.md
│   └── LINKEDIN_POST_20260407_123456_3.md
├── Approved/
│   └── (move files here to approve)
└── Done/
    └── (completed tasks moved here)
```

---

## 🌐 Cloud Deployment

The system is already running 24/7 on the cloud:

- **Dashboard:** https://ai-employee-cloud.onrender.com
- **Health API:** https://ai-employee-cloud.onrender.com/health
- **Live Logs:** Real-time activity monitoring

**Cloud Features:**
- ✅ Email monitoring (24/7)
- ✅ Real-time log display
- ✅ Email detection and display
- ✅ Health monitoring

---

## 📝 Notes

1. **Dry Run Mode:** Always test with `DRY_RUN=true` first
2. **Approval Workflow:** All actions require human approval
3. **Security:** Never commit credentials to git
4. **Rate Limits:** Be mindful of API rate limits
5. **Testing:** Use test emails/posts before going live

---

## 🆘 Support

If you encounter issues:

1. Check environment variables are set correctly
2. Verify credentials are valid
3. Check the error messages in output
4. Review the troubleshooting section above

For cloud deployment issues:
- Check: https://ai-employee-cloud.onrender.com/health
- View logs: https://ai-employee-cloud.onrender.com

---

## ✅ Checklist

Before running tests:
- [ ] Python 3.13+ installed
- [ ] Environment variables set
- [ ] Gmail App Password obtained
- [ ] Resend API key (optional)
- [ ] LinkedIn credentials (optional)

After running tests:
- [ ] All tests passed
- [ ] Approval files created
- [ ] Workflow tested end-to-end
- [ ] Ready for production use
