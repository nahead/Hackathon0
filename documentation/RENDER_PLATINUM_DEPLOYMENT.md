# Render Deployment Guide - Platinum Tier

## Overview

Deploy Cloud Orchestrator to Render.com for 24/7 operation with Cloud/Local split architecture.

---

## Architecture

```
┌─────────────────────────────────────┐
│   Render.com (Cloud Orchestrator)  │
│   - Email triage                    │
│   - Social media drafts             │
│   - Draft-only mode                 │
└──────────────┬──────────────────────┘
               │
               ▼ (Git Sync)
┌─────────────────────────────────────┐
│   Vault Git Repository              │
│   - Pending_Approval/               │
│   - Needs_Action/cloud/             │
└──────────────┬──────────────────────┘
               │
               ▼ (Git Pull)
┌─────────────────────────────────────┐
│   Local Machine (Local Orchestrator)│
│   - Approvals                       │
│   - WhatsApp                        │
│   - Final actions                   │
└─────────────────────────────────────┘
```

---

## Prerequisites

1. Vault pushed to separate GitHub repository
2. Render.com account
3. GitHub access token (for vault sync)

---

## Step 1: Create Vault Repository

### 1.1 Create New GitHub Repository

Go to: https://github.com/new

**Settings:**
- Name: `ai-employee-vault`
- Description: AI Employee Vault - Platinum Tier
- Private: ✅ (recommended)

**Click:** Create repository

### 1.2 Push Vault to GitHub

```bash
cd AI_Employee_Vault

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git

# Push
git push -u origin main
```

---

## Step 2: Update Cloud Orchestrator for Render

### 2.1 Modify cloud_orchestrator.py

Add vault cloning and Git configuration:

```python
import os
import subprocess
from pathlib import Path

VAULT_REPO_URL = os.getenv('VAULT_REPO_URL')
VAULT_PATH = Path('./AI_Employee_Vault')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def setup_vault():
    """Clone vault if not exists, configure Git"""
    if not VAULT_PATH.exists():
        # Clone vault
        repo_url_with_token = VAULT_REPO_URL.replace(
            'https://',
            f'https://{GITHUB_TOKEN}@'
        )
        subprocess.run(['git', 'clone', repo_url_with_token, str(VAULT_PATH)])
    
    # Configure Git
    subprocess.run(['git', 'config', '--global', 'user.email', 'cloud@aiemployee.com'])
    subprocess.run(['git', 'config', '--global', 'user.name', 'Cloud Agent'])
```

---

## Step 3: Configure Render Deployment

### 3.1 Update render.yaml

```yaml
services:
  # Existing WhatsApp webhook
  - type: web
    name: whatsapp-webhook
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python implementation/integrated_system.py
    envVars:
      - key: WHATSAPP_ACCESS_TOKEN
        sync: false
      - key: WHATSAPP_PHONE_NUMBER_ID
        sync: false
      # ... other env vars

  # New: Cloud Orchestrator
  - type: worker
    name: cloud-orchestrator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python implementation/cloud_orchestrator.py
    envVars:
      - key: VAULT_REPO_URL
        value: https://github.com/YOUR_USERNAME/ai-employee-vault.git
      - key: GITHUB_TOKEN
        sync: false
      - key: MODE
        value: cloud
      - key: ANTHROPIC_API_KEY
        sync: false
      # ... other env vars
```

### 3.2 Add to requirements.txt

```txt
watchdog==3.0.0
GitPython==3.1.40
```

---

## Step 4: Deploy to Render

### 4.1 Via Render Dashboard

1. Go to: https://dashboard.render.com
2. Click: **New +** → **Background Worker**
3. Connect your GitHub repository
4. Configure:
   - **Name:** cloud-orchestrator
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python implementation/cloud_orchestrator.py`

### 4.2 Add Environment Variables

**Required:**
```
VAULT_REPO_URL=https://github.com/YOUR_USERNAME/ai-employee-vault.git
GITHUB_TOKEN=ghp_your_github_token
MODE=cloud
ANTHROPIC_API_KEY=your_api_key
VAULT_PATH=./AI_Employee_Vault
```

**Optional (for email/social):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASS=your_password
LINKEDIN_ACCESS_TOKEN=...
TWITTER_BEARER_TOKEN=...
```

### 4.3 Deploy

Click: **Create Background Worker**

---

## Step 5: Verify Deployment

### 5.1 Check Logs

```bash
# In Render dashboard
# Go to: cloud-orchestrator → Logs

# Should see:
[CLOUD] CLOUD ORCHESTRATOR - PLATINUM TIER (DRAFT-ONLY)
[CLOUD] Vault Path: ./AI_Employee_Vault
[CLOUD] Mode: Draft-only (no final actions)
[CLOUD] Cloud Orchestrator started
```

### 5.2 Test Vault Sync

```bash
# On local machine
cd AI_Employee_Vault

# Create test file
echo "Test from local" > test_sync.txt
git add test_sync.txt
git commit -m "Test sync"
git push origin main

# Wait 60 seconds

# Check Render logs - should see:
[CLOUD] Syncing vault from Git...
[CLOUD] Vault synced successfully
```

---

## Step 6: Run Local Orchestrator

### 6.1 On Your Local Machine

```bash
# Clone vault (if not already)
git clone https://github.com/YOUR_USERNAME/ai-employee-vault.git AI_Employee_Vault

# Run local orchestrator
python implementation/local_orchestrator.py
```

**Expected output:**
```
[LOCAL] LOCAL ORCHESTRATOR - PLATINUM TIER
[LOCAL] Vault Path: AI_Employee_Vault
[LOCAL] Monitoring: AI_Employee_Vault/Pending_Approval
[LOCAL] Local Orchestrator started. Monitoring for approvals...
```

---

## Step 7: Test End-to-End Flow

### 7.1 Simulate Cloud Draft Creation

```bash
# On Render (via logs or manual trigger)
# Cloud creates draft in Pending_Approval/

# Or manually test:
cd AI_Employee_Vault
echo "---
type: approval_request
action: email
---
Test email from cloud" > Pending_Approval/TEST_CLOUD_DRAFT.md

git add Pending_Approval/TEST_CLOUD_DRAFT.md
git commit -m "Cloud: Test draft"
git push origin main
```

### 7.2 Local Pulls and Detects

```bash
# Local orchestrator should:
# 1. Pull from Git (every 60 seconds)
# 2. Detect new file in Pending_Approval/
# 3. Log: [LOCAL] New approval request detected: TEST_CLOUD_DRAFT.md
```

### 7.3 Approve and Execute

```bash
# Move to Approved
mv AI_Employee_Vault/Pending_Approval/TEST_CLOUD_DRAFT.md AI_Employee_Vault/Approved/

# Local should:
# 1. Detect approved file
# 2. Execute action
# 3. Move to Done/
# 4. Push to Git
```

---

## Troubleshooting

### Issue: Cloud can't clone vault
**Solution:** Check GitHub token permissions
```bash
# Token needs: repo (full control)
# Create at: https://github.com/settings/tokens
```

### Issue: Git push fails on Render
**Solution:** Configure Git credentials
```python
# In cloud_orchestrator.py
subprocess.run(['git', 'config', '--global', 'user.email', 'cloud@ai.com'])
subprocess.run(['git', 'config', '--global', 'user.name', 'Cloud Agent'])
```

### Issue: Local not detecting changes
**Solution:** Check sync interval
```python
# In local_orchestrator.py
time.sleep(60)  # Sync every 60 seconds
```

---

## Monitoring

### Render Dashboard
- **Logs:** Real-time cloud orchestrator logs
- **Metrics:** CPU, memory usage
- **Health:** Service status

### Local Machine
- **Terminal:** Local orchestrator output
- **Vault:** Git log shows sync activity

```bash
cd AI_Employee_Vault
git log --oneline -10
```

---

## Cost

**Render.com:**
- Background Worker: $7/month (or Free tier with limitations)
- WhatsApp Webhook: Already deployed

**GitHub:**
- Private repository: Free (up to 500MB)

**Total:** $0-7/month

---

## Next Steps

1. ✅ Deploy cloud orchestrator to Render
2. ✅ Run local orchestrator on your machine
3. ✅ Test end-to-end flow
4. ⏭️ Record Platinum demo
5. ⏭️ Submit Platinum tier

---

**Generated:** 2026-04-12
**Status:** Ready for Render deployment
