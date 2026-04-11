# AI Employee System - Deployment Guide

## Production Deployment to Render.com

### Prerequisites
- GitHub repository with all code
- Render.com account (free tier)
- All API credentials ready

### Environment Variables Required

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password

# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=your_permanent_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_id
WHATSAPP_ALLOWED_NUMBERS=923122955972,923242767352

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_URN=your_person_urn

# Facebook API
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
FACEBOOK_PAGE_ID=your_page_id

# Vault Configuration
VAULT_PATH=../AI_Employee_Vault
```

### Deployment Steps

1. **Push to GitHub:**
```bash
git add .
git commit -m "Production-ready AI Employee system"
git push origin main
```

2. **Create Render Web Service:**
- Go to: https://dashboard.render.com/
- Click "New +" → "Web Service"
- Connect your GitHub repository
- Configure:
  - Name: ai-employee-system
  - Environment: Python 3
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python implementation/railway_all_in_one.py`
  - Instance Type: Free

3. **Add Environment Variables:**
- In Render dashboard, go to Environment
- Add all variables from above
- Save changes

4. **Deploy:**
- Render will automatically deploy
- Check logs for successful startup
- Access health check: `https://your-app.onrender.com/health`

### System Features

✅ **Working Features:**
- WhatsApp Cloud API (with safety whitelist)
- LinkedIn API posting
- Email monitoring and sending
- Facebook posting (token refresh needed)
- Vault synchronization via Git
- 24/7 orchestrator
- Health monitoring dashboard
- Audit logging

### Safety Features

1. **Whitelist Protection:**
   - Only approved numbers receive WhatsApp messages
   - Add clients to WHATSAPP_ALLOWED_NUMBERS

2. **Human-in-the-Loop:**
   - Sensitive actions require approval
   - Files moved to /Approved folder before execution

3. **Audit Logging:**
   - All actions logged to /Logs folder
   - Daily JSON logs with timestamps

### Monitoring

**Health Check Endpoint:**
```
GET https://your-app.onrender.com/health
```

**Dashboard:**
```
GET https://your-app.onrender.com/
```

**Live Logs:**
```
GET https://your-app.onrender.com/logs
```

### Maintenance

**Daily:**
- Check dashboard for system health
- Review pending approvals in vault

**Weekly:**
- Review audit logs
- Check API token expiration
- Update whitelist if needed

**Monthly:**
- Rotate credentials
- Review automation effectiveness
- Update business rules

### Troubleshooting

**Issue: Messages not sending**
- Check API tokens not expired
- Verify recipient in whitelist
- Check logs for errors

**Issue: Vault not syncing**
- Verify Git credentials
- Check network connectivity
- Review sync logs

**Issue: Service offline**
- Check Render dashboard
- Review deployment logs
- Verify environment variables

### Cost

**Free Tier Limits:**
- Render.com: Free (with sleep after 15min inactivity)
- WhatsApp: 1,000 conversations/month free
- LinkedIn: Free API usage
- Gmail: Free
- Total: $0/month

**Paid Upgrade (Optional):**
- Render: $7/month (no sleep)
- WhatsApp: ~$0.005-0.09 per conversation after 1,000
- Total: ~$7-15/month for production use

### Support

For issues or questions:
- Check logs: `/Logs` folder in vault
- Review documentation: `/documentation` folder
- GitHub issues: Create issue in repository

---

**System Status:** ✅ Production Ready
**Last Updated:** 2026-04-11
**Version:** 1.0.0
