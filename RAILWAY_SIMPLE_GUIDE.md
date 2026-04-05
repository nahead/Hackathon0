# Railway Deployment - 30 Minute Complete Guide (Urdu/English)

## 🎯 Kya Chahiye (Prerequisites)

✅ Node.js installed (already hai)
✅ Python installed (already hai)
✅ Git installed (already hai)
✅ GitHub account (already hai)
✅ Gmail app password (already hai in .env)

---

## 📝 Step-by-Step (Bilkul Simple)

### STEP 1: Railway CLI Install (2 minutes)

```bash
# PowerShell me ye command run karo
npm install -g @railway/cli

# Verify
railway --version
```

### STEP 2: Railway Login (2 minutes)

```bash
# Browser khulega, login karo
railway login
```

### STEP 3: GitHub Vault Repository Banao (5 minutes)

1. **GitHub pe jao:** https://github.com/new
2. **Repository name:** `ai-employee-vault`
3. **Private** select karo
4. **Create repository** click karo
5. **Repository URL copy karo:** `https://github.com/nahead/ai-employee-vault.git`

### STEP 4: GitHub Token Banao (3 minutes)

1. **Jao:** https://github.com/settings/tokens
2. **Generate new token (classic)** click karo
3. **Name:** `AI Employee Vault Sync`
4. **Select scope:** `repo` (sab check karo)
5. **Generate token** click karo
6. **Token copy karo** (save kar lo, dobara nahi milega!)

### STEP 5: Railway Project Initialize (2 minutes)

```bash
# Apne project folder me jao
cd C:\Users\nahead\Documents\GitHub\Hackathon0

# Railway project banao
railway init
# Project name: ai-employee-platinum
```

### STEP 6: Environment Variables Set Karo (5 minutes)

```bash
# Basic variables
railway variables set AGENT_TYPE=cloud
railway variables set RAILWAY_ENVIRONMENT=production

# Gmail (apna email aur app password)
railway variables set SMTP_USER=naheadj@gmail.com
railway variables set SMTP_PASS=your-gmail-app-password-here

# Vault sync (apni details dalo)
railway variables set VAULT_REPO_URL=https://github.com/YOUR-USERNAME/ai-employee-vault.git
railway variables set GIT_USERNAME=your-github-username
railway variables set GIT_TOKEN=your-github-token-here
```

**Important:** Apni actual values dalo:
- `YOUR-USERNAME` → Apna GitHub username
- `your-gmail-app-password-here` → .env file se copy karo
- `your-github-token-here` → Step 4 me jo token banaya

### STEP 7: Deploy Karo (5 minutes)

```bash
# Deploy command
railway up

# Ya detached mode me
railway up --detach
```

### STEP 8: Monitor Karo (2 minutes)

```bash
# Logs dekho
railway logs --follow

# Status check karo
railway status

# App URL dekho
railway domain
```

### STEP 9: Health Check (1 minute)

```bash
# Health endpoint test karo
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "orchestrator": "running",
    "vault_sync": "active",
    "gmail_watcher": "monitoring"
  }
}
```

---

## ✅ Success Checklist

Ye sab check karo:

- [ ] Railway CLI installed
- [ ] Railway login successful
- [ ] GitHub vault repository created
- [ ] GitHub token generated
- [ ] Railway project initialized
- [ ] Environment variables set (7 variables)
- [ ] Deployment successful
- [ ] Logs showing "healthy"
- [ ] Health endpoint responding

---

## 🎬 Platinum Demo Test (5 minutes)

### Test Offline Workflow:

**1. Local agent band karo**
```bash
# Agar chal raha hai to Ctrl+C
```

**2. Test email bhejo**
- Apne Gmail ko email bhejo
- Subject: "Platinum Tier Test"

**3. Railway logs dekho**
```bash
railway logs --follow
# Dekhna chahiye: "📧 New email detected"
```

**4. Vault check karo**
```bash
cd AI_Employee_Vault
git pull
ls Pending_Approval/
# Email draft file honi chahiye
```

**5. Approve karo**
```bash
# File ko Approved folder me move karo
mv Pending_Approval/EMAIL_*.md Approved/
git add .
git commit -m "Approved email response"
git push
```

**6. Local agent start karo**
```bash
python local_vault_sync.py
# Email send ho jayega
```

---

## 🐛 Agar Problem Aaye

### Problem: Railway CLI install nahi ho raha
```bash
# Node.js update karo
npm install -g npm@latest

# Phir retry
npm install -g @railway/cli
```

### Problem: Login nahi ho raha
```bash
# Browser manually kholo
railway login --browser
```

### Problem: Deployment fail ho raha
```bash
# Logs dekho
railway logs

# Redeploy karo
railway up --detach
```

### Problem: Environment variables set nahi ho rahe
```bash
# Railway dashboard se manually set karo
railway open
# Variables tab me jao
```

---

## 💰 Cost

**Railway Free Tier:**
- $5/month credit (FREE)
- 500+ hours/month
- Platinum demo ke liye kaafi hai!

---

## 🎯 Final Commands (Copy-Paste Ready)

```bash
# 1. Install CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize
cd C:\Users\nahead\Documents\GitHub\Hackathon0
railway init

# 4. Set variables (apni values dalo)
railway variables set AGENT_TYPE=cloud
railway variables set SMTP_USER=naheadj@gmail.com
railway variables set SMTP_PASS=your-password
railway variables set VAULT_REPO_URL=https://github.com/username/ai-employee-vault.git
railway variables set GIT_USERNAME=your-username
railway variables set GIT_TOKEN=your-token

# 5. Deploy
railway up

# 6. Monitor
railway logs --follow
```

---

## 📞 Help Chahiye?

**Railway Dashboard:** https://railway.app/dashboard
**Railway Docs:** https://docs.railway.app/
**Railway Discord:** https://discord.gg/railway

---

## 🎉 Success!

Jab ye sab ho jaye:
- ✅ Railway deployment active
- ✅ Logs me "healthy" dikhe
- ✅ Health endpoint respond kare
- ✅ Offline workflow test pass ho

**Tab aapka Platinum Tier COMPLETE! 🏆**

---

*Total Time: ~30 minutes*
*Difficulty: Medium (step-by-step follow karo)*
