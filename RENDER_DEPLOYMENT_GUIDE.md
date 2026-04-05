# Render.com Deployment Guide - Complete Step-by-Step

## 🎯 Kya Milega (Free Tier)

✅ **Completely FREE** (no credit card required initially)
✅ **750 hours/month** free (enough for demo)
✅ **Auto-deploy from GitHub**
✅ **HTTPS included**
✅ **Easy setup** (15 minutes)

⚠️ **Limitation:** Sleeps after 15 min inactivity (wakes up automatically on request)

---

## 📋 Prerequisites (Already Ready!)

✅ GitHub account (hai)
✅ GitHub repository (hai)
✅ Email system tested (hai)
✅ All code ready (hai)

---

## 🚀 Deployment Steps (15 minutes)

### STEP 1: GitHub Repository Push (2 minutes)

```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0

# Add all files
git add .

# Commit
git commit -m "Render.com deployment ready - Platinum tier"

# Push to GitHub
git push origin main
```

**Verify:** Go to your GitHub repo and check files are there.

---

### STEP 2: Create Render Account (2 minutes)

1. **Go to:** https://render.com
2. **Click:** "Get Started for Free"
3. **Sign up with GitHub** (recommended)
4. **Authorize Render** to access your repos

---

### STEP 3: Create Vault Repository (5 minutes)

**Same as before:**

1. **GitHub pe jao:** https://github.com/new
2. **Repository name:** `ai-employee-vault`
3. **Private** select karo
4. **Create repository**
5. **Copy URL:** `https://github.com/nahead/ai-employee-vault.git`

**Create GitHub Token:**
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Name: `AI Employee Vault Sync`
4. Scope: `repo` (all)
5. Generate and copy token

---

### STEP 4: Deploy to Render (5 minutes)

**4.1 Create New Web Service**

1. **Render Dashboard:** https://dashboard.render.com
2. **Click:** "New +"
3. **Select:** "Web Service"
4. **Connect Repository:**
   - Select your GitHub repo: `Hackathon0`
   - Click "Connect"

**4.2 Configure Service**

**Basic Settings:**
- **Name:** `ai-employee-cloud`
- **Region:** Oregon (US West)
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Runtime:** Python 3

**Build Settings:**
- **Build Command:** `pip install -r railway-requirements.txt`
- **Start Command:** `python railway_all_in_one.py`

**4.3 Set Environment Variables**

Click "Advanced" → "Add Environment Variable"

Add these variables:

```
AGENT_TYPE=cloud
SMTP_USER=naheadj@gmail.com
SMTP_PASS=encgwiysqpyhtsji
VAULT_REPO_URL=https://github.com/nahead/ai-employee-vault.git
GIT_USERNAME=nahead
GIT_TOKEN=your-github-token-here
PYTHON_VERSION=3.13.9
```

**Important:** Replace:
- `GIT_TOKEN` with your actual GitHub token from Step 3

**4.4 Deploy**

1. **Click:** "Create Web Service"
2. **Wait:** 2-3 minutes for build
3. **Watch logs** for deployment progress

---

### STEP 5: Verify Deployment (2 minutes)

**5.1 Check Logs**

In Render dashboard:
- Click on your service
- Go to "Logs" tab
- Should see:
  ```
  Railway All-in-One Orchestrator initialized
  Environment variables configured
  Starting vault sync service...
  Starting Gmail watcher service...
  Health check server running
  ```

**5.2 Test Health Endpoint**

Your app URL will be: `https://ai-employee-cloud.onrender.com`

Test it:
```bash
curl https://ai-employee-cloud.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-05T...",
  "services": {
    "orchestrator": "running",
    "vault_sync": "active",
    "gmail_watcher": "monitoring"
  }
}
```

---

## 🎯 Platinum Demo Test (5 minutes)

### Test Offline Workflow:

**Step 1: Stop Local Agent**
```bash
# Make sure no local scripts are running
```

**Step 2: Send Test Email**
- Send email to: naheadj@gmail.com
- Subject: "Platinum Tier Demo - Render"
- Body: "Testing cloud deployment"

**Step 3: Check Render Logs**
```
Go to Render Dashboard → Logs
Should see:
- "New email detected"
- "Creating draft response"
- "Saved to vault"
```

**Step 4: Check Vault (GitHub)**
```bash
cd AI_Employee_Vault
git pull
ls Pending_Approval/
# Should see new email draft
```

**Step 5: Approve**
```bash
mv Pending_Approval/EMAIL_*.md Approved/
git add .
git commit -m "Approved email response"
git push
```

**Step 6: Verify**
- Cloud agent will sync
- Email will be sent
- Check Gmail sent folder

---

## ⚠️ Important Notes

### Free Tier Limitations:

1. **Sleep after 15 min inactivity**
   - Service sleeps if no requests
   - Wakes up automatically on next request
   - First request after sleep takes ~30 seconds

2. **750 hours/month free**
   - Enough for demo and testing
   - ~25 hours/day if always on

3. **Workaround for Sleep:**
   - Use a cron job to ping health endpoint every 10 minutes
   - Or accept the sleep (wakes automatically)

### Keep-Alive Script (Optional):

```bash
# Ping every 10 minutes to prevent sleep
*/10 * * * * curl https://ai-employee-cloud.onrender.com/health
```

---

## 🐛 Troubleshooting

### Issue: Build Failed
**Check:**
- `railway-requirements.txt` exists
- All dependencies are correct
- Python version is 3.13

**Fix:**
- Check build logs in Render dashboard
- Verify requirements file

### Issue: Service Crashed
**Check:**
- Environment variables are set correctly
- SMTP_PASS is correct
- GitHub token has repo access

**Fix:**
- Go to Environment tab
- Verify all variables
- Redeploy

### Issue: Health Check Failing
**Check:**
- Port is set correctly (Render auto-assigns)
- Health endpoint is `/health`

**Fix:**
- Check logs for errors
- Verify `railway_all_in_one.py` is running

### Issue: Email Not Detected
**Check:**
- SMTP credentials are correct
- IMAP is enabled in Gmail
- Service is not sleeping

**Fix:**
- Check logs for connection errors
- Ping health endpoint to wake service
- Verify Gmail settings

---

## 📊 Monitoring

### Render Dashboard:
- **Logs:** Real-time logs
- **Metrics:** CPU, Memory usage
- **Events:** Deployments, crashes
- **Settings:** Environment variables

### Check Service Status:
```bash
# Health check
curl https://ai-employee-cloud.onrender.com/health

# Check if sleeping
# If no response for 30+ seconds, it's sleeping
```

---

## 🎉 Success Criteria

Your Platinum tier is complete when:

- ✅ Render deployment is live
- ✅ Health endpoint responding
- ✅ Logs showing email monitoring
- ✅ Vault sync working
- ✅ Offline workflow tested successfully
- ✅ Email sent from cloud agent

---

## 📝 Next Steps After Deployment

1. **Monitor for 1 hour** - Check stability
2. **Test offline workflow** - Complete Platinum demo
3. **Record demo video** - Show cloud deployment
4. **Update submission** - Add Render deployment info
5. **Submit Platinum tier** - Complete hackathon!

---

## 💡 Tips

1. **Keep service awake during demo:**
   - Open health endpoint in browser
   - Refresh every 10 minutes

2. **Monitor logs actively:**
   - Keep Render dashboard open
   - Watch for errors

3. **Test thoroughly:**
   - Send multiple test emails
   - Verify all workflows

4. **Document everything:**
   - Take screenshots
   - Record demo video
   - Note any issues

---

## 🎬 Demo Video Checklist

Show in your video:
- ✅ Render dashboard (service running)
- ✅ Logs showing email monitoring
- ✅ Health endpoint response
- ✅ Send test email
- ✅ Cloud detects email (check logs)
- ✅ Draft created in vault (GitHub)
- ✅ Approve locally
- ✅ Email sent successfully

---

## 📞 Support

**Render Documentation:**
- https://render.com/docs

**Render Community:**
- https://community.render.com

**Your Guides:**
- This file: RENDER_DEPLOYMENT_GUIDE.md
- Quick reference: RENDER_QUICK_REFERENCE.md

---

*Render.com Deployment Guide - Platinum Tier*
*Free tier with 750 hours/month*
*Last Updated: 2026-04-05*
