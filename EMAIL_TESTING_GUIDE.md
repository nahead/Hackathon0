# Email System Testing Guide

## 🎯 Quick Test (5 minutes)

### Step 1: Run Test Script
```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0
python test_email_system.py
```

### Step 2: Select Test Mode
- **Option 1:** Run all tests (recommended)
- **Option 2:** Quick test (just connections)
- **Option 3:** Full test (includes sending email)

### Step 3: Check Results
Script will test:
- ✅ Credentials (SMTP_USER, SMTP_PASS)
- ✅ IMAP connection (email detection)
- ✅ SMTP connection (email sending)
- ✅ Vault folder structure
- ✅ Send test email (optional)
- ✅ Email detection (optional)

---

## 📧 Manual Email Test (10 minutes)

### Test 1: Email Detection

**Step 1: Start Gmail Watcher**
```bash
python simple_gmail_watcher.py
```

**Step 2: Send Test Email**
- Open Gmail in browser
- Send email to yourself: naheadj@gmail.com
- Subject: "Test Email Detection"
- Body: "Testing AI Employee email detection"

**Step 3: Check Watcher Output**
Should see:
```
SUCCESS: Connected to Gmail: naheadj@gmail.com
FOUND: Found 1 new emails
[EMAIL] Processing: Test Email Detection from naheadj@gmail.com
SUCCESS: Approval file created: EMAIL_TEST_*.md
```

**Step 4: Check Vault**
```bash
ls AI_Employee_Vault/Needs_Action/
# Should see: EMAIL_TEST_*.md
```

---

### Test 2: Email Response

**Step 1: Check Approval File**
```bash
cat AI_Employee_Vault/Needs_Action/EMAIL_TEST_*.md
```

Should contain:
- Original email details
- Suggested response
- Approval instructions

**Step 2: Approve Response**
```bash
# Move to Approved folder
mv AI_Employee_Vault/Needs_Action/EMAIL_TEST_*.md AI_Employee_Vault/Approved/
```

**Step 3: Send Response (Manual)**
```bash
python email_response_sender.py
```

**Step 4: Check Gmail**
- Check sent folder
- Verify email was sent

---

## 🔍 Troubleshooting

### Issue: "Gmail App Password not found"
**Fix:**
```bash
# Check .env file
cat .env | grep SMTP

# Should show:
# SMTP_USER=naheadj@gmail.com
# SMTP_PASS=encgwiysqpyhtsji
```

### Issue: "Authentication failed"
**Fix:**
1. Check if IMAP is enabled in Gmail
2. Go to: https://mail.google.com/mail/u/0/#settings/fwdandpop
3. Enable IMAP
4. Save changes

### Issue: "Connection timeout"
**Fix:**
1. Check internet connection
2. Check firewall settings
3. Try different network

### Issue: "No emails detected"
**Fix:**
1. Make sure email is unread
2. Check spam folder
3. Wait 1-2 minutes for sync

---

## ✅ Success Criteria

Email system is working when:
- ✅ Gmail watcher connects successfully
- ✅ Unread emails are detected
- ✅ Approval files are created in Needs_Action/
- ✅ Email responses can be sent
- ✅ No authentication errors

---

## 🎯 Next Steps After Testing

Once email system is working:
1. ✅ Local email detection: Working
2. ✅ Local email sending: Working
3. ➡️ Deploy to Railway (cloud 24/7)
4. ➡️ Test offline workflow (Platinum demo)
5. ➡️ Submit hackathon

---

*Email System Testing Guide*
*Test locally first, then deploy to cloud*
