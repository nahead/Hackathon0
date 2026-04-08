# Deployment Guide

## Local Deployment

### Prerequisites
- Python 3.8+
- Node.js 16+ (for some integrations)
- Git

### Installation

1. Clone repository:
```bash
git clone <repository-url>
cd Hackathon0
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Initialize vault:
```bash
python initialize_vault.py
```

### Running Locally

Start the email workflow:
```bash
python test_email_workflow.py
```

Start LinkedIn posting:
```bash
python linkedin_api_poster.py
```

Start autonomous loop:
```bash
python agent_skills/ralph_wiggum_loop.py
```

## Cloud Deployment (Render.com)

### Prerequisites
- Render.com account
- GitHub repository

### Deployment Steps

1. Push code to GitHub:
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

2. Create new Web Service on Render:
- Connect GitHub repository
- Build command: `pip install -r requirements.txt`
- Start command: `python cloud_deployment/render_deploy.py`

3. Configure environment variables in Render dashboard:
- Add all variables from .env file
- Set NODE_ENV=production

4. Deploy:
- Render will automatically deploy on push
- Monitor logs for deployment status

### Health Monitoring

Health check endpoint:
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "services": {
    "vault": true,
    "email": true,
    "linkedin": true
  }
}
```

### Error Recovery

The system includes automatic error recovery:
- 3 retry attempts for failed operations
- 5-second delay between retries
- Automatic service restart on failure
- Health monitoring every 60 seconds

### Scaling

To scale the deployment:
1. Increase instance count in Render dashboard
2. Configure load balancing
3. Use Redis for distributed state (optional)

## Monitoring

### Logs

View logs in Render dashboard or via CLI:
```bash
render logs -s <service-name>
```

### Audit Trail

All actions are logged in:
```
AI_Employee_Vault/Audit_Logs/audit_YYYY-MM-DD.jsonl
```

### CEO Briefings

Daily briefings generated in:
```
AI_Employee_Vault/CEO_Briefings/CEO_Briefing_YYYY-MM-DD.md
```

## Troubleshooting

### Common Issues

1. **LinkedIn posting fails**
   - Check access token validity (59 days)
   - Regenerate token: `python setup_linkedin_oauth.py`

2. **Email not sending**
   - Verify SMTP credentials in .env
   - Check Gmail app password

3. **Vault permissions**
   - Ensure write permissions on vault directory
   - Check disk space

### Support

For issues, check:
- Audit logs in vault
- Render deployment logs
- Error recovery logs

## Backup & Recovery

### Backup

Create backup:
```bash
python agent_skills/backup_manager.py
```

### Restore

Restore from backup:
```bash
python agent_skills/backup_manager.py --restore <backup_id>
```

## Security

### Best Practices

1. Never commit .env file
2. Rotate credentials regularly
3. Use environment variables for secrets
4. Enable 2FA on all accounts
5. Monitor audit logs daily

### Credential Management

Store credentials in:
- Local: .env file
- Cloud: Render environment variables
- Never hardcode in source code
