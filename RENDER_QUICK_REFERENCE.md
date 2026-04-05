# Render.com Quick Reference

## 🚀 Quick Deploy (5 Commands)

```bash
# 1. Commit and push
git add .
git commit -m "Render deployment ready"
git push origin main

# 2. Go to Render
# https://render.com

# 3. New Web Service
# Connect your GitHub repo

# 4. Configure
# Build: pip install -r railway-requirements.txt
# Start: python railway_all_in_one.py

# 5. Add Environment Variables
# See list below
```

## 🔧 Required Environment Variables

```
AGENT_TYPE=cloud
SMTP_USER=naheadj@gmail.com
SMTP_PASS=encgwiysqpyhtsji
VAULT_REPO_URL=https://github.com/nahead/ai-employee-vault.git
GIT_USERNAME=nahead
GIT_TOKEN=your-github-token
PYTHON_VERSION=3.13.9
```

## 📊 Monitoring Commands

```bash
# Health check
curl https://your-app.onrender.com/health

# Keep alive (prevent sleep)
watch -n 600 curl https://your-app.onrender.com/health
```

## 🐛 Quick Troubleshooting

**Service sleeping?**
- Ping health endpoint to wake

**Build failed?**
- Check railway-requirements.txt exists
- Verify Python version

**Crashed?**
- Check environment variables
- View logs in dashboard

## ⚡ One-Line Health Check

```bash
curl https://your-app.onrender.com/health && echo "✅ Service is awake"
```

## 📝 Deployment Checklist

- [ ] GitHub repo pushed
- [ ] Render account created
- [ ] Vault repository created
- [ ] GitHub token generated
- [ ] Web service created
- [ ] Environment variables set
- [ ] Service deployed
- [ ] Health check passing
- [ ] Logs showing activity

## 🎯 Success Criteria

- ✅ Service status: Live
- ✅ Health endpoint: 200 OK
- ✅ Logs: No errors
- ✅ Email monitoring: Active

## 📞 Quick Links

- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

---
*Render.com Quick Reference - Free Tier*
