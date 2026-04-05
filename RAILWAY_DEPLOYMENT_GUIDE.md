# Railway Deployment Guide - Platinum Tier Complete

## 📋 Table of Contents
1. Railway Account Setup
2. Railway CLI Installation
3. Project Preparation
4. Environment Variables Configuration
5. Deployment Process
6. Vault Sync Setup
7. Testing & Verification
8. Platinum Demo

---

## Step 1: Railway Account Setup (5 minutes)

### 1.1 Create Railway Account
1. Visit: https://railway.app/
2. Click "Start a New Project"
3. Sign up with GitHub account (recommended)
4. Verify your email

### 1.2 Get Railway Credits
- Railway gives $5 free credits per month
- Enough for Platinum tier demo
- No credit card required for trial

---

## Step 2: Railway CLI Installation (5 minutes)

### For Windows (PowerShell):
```powershell
# Install via npm (recommended)
npm install -g @railway/cli

# OR download installer
# Visit: https://docs.railway.app/develop/cli#installation
```

### For Linux/Mac:
```bash
# Install via npm
npm install -g @railway/cli

# OR via shell script
curl -fsSL https://railway.app/install.sh | sh
```

### Verify Installation:
```bash
railway --version
```

### Login to Railway:
```bash
railway login
# Browser window will open
# Authorize the CLI
```

---

## Step 3: Project Preparation (10 minutes)

### 3.1 Create .env.railway file
```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0
```

Create `.env.railway` file:
```env
# Railway Environment Variables
AGENT_TYPE=cloud
RAILWAY_ENVIRONMENT=production
NODE_ENV=production

# Gmail Configuration (for cloud agent)
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Vault Sync Configuration
VAULT_REPO_URL=https://github.com/your-username/ai-employee-vault.git
GIT_USERNAME=your-github-username
GIT_TOKEN=your-github-token

# Optional: Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

### 3.2 Create railway-requirements.txt
```bash
# Minimal requirements for Railway (to reduce build time)
watchdog==3.0.0
schedule==1.2.0
python-dotenv==1.0.0
requests==2.31.0
psutil==5.9.6
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-api-python-client==2.108.0
gitpython==3.1.40
```

### 3.3 Update Procfile for Railway
```procfile
web: python railway_all_in_one.py
```

---

## Step 4: Initialize Railway Project (5 minutes)

### 4.1 Initialize in your project directory:
```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0
railway init
```

You'll be asked:
- Project name: `ai-employee-platinum`
- Select: "Create new project"

### 4.2 Link to Railway:
```bash
railway link
```

---

## Step 5: Configure Environment Variables (10 minutes)

### Option A: Via Railway CLI
```bash
# Set variables one by one
railway variables set AGENT_TYPE=cloud
railway variables set RAILWAY_ENVIRONMENT=production
railway variables set SMTP_USER=your-email@gmail.com
railway variables set SMTP_PASS=your-app-password
railway variables set VAULT_REPO_URL=https://github.com/username/vault.git
railway variables set GIT_USERNAME=your-username
railway variables set GIT_TOKEN=your-token
```

### Option B: Via Railway Dashboard (Easier)
1. Go to: https://railway.app/dashboard
2. Select your project: `ai-employee-platinum`
3. Click "Variables" tab
4. Click "New Variable"
5. Add all variables from `.env.railway`

**Important Variables:**
- `AGENT_TYPE=cloud` (tells system it's cloud agent)
- `SMTP_USER` (your Gmail)
- `SMTP_PASS` (Gmail app password)
- `VAULT_REPO_URL` (Git repo for vault sync)
- `GIT_USERNAME` (GitHub username)
- `GIT_TOKEN` (GitHub personal access token)

---

## Step 6: Create Vault Repository (15 minutes)

### 6.1 Create GitHub Repository for Vault
```bash
# On GitHub, create new repository:
# Name: ai-employee-vault
# Private repository
# Don't initialize with README
```

### 6.2 Initialize Local Vault as Git Repo
```bash
cd AI_Employee_Vault

# Initialize git
git init

# Create .gitignore for vault
cat > .gitignore << 'EOF'
# Logs
Logs/*.log
Logs/*.json
Logs/Audit/*.db

# Obsidian workspace
.obsidian/workspace
.obsidian/workspace.json

# Temporary files
*.tmp
*.temp

# Credentials (never sync)
credentials.json
*_token.json
EOF

# Add files
git add .

# Commit
git commit -m "Initial vault setup for cloud sync"

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/ai-employee-vault.git

# Push
git push -u origin main
```

### 6.3 Create GitHub Personal Access Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `AI Employee Vault Sync`
4. Select scopes: `repo` (all)
5. Generate token
6. Copy token (save it - you won't see it again!)

---

## Step 7: Deploy to Railway (10 minutes)

### 7.1 Commit all changes
```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0

# Add all files
git add .

# Commit
git commit -m "Railway deployment configuration for Platinum tier"

# Push to GitHub
git push origin main
```

### 7.2 Deploy to Railway
```bash
# Deploy from current directory
railway up

# OR deploy from GitHub
railway up --detach
```

### 7.3 Monitor Deployment
```bash
# Watch logs
railway logs

# Check status
railway status
```

---

## Step 8: Verify Deployment (5 minutes)

### 8.1 Check Railway Dashboard
1. Go to: https://railway.app/dashboard
2. Select your project
3. Check "Deployments" tab
4. Should show "Active" status

### 8.2 Check Logs
```bash
railway logs --follow
```

You should see:
```
🚀 Railway All-in-One Orchestrator initialized
✅ Environment variables configured
🔄 Starting vault sync service...
📧 Starting Gmail watcher service...
🌐 Health check server running on port 8080
```

### 8.3 Test Health Endpoint
```bash
# Get your Railway URL
railway domain

# Test health endpoint
curl https://your-app.railway.app/health
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

## Step 9: Local Agent Setup (5 minutes)

### 9.1 Configure Local Agent
```bash
cd C:\Users\nahead\Documents\GitHub\Hackathon0

# Create local config
cat > .env.local << 'EOF'
AGENT_TYPE=local
VAULT_REPO_URL=https://github.com/YOUR-USERNAME/ai-employee-vault.git
GIT_USERNAME=your-username
GIT_TOKEN=your-token
EOF
```

### 9.2 Start Local Vault Sync
```bash
python local_vault_sync.py
```

This will:
- Pull latest changes from cloud
- Monitor for approval requests
- Push approved actions back

---

## Step 10: Platinum Demo Test (10 minutes)

### Test Scenario: Offline Email Workflow

**Step 1: Stop Local Agent**
```bash
# Stop local_vault_sync.py (Ctrl+C)
```

**Step 2: Send Test Email**
- Send email to your Gmail
- Subject: "Test Platinum Tier Demo"
- Body: "This is a test for offline workflow"

**Step 3: Cloud Agent Creates Draft**
```bash
# Check Railway logs
railway logs

# Should see:
# 📧 New email detected
# 📝 Creating draft response
# 💾 Saved to vault: /Pending_Approval/EMAIL_...
```

**Step 4: Start Local Agent**
```bash
python local_vault_sync.py
```

**Step 5: Approve Draft**
```bash
# Check pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Move to approved
mv AI_Employee_Vault/Pending_Approval/EMAIL_*.md AI_Employee_Vault/Approved/
```

**Step 6: Local Agent Executes**
```bash
# Local agent will:
# 1. Detect approved file
# 2. Send email via local MCP server
# 3. Move to /Done/
# 4. Push to vault
```

**Step 7: Verify**
- Check sent email in Gmail
- Check Railway logs for sync confirmation
- Check `/Done/` folder for completed task

---

## 🎯 Success Criteria

Your Platinum tier is complete when:

- ✅ Railway deployment is active (24/7)
- ✅ Cloud agent monitoring emails
- ✅ Vault syncing via Git
- ✅ Local agent handling approvals
- ✅ Offline workflow demo successful
- ✅ Health endpoint responding
- ✅ Logs showing continuous operation

---

## 📊 Railway Dashboard Monitoring

### Key Metrics to Watch:
1. **Deployment Status**: Should be "Active"
2. **Memory Usage**: Should be < 512MB
3. **CPU Usage**: Should be < 50%
4. **Network**: Inbound/outbound traffic
5. **Logs**: No critical errors

### Railway Free Tier Limits:
- $5 credit per month
- 512MB RAM
- 1GB storage
- Enough for Platinum demo!

---

## 🐛 Troubleshooting

### Issue: Deployment Failed
```bash
# Check logs
railway logs

# Common fixes:
# 1. Check requirements.txt
# 2. Verify Procfile
# 3. Check environment variables
```

### Issue: Health Check Failing
```bash
# Verify port configuration
railway variables set PORT=8080

# Redeploy
railway up --detach
```

### Issue: Vault Sync Not Working
```bash
# Check Git credentials
railway variables list | grep GIT

# Verify repository access
git ls-remote https://github.com/username/vault.git
```

### Issue: Gmail Not Connecting
```bash
# Verify Gmail app password
# Check SMTP_USER and SMTP_PASS variables
railway variables list | grep SMTP
```

---

## 💰 Cost Estimation

**Railway Free Tier:**
- $5/month credit (free)
- Enough for ~500 hours/month
- Perfect for Platinum demo

**If you need more:**
- Hobby Plan: $5/month
- Unlimited projects
- 512MB RAM per service

---

## 📝 Next Steps After Deployment

1. **Monitor for 24 hours** - Ensure stability
2. **Test offline workflow** - Complete Platinum demo
3. **Record demo video** - Show cloud deployment
4. **Update submission** - Add Railway deployment info
5. **Submit Platinum tier** - Complete hackathon!

---

## 🎬 Demo Video Checklist

Show in your video:
- ✅ Railway dashboard (deployment active)
- ✅ Railway logs (cloud agent running)
- ✅ Health endpoint response
- ✅ Offline email workflow
- ✅ Vault sync in action
- ✅ Local approval process
- ✅ Email sent successfully

---

## 📞 Support

**Railway Documentation:**
- https://docs.railway.app/

**Railway Discord:**
- https://discord.gg/railway

**GitHub Issues:**
- Your repository issues tab

---

*Railway Deployment Guide - Platinum Tier*
*Last Updated: 2026-04-05*
