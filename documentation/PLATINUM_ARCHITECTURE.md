# 💎 Platinum Tier Architecture Guide

## Overview

Platinum Tier implements a **Cloud/Local split architecture** where:
- **Cloud Agent** runs 24/7 on Render.com (draft-only mode)
- **Local Agent** runs on your machine (approvals and final actions)
- **Vault** syncs via Git between both agents

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  CLOUD AGENT (Render.com)                   │
│                    DRAFT-ONLY MODE                          │
├─────────────────────────────────────────────────────────────┤
│  • Email triage and draft responses                         │
│  • Social media draft posts                                 │
│  • Data collection and monitoring                           │
│  • Writes to: /Needs_Action/cloud/                          │
│  • Writes to: /Pending_Approval/ (drafts)                   │
│  • NO final actions (no send/post)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    GIT VAULT SYNC                           │
│              (AI_Employee_Vault Repository)                 │
├─────────────────────────────────────────────────────────────┤
│  • Cloud pushes: Drafts, plans, data                        │
│  • Local pushes: Approvals, completions                     │
│  • Syncs every 60 seconds                                   │
│  • Security: Secrets never sync (.gitignore)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LOCAL AGENT (Your Machine)                 │
│                   APPROVAL & EXECUTION                      │
├─────────────────────────────────────────────────────────────┤
│  • Monitors /Pending_Approval/                              │
│  • Human reviews and approves                               │
│  • Executes approved actions via MCP                        │
│  • WhatsApp session (local only)                            │
│  • Banking/payment operations                               │
│  • Writes to: /Approved/, /Done/                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Work-Zone Specialization

### Cloud Agent Owns:
1. **Email Triage**
   - Monitor Gmail for new emails
   - Classify: urgent, routine, spam
   - Generate draft responses
   - Create approval requests

2. **Social Media Drafts**
   - Generate LinkedIn post drafts
   - Generate Twitter post drafts
   - Generate Facebook/Instagram drafts
   - Schedule suggestions

3. **Data Collection**
   - Monitor business metrics
   - Track social media analytics
   - Prepare CEO briefing data

### Local Agent Owns:
1. **Approvals**
   - Monitor /Pending_Approval/
   - Wait for human review
   - Execute approved actions

2. **WhatsApp Operations**
   - WhatsApp session (never syncs)
   - Send WhatsApp messages
   - Handle WhatsApp webhooks

3. **Banking/Payments**
   - Payment operations
   - Banking credentials (never sync)
   - Financial transactions

4. **Final Actions**
   - Send emails via MCP
   - Post to social media
   - Execute all approved operations

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── cloud/          # Cloud agent tasks
│   └── local/          # Local agent tasks
├── Plans/
│   ├── cloud/          # Cloud agent plans
│   └── local/          # Local agent plans
├── In_Progress/
│   ├── cloud/          # Cloud agent working
│   └── local/          # Local agent working
├── Pending_Approval/   # Drafts awaiting approval
├── Approved/           # Approved actions (Local executes)
├── Done/               # Completed actions
└── Rejected/           # Rejected actions
```

---

## Claim-by-Move Rule

**Prevents double-work between agents:**

1. Agent sees task in `/Needs_Action/`
2. Agent moves task to `/In_Progress/<agent>/`
3. Other agents ignore tasks in `/In_Progress/`
4. When complete, move to `/Done/`

**Example:**
```bash
# Cloud agent claims task
mv Needs_Action/cloud/EMAIL_123.md In_Progress/cloud/EMAIL_123.md

# Local agent sees it's claimed, ignores it
# Cloud completes, moves to Pending_Approval
mv In_Progress/cloud/EMAIL_123.md Pending_Approval/EMAIL_DRAFT_123.md
```

---

## Security Rules

### Secrets Never Sync

**Vault .gitignore includes:**
- `.env` files
- Credentials (*.json)
- Sessions (WhatsApp, browser)
- Banking data
- Private keys

**Cloud Agent:**
- Has: Email API keys, Social media tokens
- Does NOT have: WhatsApp session, Banking credentials

**Local Agent:**
- Has: All credentials
- Executes: All final actions

---

## Vault Sync Flow

### Cloud → Git → Local

1. **Cloud Agent** creates draft:
   ```
   /Pending_Approval/EMAIL_DRAFT_20260412.md
   ```

2. **Cloud Agent** syncs to Git:
   ```bash
   git add .
   git commit -m "Cloud: Email draft created"
   git push origin main
   ```

3. **Local Agent** pulls from Git:
   ```bash
   git pull origin main
   ```

4. **Human** reviews and approves:
   ```bash
   mv Pending_Approval/EMAIL_DRAFT_20260412.md Approved/
   ```

5. **Local Agent** executes and completes:
   ```bash
   # Execute via MCP
   # Move to Done
   mv Approved/EMAIL_DRAFT_20260412.md Done/
   ```

6. **Local Agent** syncs to Git:
   ```bash
   git add .
   git commit -m "Local: Email sent"
   git push origin main
   ```

---

## Setup Instructions

### 1. Create Vault Git Repository

```bash
cd AI_Employee_Vault
git init
git add .
git commit -m "Initial vault state"

# Create GitHub repository
# Then push
git remote add origin <your-vault-repo-url>
git push -u origin main
```

### 2. Deploy Cloud Agent

**On Render.com:**
```bash
# Add to render.yaml
services:
  - type: web
    name: cloud-orchestrator
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python implementation/cloud_orchestrator.py
    envVars:
      - key: VAULT_REPO_URL
        value: <your-vault-repo-url>
      - key: MODE
        value: cloud
```

### 3. Run Local Agent

**On your machine:**
```bash
# Install dependencies
pip install watchdog python-dotenv

# Run local orchestrator
python implementation/local_orchestrator.py
```

### 4. Configure Vault Sync

**Add to crontab (Mac/Linux):**
```bash
*/1 * * * * cd /path/to/AI_Employee_Vault && python ../implementation/vault_sync.py
```

**Or use Task Scheduler (Windows)**

---

## Platinum Demo Scenario

**Requirement:** Email arrives while Local is offline → Cloud drafts → Local approves → Local sends

### Demo Steps:

1. **Setup:**
   - Cloud Agent running on Render
   - Local Agent stopped (offline)
   - Vault synced

2. **Email Arrives:**
   - Cloud Agent detects new email
   - Cloud generates draft response
   - Cloud creates: `/Pending_Approval/EMAIL_DRAFT_123.md`
   - Cloud pushes to Git

3. **Local Comes Online:**
   - Local Agent starts
   - Local pulls from Git
   - Local detects new approval request
   - Logs: "New approval request: EMAIL_DRAFT_123.md"

4. **Human Approves:**
   - User reviews draft
   - User moves to `/Approved/`

5. **Local Executes:**
   - Local detects approved file
   - Local sends email via MCP
   - Local moves to `/Done/`
   - Local pushes to Git

6. **Result:**
   - Email sent successfully
   - Full audit trail in vault
   - Cloud and Local in sync

---

## Testing Platinum Tier

### Test 1: Cloud Draft Creation
```bash
# Run cloud orchestrator
python implementation/cloud_orchestrator.py

# Verify: Check Pending_Approval/ for drafts
ls AI_Employee_Vault/Pending_Approval/
```

### Test 2: Local Approval Flow
```bash
# Run local orchestrator
python implementation/local_orchestrator.py

# Move draft to Approved
mv AI_Employee_Vault/Pending_Approval/EMAIL_DRAFT_123.md AI_Employee_Vault/Approved/

# Verify: Check Done/ for completed action
ls AI_Employee_Vault/Done/
```

### Test 3: Vault Sync
```bash
# Run sync script
python implementation/vault_sync.py

# Verify: Check Git log
cd AI_Employee_Vault
git log --oneline -5
```

### Test 4: Offline Scenario
```bash
# 1. Stop local agent
# 2. Cloud creates draft
# 3. Start local agent
# 4. Verify local pulls draft
# 5. Approve and execute
```

---

## Troubleshooting

### Issue: Vault sync conflicts
**Solution:** 
```bash
cd AI_Employee_Vault
git pull --rebase origin main
```

### Issue: Cloud agent can't push
**Solution:** Configure Git credentials on Render
```bash
git config --global user.email "cloud@aiemployee.com"
git config --global user.name "Cloud Agent"
```

### Issue: Local agent not detecting approvals
**Solution:** Check watchdog is running
```bash
pip install watchdog
python implementation/local_orchestrator.py
```

---

## Platinum Tier Checklist

- [x] All Gold requirements (100%)
- [x] Cloud 24/7 deployment (Render.com)
- [x] Work-zone specialization (Cloud/Local split)
- [x] Cloud owns: Email triage + drafts
- [x] Local owns: Approvals + WhatsApp
- [x] Vault sync via Git
- [x] Security rules (secrets never sync)
- [x] Cloud deployment complete
- [ ] Odoo on Cloud VM (optional - 11% remaining)

---

## Next Steps

1. **Deploy Odoo to Cloud VM**
   - Oracle Cloud Free Tier
   - Install Odoo Community
   - Configure HTTPS
   - Update MCP server

2. **Record Platinum Demo**
   - Show offline scenario
   - Show Cloud/Local handoff
   - Show approval workflow
   - 5-10 minute video

3. **Submit Platinum Tier**
   - Update README
   - Submit form
   - Include demo video

---

**Generated:** 2026-04-12
**Status:** Platinum Tier 89% Complete (8/9 requirements met, Odoo cloud optional)
