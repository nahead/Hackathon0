# Railway Deployment - Quick Reference Card

## 🚀 Quick Start (5 Commands)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Set environment variables (minimum required)
railway variables set AGENT_TYPE=cloud
railway variables set SMTP_USER=naheadj@gmail.com
railway variables set SMTP_PASS=your-gmail-app-password

# 5. Deploy
railway up
```

## 📊 Monitoring Commands

```bash
# View logs
railway logs --follow

# Check status
railway status

# Get app URL
railway domain

# Test health
curl $(railway domain)/health
```

## 🔧 Configuration Commands

```bash
# List all variables
railway variables

# Set a variable
railway variables set KEY=value

# Delete a variable
railway variables delete KEY

# Open dashboard
railway open
```

## 🐛 Troubleshooting Commands

```bash
# Restart deployment
railway restart

# Redeploy
railway up --detach

# View build logs
railway logs --build

# Check service info
railway service
```

## 📝 Required Environment Variables

```
AGENT_TYPE=cloud
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
VAULT_REPO_URL=https://github.com/username/vault.git
GIT_USERNAME=your-username
GIT_TOKEN=your-token
```

## 🎯 Success Checklist

- [ ] Railway CLI installed
- [ ] Logged in to Railway
- [ ] Project initialized
- [ ] Environment variables set
- [ ] Deployed successfully
- [ ] Health endpoint responding
- [ ] Logs showing activity
- [ ] Vault sync working

## 📞 Quick Links

- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app/
- Status: https://status.railway.app/

## ⚡ One-Line Deploy (After setup)

```bash
railway up && railway logs --follow
```

---
*Railway Quick Reference - Platinum Tier*
