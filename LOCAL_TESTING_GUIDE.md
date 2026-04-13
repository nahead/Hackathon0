# 🧪 Local Testing Guide - Quick Verification

**Purpose:** Test all workflows locally before submission
**Time:** 15-20 minutes

---

## ✅ Pre-Test Checklist

```bash
# 1. Check Python version
python --version
# Should be 3.13+

# 2. Check dependencies
pip list | grep -E "anthropic|watchdog|GitPython|requests"

# 3. Check vault structure
ls AI_Employee_Vault/
# Should see: Pending_Approval/, Approved/, Done/, etc.

# 4. Check .env file exists
ls -la .env
# Should exist with credentials
```

---

## 🧪 Test 1: Local Orchestrator (5 min)

**What it tests:** Approval workflow, file monitoring

```bash
# Terminal 1: Start local orchestrator
cd C:\Users\nahead\Documents\GitHub\Hackathon0
python implementation/local_orchestrator.py
```

**Expected output:**
```
[LOCAL] LOCAL ORCHESTRATOR - PLATINUM TIER
[LOCAL] Vault Path: AI_Employee_Vault
[LOCAL] Monitoring: AI_Employee_Vault/Pending_Approval
[LOCAL] Local Orchestrator started. Monitoring for approvals...
```

**If you see errors:**
- Check vault path exists
- Check Python dependencies installed
- Check .env file has required variables

---

## 🧪 Test 2: Approval Workflow (3 min)

**What it tests:** End-to-end approval flow

```bash
# Terminal 2: Create test approval request
cd AI_Employee_Vault

# Create test file
cat > Pending_Approval/TEST_APPROVAL.md << 'EOF'
---
type: approval_request
action: test
created_by: manual_test
---

# Test Approval Request

This is a test to verify the approval workflow.

## To Approve
Move this file to /Approved folder.
EOF

# Check Terminal 1 - should see:
# [LOCAL] New approval request detected: TEST_APPROVAL.md
```

**Approve the request:**
```bash
# Move to Approved
mv Pending_Approval/TEST_APPROVAL.md Approved/

# Check Terminal 1 - should see:
# [LOCAL] Approved action detected: TEST_APPROVAL.md
# [LOCAL] Executing action...
# [LOCAL] Moved to Done: TEST_APPROVAL.md
```

**Verify completion:**
```bash
ls Done/TEST_APPROVAL.md
# File should exist in Done/
```

✅ **Test 2 PASSED** if file moved to Done/

---

## 🧪 Test 3: WhatsApp Integration (2 min)

**What it tests:** WhatsApp watcher and message handling

```bash
# Check WhatsApp watcher exists
ls implementation/whatsapp_watcher.py

# Test run (dry run mode)
python implementation/whatsapp_watcher.py

# Expected: Script runs without errors
# Note: Won't send actual messages without WhatsApp session
```

✅ **Test 3 PASSED** if script runs without errors

---

## 🧪 Test 4: Email Integration (2 min)

**What it tests:** Email monitoring and processing

```bash
# Check email integration
ls implementation/integrated_system.py

# Verify .env has email credentials
grep -E "SMTP_USER|SMTP_PASS" .env

# Expected: Should show your email credentials (masked)
```

✅ **Test 4 PASSED** if credentials exist

---

## 🧪 Test 5: LinkedIn Integration (2 min)

**What it tests:** LinkedIn posting capability

```bash
# Check LinkedIn files
ls implementation/linkedin_api_poster.py
ls implementation/linkedin_content_generator.py

# Verify LinkedIn token
grep "LINKEDIN_ACCESS_TOKEN" .env

# Expected: Token should exist
```

✅ **Test 5 PASSED** if files and token exist

---

## 🧪 Test 6: MCP Servers (3 min)

**What it tests:** MCP server configuration

```bash
# Check MCP servers exist
ls mcp_servers/email_mcp/index.js
ls mcp_servers/whatsapp_mcp/index.js
ls mcp_servers/odoo_mcp/index.js

# Check MCP config
cat .claude/mcp_config.json

# Expected: Should show 5 MCP servers configured
```

✅ **Test 6 PASSED** if all MCP servers exist

---

## 🧪 Test 7: Odoo Integration (3 min)

**What it tests:** Odoo local connection

```bash
# Check Odoo is running
curl http://localhost:8070/web/database/selector
# Expected: HTML response (Odoo login page)

# Test Odoo connection script
python test_odoo_connection.py

# Expected output:
# ✓ Authentication successful
# ✓ User ID: 2
# ✓ Customer creation: Working
# ✓ Invoice access: Working
```

**If Odoo not running:**
```bash
# Start Odoo (if using Docker)
docker start odoo

# Wait 30 seconds, then retry
```

✅ **Test 7 PASSED** if connection successful

---

## 🧪 Test 8: Agent Skills (2 min)

**What it tests:** Claude Code skills configuration

```bash
# Check Agent Skills
ls AI_Employee_Vault/.claude/skills/

# Count skills
ls AI_Employee_Vault/.claude/skills/*.md | wc -l
# Expected: 19 skills

# Verify key skills exist
ls AI_Employee_Vault/.claude/skills/whatsapp-handler.md
ls AI_Employee_Vault/.claude/skills/email-processor.md
ls AI_Employee_Vault/.claude/skills/linkedin-manager.md
ls AI_Employee_Vault/.claude/skills/odoo-accounting.md
```

✅ **Test 8 PASSED** if 19 skills exist

---

## 🧪 Test 9: Cloud Deployment (1 min)

**What it tests:** Cloud orchestrator is live

```bash
# Check cloud health
curl https://ai-employee-cloud.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-04-13T...",
#   "services": {
#     "orchestrator": "running",
#     "vault_sync": "active"
#   }
# }
```

✅ **Test 9 PASSED** if status is "healthy"

---

## 🧪 Test 10: Vault Structure (1 min)

**What it tests:** Complete vault organization

```bash
# Check all required folders
cd AI_Employee_Vault
ls -la

# Required folders:
# - Needs_Action/
# - Pending_Approval/
# - Approved/
# - Done/
# - Plans/
# - Logs/
# - In_Progress/

# Check key files
ls Dashboard.md
ls Company_Handbook.md
ls Business_Goals.md
```

✅ **Test 10 PASSED** if all folders and files exist

---

## 📊 Test Results Summary

| Test | Component | Status |
|------|-----------|--------|
| 1 | Local Orchestrator | ⬜ |
| 2 | Approval Workflow | ⬜ |
| 3 | WhatsApp Integration | ⬜ |
| 4 | Email Integration | ⬜ |
| 5 | LinkedIn Integration | ⬜ |
| 6 | MCP Servers | ⬜ |
| 7 | Odoo Integration | ⬜ |
| 8 | Agent Skills | ⬜ |
| 9 | Cloud Deployment | ⬜ |
| 10 | Vault Structure | ⬜ |

**Mark ✅ for passed, ❌ for failed**

---

## 🚨 Common Issues & Fixes

### Issue 1: Local orchestrator won't start
**Fix:**
```bash
pip install watchdog python-dotenv
```

### Issue 2: Odoo connection fails
**Fix:**
```bash
# Check Odoo is running
docker ps | grep odoo

# Start if not running
docker start odoo
```

### Issue 3: Cloud health check fails
**Fix:**
- Check Render.com dashboard
- Verify service is running
- Check deployment logs

### Issue 4: Missing .env file
**Fix:**
```bash
# Create .env from template
cp .env.example .env
# Edit with your credentials
nano .env
```

---

## ✅ Final Verification

**All tests passed?** Your system is ready for submission! 🎉

**Some tests failed?** Fix the issues and re-run failed tests.

**Ready to submit?**
1. Commit any final changes
2. Push to GitHub
3. Fill submission form: https://forms.gle/JR9T1SJq5rmQyGkGA

---

**Generated:** 2026-04-13
**Purpose:** Pre-submission verification
**Time Required:** 15-20 minutes
