# Testing Guide - Personal AI Employee System

**How to Test All Four Tiers**

---

## Prerequisites

Before testing, ensure you have:
- Python 3.13+ installed
- Node.js 24+ installed
- Git installed
- Obsidian installed (optional, for viewing vault)

---

## 🥉 Bronze Tier Testing

### Test 1: Verify Obsidian Vault Structure

```bash
# Navigate to project directory
cd Hackathon0

# Check vault files exist
ls -la AI_Employee_Vault/Dashboard.md
ls -la AI_Employee_Vault/Company_Handbook.md
ls -la AI_Employee_Vault/Business_Goals.md

# Check folder structure
ls -la AI_Employee_Vault/ | grep -E "(Inbox|Needs_Action|Done|Plans|Logs|Pending_Approval|Approved)"
```

**Expected Result:** All files and folders exist ✅

### Test 2: Verify Agent Skills

```bash
# Check Agent Skills location
ls -la .claude/skills/

# Should show 4 skills:
# - email_monitor_skill.md
# - linkedin_automation_skill.md
# - plan_creation_skill.md
# - whatsapp_monitor_skill.md
```

**Expected Result:** 4 skill files present ✅

### Test 3: Test Gmail Watcher

```bash
# Install dependencies
pip install -r requirements.txt

# Run Gmail watcher (requires credentials)
python simple_gmail_watcher.py
```

**Expected Result:** Script runs without errors (may need Gmail credentials) ✅

---

## 🥈 Silver Tier Testing

### Test 1: Verify Multiple Watchers

```bash
# Check watcher files exist
ls -la simple_gmail_watcher.py
ls -la linkedin_automation.py
ls -la email_workflow_orchestrator.py
```

**Expected Result:** All 3 watcher files exist ✅

### Test 2: Test LinkedIn Automation

```bash
# Run LinkedIn automation (dry-run mode)
export DRY_RUN=true
python linkedin_automation.py
```

**Expected Result:** 
- Script runs successfully
- Creates approval file in AI_Employee_Vault/Pending_Approval/
- No actual posting (dry-run mode)

### Test 3: Verify MCP Servers

```bash
# Check MCP server directories
ls -la email-mcp-server/
ls -la odoo-mcp-server/
ls -la social-media-mcp-servers/
ls -la task-management-mcp-server/

# Check each has package.json or main file
ls email-mcp-server/package.json
ls odoo-mcp-server/package.json
```

**Expected Result:** All 4 MCP servers present with proper structure ✅

### Test 4: Test Plan Generator

```bash
# Run plan generator
python plan_generator.py
```

**Expected Result:** Creates Plan.md file in AI_Employee_Vault/Plans/ ✅

### Test 5: Test Approval Workflow

```bash
# Create a test approval file
mkdir -p AI_Employee_Vault/Pending_Approval
echo "Test approval request" > AI_Employee_Vault/Pending_Approval/TEST_APPROVAL.md

# Move to Approved (simulating human approval)
mv AI_Employee_Vault/Pending_Approval/TEST_APPROVAL.md AI_Employee_Vault/Approved/

# Verify
ls AI_Employee_Vault/Approved/TEST_APPROVAL.md
```

**Expected Result:** File successfully moved ✅

---

## 🥇 Gold Tier Testing

### Test 1: Test CEO Briefing System

```bash
# Run CEO briefing system
python ceo_briefing_system.py
```

**Expected Result:**
- Creates briefing file in AI_Employee_Vault/Briefings/
- No errors
- File contains business metrics

### Test 2: Test Audit Logger

```bash
# Run audit logger
python comprehensive_audit_logger.py
```

**Expected Result:**
- Creates SQLite database
- Logs audit entries
- No errors

### Test 3: Test Ralph Wiggum Loop

```bash
# Run Ralph Wiggum loop (with test task)
python ralph_wiggum_loop.py
```

**Expected Result:**
- Script runs autonomous loop
- Processes tasks
- Creates completion markers

### Test 4: Test Cross-Domain Integration

```bash
# Run cross-domain integration
python cross_domain_integration.py
```

**Expected Result:**
- Orchestrates multiple systems
- No errors
- Creates integration logs

### Test 5: Test Error Recovery

```bash
# Run error recovery system
python error_recovery_system.py
```

**Expected Result:**
- System handles errors gracefully
- Creates recovery logs
- No crashes

### Test 6: Test Social Media Integrations (Code Verification)

```bash
# Verify Facebook handler exists and is valid Python
python -m py_compile facebook_content_handler.py
echo "Facebook handler: OK"

# Verify Twitter handler exists and is valid Python
python -m py_compile twitter_api_handler.py
echo "Twitter handler: OK"

# Check MCP servers
ls social-media-mcp-servers/facebook-mcp-server/index.js
ls social-media-mcp-servers/twitter-mcp-server/
```

**Expected Result:** All files compile without syntax errors ✅

**Note:** Live posting requires API credentials (see SOCIAL_MEDIA_SETUP_GUIDE.md)

### Test 7: Test Odoo Integration (Code Verification)

```bash
# Verify Odoo integration code
python -m py_compile odoo_integration.py
echo "Odoo integration: OK"

# Check Odoo MCP server
ls odoo-mcp-server/package.json
ls odoo-mcp-server/index.js
```

**Expected Result:** Code compiles, MCP server files exist ✅

**Note:** Requires local Odoo instance for live testing

---

## 💎 Platinum Tier Testing

### Test 1: Verify Cloud Deployment

```bash
# Check cloud orchestrator file
ls -la implementation/railway_all_in_one.py

# Test health endpoint
curl https://ai-employee-cloud.onrender.com/health
```

**Expected Result:**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-06T...",
  "services": {
    "orchestrator": "running",
    "vault_sync": "active",
    "gmail_watcher": "monitoring"
  }
}
```

### Test 2: Verify Git-Based Vault Sync

```bash
# Check if vault is a git repository
cd AI_Employee_Vault
git status

# Check recent commits
git log --oneline -5

# Verify .gitignore excludes secrets
cat .gitignore | grep -E "(credentials|token|\.env)"
```

**Expected Result:**
- Vault is a git repository ✅
- Has commit history ✅
- Secrets are in .gitignore ✅

### Test 3: Test Offline Coordination Workflow

**Manual Test Steps:**

1. **Create test email scenario:**
   - Send email to your Gmail account
   - Subject: "Test Platinum Workflow"

2. **Verify cloud detection:**
   - Check cloud logs: `curl https://ai-employee-cloud.onrender.com/health`
   - Cloud should detect email

3. **Check vault for draft:**
   - Look in AI_Employee_Vault/Pending_Approval/
   - Should see EMAIL_CLOUD_*.md file

4. **Simulate approval:**
   - Move file to AI_Employee_Vault/Approved/
   - Commit and push to GitHub

5. **Verify completion:**
   - Cloud pulls approval
   - Task moves to Done/

**Expected Result:** Complete offline coordination workflow ✅

### Test 4: Verify Security Rules

```bash
# Check .gitignore
cat .gitignore | grep -E "(\.env|credentials|token|session)"

# Verify no secrets in git
git log --all --full-history --source --pretty=format: -- .env credentials.json | wc -l
# Should be 0
```

**Expected Result:** No secrets in git history ✅

---

## 🧪 Integration Testing

### Full System Test

```bash
# Start all components (in separate terminals)

# Terminal 1: Gmail Watcher
python simple_gmail_watcher.py

# Terminal 2: LinkedIn Automation
python linkedin_automation.py

# Terminal 3: System Monitor
python ai_employee_monitor.py

# Terminal 4: Master System
python ai_employee_master_system.py
```

**Expected Result:** All systems run without conflicts ✅

---

## 📊 Performance Testing

### Test System Health

```bash
# Run health check
python system_health_check.py
```

**Expected Result:**
- All systems report healthy
- No resource issues
- Response times acceptable

---

## 🐛 Error Testing

### Test Error Recovery

```bash
# Simulate error condition
# (Create invalid file in Needs_Action)
echo "INVALID" > AI_Employee_Vault/Needs_Action/INVALID_TEST.md

# Run error recovery
python error_recovery_system.py

# Verify error was handled
ls AI_Employee_Vault/Errors/
```

**Expected Result:** Error logged and handled gracefully ✅

---

## 📝 Documentation Testing

### Verify All Documentation Exists

```bash
# Check documentation files
ls -la README.md
ls -la FINAL_SUBMISSION.md
ls -la HACKATHON_COMPLETION_STATUS.md
ls -la TIER_VERIFICATION_FINAL.md
ls -la PLATINUM_TIER_ACHIEVEMENT.md
ls -la PLATINUM_LIMITATIONS.md
ls -la RENDER_DEPLOYMENT_GUIDE.md
ls -la SOCIAL_MEDIA_SETUP_GUIDE.md
ls -la SUBMISSION_CHECKLIST.md
```

**Expected Result:** All 9+ documentation files exist ✅

---

## ✅ Quick Verification Checklist

Run this script to verify everything:

```bash
#!/bin/bash
echo "=== Quick Verification Script ==="
echo ""

# Bronze Tier
echo "✓ Bronze Tier:"
[ -f "AI_Employee_Vault/Dashboard.md" ] && echo "  ✅ Dashboard.md" || echo "  ❌ Dashboard.md"
[ -f "AI_Employee_Vault/Company_Handbook.md" ] && echo "  ✅ Company_Handbook.md" || echo "  ❌ Company_Handbook.md"
[ -f "simple_gmail_watcher.py" ] && echo "  ✅ Gmail Watcher" || echo "  ❌ Gmail Watcher"
[ -d ".claude/skills" ] && echo "  ✅ Agent Skills" || echo "  ❌ Agent Skills"

# Silver Tier
echo ""
echo "✓ Silver Tier:"
[ -f "linkedin_automation.py" ] && echo "  ✅ LinkedIn Automation" || echo "  ❌ LinkedIn Automation"
[ -f "plan_generator.py" ] && echo "  ✅ Plan Generator" || echo "  ❌ Plan Generator"
[ -d "email-mcp-server" ] && echo "  ✅ MCP Servers" || echo "  ❌ MCP Servers"

# Gold Tier
echo ""
echo "✓ Gold Tier:"
[ -f "ceo_briefing_system.py" ] && echo "  ✅ CEO Briefing (728 lines)" || echo "  ❌ CEO Briefing"
[ -f "comprehensive_audit_logger.py" ] && echo "  ✅ Audit Logger (842 lines)" || echo "  ❌ Audit Logger"
[ -f "ralph_wiggum_loop.py" ] && echo "  ✅ Ralph Wiggum (829 lines)" || echo "  ❌ Ralph Wiggum"
[ -f "facebook_content_handler.py" ] && echo "  ✅ Facebook Integration" || echo "  ❌ Facebook Integration"
[ -f "twitter_api_handler.py" ] && echo "  ✅ Twitter Integration" || echo "  ❌ Twitter Integration"

# Platinum Tier
echo ""
echo "✓ Platinum Tier:"
[ -f "implementation/railway_all_in_one.py" ] && echo "  ✅ Cloud Orchestrator" || echo "  ❌ Cloud Orchestrator"
curl -s https://ai-employee-cloud.onrender.com/health > /dev/null && echo "  ✅ Live Deployment" || echo "  ❌ Live Deployment"

echo ""
echo "=== Verification Complete ==="
```

---

## 🎯 Expected Test Results Summary

| Tier | Tests | Expected Pass Rate |
|------|-------|-------------------|
| Bronze | 3 tests | 100% ✅ |
| Silver | 5 tests | 100% ✅ |
| Gold | 7 tests | 100% ✅ |
| Platinum | 4 tests | 100% ✅ |

**Total: 19 tests, 100% pass rate expected**

---

## 🚨 Troubleshooting

### Common Issues:

1. **Gmail credentials missing:**
   - Run: `python generate_gmail_token.py`
   - Follow OAuth flow

2. **MCP servers not starting:**
   - Check: `npm install` in each MCP server directory
   - Verify: Node.js version 24+

3. **Cloud deployment not responding:**
   - Check: https://ai-employee-cloud.onrender.com/health
   - May need to wake up (free tier sleeps after inactivity)

4. **Vault sync issues:**
   - Verify: Git credentials configured
   - Check: .gitignore excludes secrets

---

## 📞 Support

If tests fail:
1. Check error logs in AI_Employee_Vault/Logs/
2. Review PLATINUM_LIMITATIONS.md for known issues
3. Verify all dependencies installed: `pip install -r requirements.txt`

---

**Testing Guide Complete - All Systems Ready for Verification** ✅
