# Platinum Tier - Quick Deployment Checklist

## ✅ Prerequisites
- [x] Gold Tier 100% complete
- [x] Cloud/Local architecture implemented
- [x] Render account with existing deployment
- [ ] Vault GitHub repository
- [ ] GitHub personal access token

---

## 📋 Deployment Steps

### 1. Create Vault Repository (5 min)

**Go to:** https://github.com/new

**Settings:**
- Name: `ai-employee-vault`
- Description: AI Employee Vault - Platinum Tier
- Private: ✅ (recommended)
- Initialize: ❌ (we already have files)

**Click:** Create repository

**Copy the URL:** `https://github.com/YOUR_USERNAME/ai-employee-vault.git`

### 2. Push Vault to GitHub (2 min)

```bash
cd AI_Employee_Vault

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git

# Push
git push -u origin main
```

**Verify:** Go to your repository and see all vault files

### 3. Create GitHub Token (2 min)

**Go to:** https://github.com/settings/tokens

**Click:** Generate new token (classic)

**Settings:**
- Note: `ai-employee-vault-access`
- Expiration: 90 days (or No expiration)
- Scopes: ✅ `repo` (full control of private repositories)

**Click:** Generate token

**Copy the token:** `ghp_xxxxxxxxxxxxxxxxxxxx`

⚠️ **Save it now** - you won't see it again!

### 4. Add Cloud Orchestrator to Render (5 min)

**Go to:** https://dashboard.render.com

**Your existing service:** ai-employee-cloud

**Add new service:**
1. Click: **New +** → **Background Worker**
2. Select repository: `Hackathon0`
3. Configure:
   - **Name:** `cloud-orchestrator-platinum`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python implementation/cloud_orchestrator.py`

4. **Environment Variables:**
   ```
   MODE=cloud
   VAULT_REPO_URL=https://github.com/YOUR_USERNAME/ai-employee-vault.git
   GITHUB_TOKEN=ghp_your_token_here
   VAULT_PATH=./AI_Employee_Vault
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

5. Click: **Create Background Worker**

### 5. Verify Deployment (2 min)

**Check Render Logs:**

Should see:
```
[CLOUD] CLOUD ORCHESTRATOR - PLATINUM TIER (DRAFT-ONLY)
[CLOUD] Git configured successfully
[CLOUD] Cloning vault from https://github.com/...
[CLOUD] Vault cloned successfully
[CLOUD] Cloud Orchestrator started
[CLOUD] Monitoring for tasks...
```

### 6. Run Local Orchestrator (1 min)

**On your local machine:**

```bash
# Clone vault (if not already)
git clone https://github.com/YOUR_USERNAME/ai-employee-vault.git AI_Employee_Vault

# Run local orchestrator
python implementation/local_orchestrator.py
```

**Should see:**
```
[LOCAL] LOCAL ORCHESTRATOR - PLATINUM TIER
[LOCAL] Monitoring: AI_Employee_Vault/Pending_Approval
[LOCAL] Local Orchestrator started. Monitoring for approvals...
```

---

## 🧪 Test End-to-End (5 min)

### Test 1: Cloud Creates Draft

**Manually simulate:**
```bash
cd AI_Employee_Vault

# Create test draft
echo "---
type: approval_request
action: email
---
Test email from cloud" > Pending_Approval/TEST_CLOUD_DRAFT.md

git add Pending_Approval/TEST_CLOUD_DRAFT.md
git commit -m "Test: Cloud draft"
git push origin main
```

### Test 2: Local Detects and Approves

**Local orchestrator should:**
1. Pull from Git (within 60 seconds)
2. Log: `[LOCAL] New approval request detected: TEST_CLOUD_DRAFT.md`

**Approve it:**
```bash
mv AI_Employee_Vault/Pending_Approval/TEST_CLOUD_DRAFT.md AI_Employee_Vault/Approved/
```

**Local should:**
1. Log: `[LOCAL] Approved action detected: TEST_CLOUD_DRAFT.md`
2. Execute action
3. Move to Done/
4. Push to Git

### Test 3: Verify Completion

```bash
ls AI_Employee_Vault/Done/TEST_CLOUD_DRAFT.md
# Should exist

git log --oneline -3
# Should show local agent commit
```

---

## ✅ Success Criteria

- [ ] Vault repository created on GitHub
- [ ] Vault pushed successfully
- [ ] GitHub token created
- [ ] Cloud orchestrator deployed to Render
- [ ] Cloud orchestrator logs show "started"
- [ ] Local orchestrator running on your machine
- [ ] End-to-end test passed

---

## 🎯 Current Status

**Platinum Tier:** 78% → 89% (after deployment)

**What's Complete:**
- ✅ Cloud/Local architecture
- ✅ Vault sync automation
- ✅ Work-zone specialization
- ✅ Security rules
- ✅ Cloud deployment (Render)
- ⏭️ Odoo cloud (optional)
- ⏭️ Demo video (optional)

---

## 💡 Quick Commands Reference

```bash
# Check vault status
cd AI_Employee_Vault && git status

# Sync vault manually
cd AI_Employee_Vault && git pull && git push

# View local orchestrator logs
python implementation/local_orchestrator.py

# Check Render logs
# Go to: https://dashboard.render.com → cloud-orchestrator-platinum → Logs
```

---

**Time to Complete:** 15-20 minutes
**Difficulty:** Easy (follow steps)
**Result:** Platinum Tier 89% complete with live Cloud/Local split
