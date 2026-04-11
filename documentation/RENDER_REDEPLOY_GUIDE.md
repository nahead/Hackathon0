# Render.com Redeploy Guide - Intelligent WhatsApp System

## Quick Redeploy Steps

### Option A: Automatic Redeploy (Recommended)

Render automatically redeploys when you push to GitHub:

1. ✅ **Already Done:** Code pushed to GitHub (commit: 33ab55c)
2. **Go to:** https://dashboard.render.com/
3. **Find your service** (if exists) or create new one
4. **Render will auto-deploy** from latest commit

### Option B: Manual Redeploy

If you have existing service:

1. Go to: https://dashboard.render.com/
2. Click on your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**
4. Wait for deployment to complete

### Option C: Create New Service

If no service exists yet:

1. Go to: https://dashboard.render.com/
2. Click: **"New +"** → **"Web Service"**
3. Connect GitHub repository: `nahead/Hackathon0`
4. Configure settings (see below)

---

## 🔧 Service Configuration

### Basic Settings

```
Name: ai-employee-whatsapp
Region: Singapore (or closest to you)
Branch: main
Root Directory: (leave empty)
```

### Build Settings

```
Build Command: pip install -r requirements.txt
Start Command: python implementation/whatsapp_webhook.py
```

### Environment Variables

Click **"Environment"** tab and add these one by one:

**WhatsApp (Required):**
```
WHATSAPP_ACCESS_TOKEN
Value: EAALxnnACIoABRKUcn2x15eNZCUaZAdqCZCD5mkuiZCy4LkbyzABKxBx1VaPvPXthDMO0pSZCoNPdwl0ZC1C2d1JV7NpBn96I6Gdrrnl8QeROMQBFGTJsXZBkD0BUZADr3aFd5ZAdrUZBINFz7kzQbBEpdT7Ot6mHzzZCilTonQinf0zlfhfxQrkma5ZCUK4DDmupxFsIwZDZD

WHATSAPP_PHONE_NUMBER_ID
Value: 1004199756120385

WHATSAPP_BUSINESS_ACCOUNT_ID
Value: 1491297882449999

WHATSAPP_WEBHOOK_VERIFY_TOKEN
Value: ai_employee_whatsapp_verify_2026
```

**Server (Required):**
```
PORT
Value: 8080
```

**LinkedIn (Optional):**
```
LINKEDIN_ACCESS_TOKEN
Value: AQWO57LAdDComDNuYaz9IDxgcl_x8MQZsZ-6Al_rYI5Tp7bSfvKux5Kc3cJn2D-T0QIfFrLHV_NuY1lYjrLB2pKrcN1jYc1QYB5G-E0NPmgWBayrCmlu1gh-dTLOVrZI2C3yOxmG_geBpi8IvoWfFVUwcUJd11wEfX0bH4a2pmgLbo_hrv0dqgmOz9pNmxnCcFQxf1kLH3ZVV2aytHzv0hg5SiBrkRFcvk1MS857ZIQMjraPRU2WbJp5MXO-01npu8oaMI18lqyO0xTdR9mu6cdbjjtn3Dbm-eM-Q22_EHL1jzRYYc4qtqG1Fm8PoP6EXboqMy3aR2eWa7bPk67cCCFf1hv5Fw

LINKEDIN_PERSON_URN
Value: urn:li:person:XbMGWdmblt
```

**Email (Optional):**
```
SMTP_HOST
Value: smtp.gmail.com

SMTP_PORT
Value: 587

SMTP_USER
Value: naheadj@gmail.com

SMTP_PASS
Value: encgwiysqpyhtsji

EMAIL_FROM_ADDRESS
Value: naheadj@gmail.com
```

### Health Check

```
Health Check Path: /health
```

### Instance Type

- **Free:** For testing (sleeps after 15min inactivity)
- **Starter ($7/month):** For production (always on, no sleep)

---

## ✅ Verify Deployment

### Step 1: Check Deployment Status

1. In Render dashboard, watch the **"Logs"** tab
2. Look for:
   ```
   Starting WhatsApp Webhook on port 8080...
   * Running on http://0.0.0.0:8080
   ```
3. Status should show: **"Live"** (green)

### Step 2: Test Health Endpoint

Open in browser:
```
https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "whatsapp_webhook",
  "timestamp": "2026-04-11T..."
}
```

### Step 3: Check Dashboard

Open in browser:
```
https://your-app-name.onrender.com/
```

You should see the WhatsApp Webhook dashboard with setup instructions.

---

## 🔗 Configure WhatsApp Webhook

### Step 1: Get Your Render URL

Your URL will be:
```
https://ai-employee-whatsapp.onrender.com
```

(Or whatever name you chose)

### Step 2: Configure in Meta Dashboard

1. **Go to:** https://developers.facebook.com/apps/
2. **Select:** Your WhatsApp app
3. **Navigate:** Left sidebar → WhatsApp → Configuration
4. **Find:** Webhook section
5. **Click:** "Edit" or "Configure"

### Step 3: Add Webhook URL

**Callback URL:**
```
https://your-app-name.onrender.com/webhook/whatsapp
```

**Verify Token:**
```
ai_employee_whatsapp_verify_2026
```

### Step 4: Subscribe to Events

Check the box for:
- ✅ **messages**

### Step 5: Verify and Save

1. Click **"Verify and Save"**
2. Meta will send GET request to verify
3. Should show: ✅ "Verified"

---

## 🧪 Test the System

### Test 1: Send Routine Message

From your phone (03122955972), send to business number:
```
Hello! Can you tell me about your services?
```

**Expected:**
- System receives via webhook (instant)
- Classifies as ROUTINE
- Auto-responds within 5 seconds
- You receive intelligent reply

**Check Render Logs:**
```
[NEW MESSAGE] From: Your Name (923122955972)
[CLASSIFICATION] ROUTINE
[SENT] ✅ Message sent to 923122955972
```

### Test 2: Send Serious Message

From your phone, send:
```
URGENT! I have a complaint and want a refund!
```

**Expected:**
- System receives via webhook
- Classifies as SERIOUS
- Creates approval request
- NO auto-response sent

**Check Render Logs:**
```
[NEW MESSAGE] From: Your Name (923122955972)
[CLASSIFICATION] SERIOUS
[APPROVAL] ⚠️ Created approval request
```

**Check Vault:**
- File created in: `/Pending_Approval/WHATSAPP_APPROVAL_*.md`

---

## 🔍 Monitoring

### Check Render Logs

In Render dashboard:
1. Click on your service
2. Go to **"Logs"** tab
3. Watch for:
   - `[NEW MESSAGE]` - Incoming messages
   - `[CLASSIFICATION]` - How message was classified
   - `[SENT]` - Auto-responses sent
   - `[APPROVAL]` - Approval requests created

### Check Vault (Local)

```bash
cd AI_Employee_Vault

# Check pending approvals
ls -la Pending_Approval/

# Check done messages
ls -la Done/
```

---

## 🐛 Troubleshooting

### Issue: Webhook not receiving messages

**Check:**
1. Webhook URL is correct in Meta dashboard
2. Verify token matches exactly
3. Service is "Live" in Render
4. Check Render logs for errors

**Fix:**
- Re-verify webhook in Meta dashboard
- Check environment variables are set
- Restart service in Render

### Issue: Messages received but not responding

**Check:**
1. WHATSAPP_ACCESS_TOKEN is valid
2. Phone number format is correct (no + sign)
3. Check Render logs for API errors

**Fix:**
- Verify token hasn't expired
- Check Meta dashboard for API errors
- Review Render logs for details

### Issue: Service keeps sleeping (Free tier)

**Symptom:** First message takes 30+ seconds

**Fix:**
- Upgrade to Starter plan ($7/month)
- Or use external ping service to keep awake
- Or accept cold start delay

---

## 💡 Pro Tips

### Keep Service Awake (Free Tier)

Use cron-job.org or similar:
```
URL: https://your-app.onrender.com/health
Interval: Every 10 minutes
```

### Monitor Uptime

Use UptimeRobot.com (free):
- Monitor: https://your-app.onrender.com/health
- Alert: Email when down
- Interval: 5 minutes

### View Live Logs

In Render dashboard:
- Enable "Live Logs"
- Watch real-time message processing
- Debug issues instantly

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub (commit: 33ab55c)
- [ ] Render service created/updated
- [ ] Environment variables added
- [ ] Service deployed successfully
- [ ] Health check returns 200 OK
- [ ] Webhook configured in Meta dashboard
- [ ] Webhook verified successfully
- [ ] Test message 1 (routine) - auto-responded
- [ ] Test message 2 (serious) - approval created
- [ ] Logs showing correct behavior

---

## 🎯 What Happens After Deploy

**Automatic Process:**

1. **Client sends WhatsApp message** → Your business number
2. **Meta forwards to webhook** → Render service receives
3. **Intelligent classification** → Routine or Serious
4. **If Routine:** Auto-respond instantly (< 5 sec)
5. **If Serious:** Create approval request
6. **You review & approve** → System sends your response
7. **Complete audit trail** → All logged

**You're now running a 24/7 autonomous AI Employee!** 🎉

---

## 📞 Need Help?

**Check:**
1. Render logs for errors
2. Meta dashboard for webhook status
3. GitHub repository for latest code
4. Documentation folder for guides

**Common URLs:**
- Render: https://dashboard.render.com/
- Meta: https://developers.facebook.com/apps/
- GitHub: https://github.com/nahead/Hackathon0
