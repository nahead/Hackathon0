# AI Employee System - Daily Operations Guide
# How to Run Your AI Employee

## 🚀 STARTING THE SYSTEM

### Method 1: Complete System Startup (Recommended)
```bash
# Start everything at once
python start_ai_employee_system.py
```
**This starts**: All MCP servers + Ralph loop + Error recovery + Audit logging

### Method 2: Individual Components
```bash
# Start Ralph Wiggum autonomous loop only
python ralph_wiggum_loop.py

# Generate LinkedIn content
python linkedin_automation.py

# Create CEO briefing
python ceo_briefing_system.py

# Process emails
python email_response_sender.py
```

## 📊 DAILY OPERATIONS WORKFLOW

### Morning Routine (8:00 AM):
1. **Check Daily Briefing**:
   ```bash
   cat "AI_Employee_Vault/Briefings/CEO_Daily_Briefing_$(date +%Y-%m-%d).md"
   ```

2. **Review Pending Approvals**:
   ```bash
   ls "AI_Employee_Vault/Pending_Approval/"
   ```

3. **Approve LinkedIn Posts**:
   ```bash
   # Move approved posts
   mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Approved/"
   ```

### Throughout the Day:
- **Ralph Loop**: Runs automatically (checks emails, manages tasks)
- **Content Generation**: Creates posts at 9:00 AM
- **Email Processing**: Handles emails hourly
- **System Monitoring**: Continuous health checks

### Evening Review (6:00 PM):
1. **Check System Logs**:
   ```bash
   tail -20 "AI_Employee_Vault/Logs/ralph_loop.log"
   ```

2. **Review Business Metrics**:
   ```bash
   ls "AI_Employee_Vault/Audits/" | tail -3
   ```

## 🔍 MONITORING YOUR AI EMPLOYEE

### Real-Time Monitoring:
```bash
# Watch Ralph loop activity
tail -f "AI_Employee_Vault/Logs/ralph_loop.log"

# Monitor error recovery
tail -f "AI_Employee_Vault/Logs/error_recovery.log"

# Check system health
python system_health_check.py
```

### Key Folders to Monitor:
- **`/Pending_Approval/`**: Content waiting for your approval
- **`/Approved/`**: Content ready for publishing
- **`/Briefings/`**: Daily CEO briefings
- **`/Audits/`**: Business performance reports
- **`/Logs/`**: System activity logs

## ⚙️ SYSTEM CONTROL COMMANDS

### Start/Stop Operations:
```bash
# Start complete system
python start_ai_employee_system.py

# Stop all Python processes (if needed)
pkill -f python

# Restart system
pkill -f python && python start_ai_employee_system.py
```

### Content Management:
```bash
# Generate LinkedIn post manually
python linkedin_automation.py

# Create immediate CEO briefing
python ceo_briefing_system.py

# Generate business audit
python comprehensive_audit_logger.py
```

## 📱 SOCIAL MEDIA WORKFLOW

### LinkedIn Automation:
1. **System generates post** → `Pending_Approval/`
2. **You review content** → Check quality and relevance
3. **Approve by moving** → `mv` to `Approved/` folder
4. **System publishes** → Automatic posting (if configured)

### Content Approval Process:
```bash
# Check pending posts
ls "AI_Employee_Vault/Pending_Approval/"

# Read post content
cat "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md"

# Approve post
mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Approved/"

# Reject post (optional)
mv "AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md" "AI_Employee_Vault/Rejected/"
```

## 📊 BUSINESS INTELLIGENCE

### Daily Reports:
```bash
# Today's CEO briefing
cat "AI_Employee_Vault/Briefings/CEO_Daily_Briefing_$(date +%Y-%m-%d).md"

# Latest business audit
ls "AI_Employee_Vault/Audits/" | tail -1 | xargs -I {} cat "AI_Employee_Vault/Audits/{}"
```

### Weekly Analysis:
- **Sunday 8:00 PM**: Automatic weekly audit
- **Location**: `AI_Employee_Vault/Audits/`
- **Format**: JSON + Markdown reports

## 🔧 TROUBLESHOOTING

### If System Stops:
```bash
# Check what's running
ps aux | grep python

# Restart everything
python start_ai_employee_system.py
```

### If Logs Show Errors:
```bash
# Check error recovery log
tail -20 "AI_Employee_Vault/Logs/error_recovery.log"

# Check Ralph loop status
tail -10 "AI_Employee_Vault/Logs/ralph_loop.log"
```

### Common Issues:
- **Unicode Errors**: System continues working, non-critical
- **Email Connection**: Check internet connection
- **LinkedIn Login**: Verify credentials in config

## 📅 AUTOMATED SCHEDULE

Your AI Employee runs these automatically:
- **07:00**: System health check
- **08:00**: Daily CEO briefing
- **09:00**: Social media content generation
- **Every Hour**: Email processing
- **Sunday 20:00**: Weekly business audit

## 🎯 SUCCESS INDICATORS

### System is Working When You See:
- ✅ Ralph loop entries every few minutes
- ✅ New LinkedIn posts in Pending_Approval
- ✅ Daily briefings generated
- ✅ Business audits created
- ✅ Email processing logs
- ✅ Error recovery monitoring

## 🚀 QUICK START COMMANDS

```bash
# Start everything
python start_ai_employee_system.py

# Check status
tail -5 "AI_Employee_Vault/Logs/ralph_loop.log"

# Review today's work
ls "AI_Employee_Vault/Briefings/"
ls "AI_Employee_Vault/Pending_Approval/"

# Approve content
mv "AI_Employee_Vault/Pending_Approval/"*.md "AI_Employee_Vault/Approved/"
```

---
**Your AI Employee is ready to work 24/7!**
Just run `python start_ai_employee_system.py` and monitor the folders.