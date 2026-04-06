# Personal AI Employee - Autonomous FTE System

🤖 **Complete implementation of the Personal AI Employee Hackathon 0 project**

A fully autonomous AI employee system that manages business operations 24/7 using Claude Code, Obsidian, and Model Context Protocol (MCP) servers.

## 🏆 Achievement Status

### ✅ Bronze Tier - COMPLETE (100%)
- Obsidian vault with Dashboard.md and Company_Handbook.md
- Working file system watcher (base_watcher.py, simple_gmail_watcher.py)
- Claude Code integration with vault
- Complete folder structure (/Inbox, /Needs_Action, /Done, /Plans, /Logs, /Pending_Approval, /Approved, /Rejected)
- **4 Agent Skills** implemented in `skills/`

### ✅ Silver Tier - COMPLETE (100%)
- Multiple watchers (Gmail + LinkedIn automation)
- Automatic LinkedIn posting for business lead generation
- Plan.md generation system (plan_generator.py)
- Working MCP servers (email, odoo, social-media, task-management)
- Human-in-the-loop approval workflow
- Cross-platform scheduling system (scheduling_system.py)
- All functionality as Agent Skills

### ✅ Gold Tier - COMPLETE (95%)
- Full cross-domain integration (cross_domain_integration.py)
- Odoo Community accounting integration (odoo_integration.py + MCP server)
- Facebook and Instagram integration (facebook_content_handler.py)
- Twitter/X integration (twitter_api_handler.py)
- Multiple MCP servers for different domains
- Weekly CEO briefing and business audit system (ceo_briefing_system.py - 729 lines)
- Error recovery and graceful degradation (error_recovery_system.py)
- Comprehensive audit logging (comprehensive_audit_logger.py - 843 lines)
- Ralph Wiggum autonomous loop (ralph_wiggum_loop.py - 830 lines)
- Complete documentation and architecture

### ✅ Platinum Tier - COMPLETE (100%)
- **Cloud deployment LIVE on Render.com** (24/7 operation)
- **Live URL:** https://ai-employee-cloud.onrender.com/health
- Git-based vault synchronization (bidirectional sync every 5 minutes)
- Work-zone specialization (cloud detects, local approves/sends)
- Complete offline coordination proven with real workflow
- Email monitoring working (IMAP real-time detection)
- Approval workflow complete (human-in-the-loop)
- Email sending tested and functional (local proof)
- Security rules implemented (secrets never synced)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 24+ LTS
- Claude Code CLI
- Obsidian (for vault management)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Hackathon0
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright (for LinkedIn automation)**
```bash
playwright install
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Install MCP server dependencies**
```bash
# Email MCP Server
cd email-mcp-server && npm install && cd ..

# Odoo MCP Server
cd odoo-mcp-server && npm install && cd ..

# Social Media MCP Servers
cd social-media-mcp-servers/facebook-mcp-server && npm install && cd ../..
```

### Running the System

**Start the complete AI Employee system:**
```bash
python start_ai_employee_system.py
```

**Run individual components:**

```bash
# Gmail watcher
python simple_gmail_watcher.py

# LinkedIn automation
python linkedin_automation.py

# Ralph Wiggum autonomous loop
python ralph_wiggum_loop.py

# CEO briefing system
python ceo_briefing_system.py

# Cross-domain integration
python cross_domain_integration.py
```

**Start MCP servers:**
```bash
# Email MCP
cd email-mcp-server && node index.js

# Odoo MCP
cd odoo-mcp-server && node index.js

# Social Media MCP
cd social-media-mcp-servers && node social_media_mcp_server.py
```

## 📁 Project Structure

```
Hackathon0/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
│
├── AI_Employee_Vault/                  # Obsidian vault (Bronze tier)
│   ├── Dashboard.md                    # Real-time status
│   ├── Company_Handbook.md             # Operating rules
│   ├── Business_Goals.md               # Business objectives
│   ├── .claude/skills/                 # 15 Agent Skills
│   ├── Inbox/                          # File drop zone
│   ├── Needs_Action/                   # Tasks requiring attention
│   ├── Pending_Approval/               # Human approval queue
│   ├── Approved/                       # Approved actions
│   ├── Done/                           # Completed tasks
│   ├── Plans/                          # Generated plans
│   ├── Logs/                           # System logs
│   ├── Briefings/                      # Daily CEO briefings
│   └── Audits/                         # Business audits
│
├── Core System Files
│   ├── ai_employee_master_system.py    # Master orchestrator
│   ├── start_ai_employee_system.py     # System launcher
│   ├── base_watcher.py                 # Watcher template
│   └── simple_gmail_watcher.py         # Gmail monitoring
│
├── Silver Tier Components
│   ├── plan_generator.py               # Plan.md generation
│   └── scheduling_system.py            # Task scheduling
│
├── Gold Tier Systems
│   ├── comprehensive_audit_logger.py   # Audit logging
│   ├── ceo_briefing_system.py          # CEO briefings
│   ├── cross_domain_integration.py     # Workflow orchestration
│   ├── error_recovery_system.py        # Error handling
│   └── ralph_wiggum_loop.py            # Autonomous agent
│
├── Automation & Integration
│   ├── linkedin_automation.py          # LinkedIn posting
│   ├── linkedin_content_handler.py     # LinkedIn content
│   ├── facebook_content_handler.py     # Facebook integration
│   ├── twitter_api_handler.py          # Twitter integration
│   ├── auto_content_generator.py       # Content generation
│   ├── odoo_integration.py             # Odoo accounting
│   ├── email_response_sender.py        # Email automation
│   └── email_workflow_orchestrator.py  # Email workflows
│
├── MCP Servers (Model Context Protocol)
│   ├── email-mcp-server/               # Email operations
│   ├── odoo-mcp-server/                # Accounting operations
│   ├── social-media-mcp-servers/       # Social media ops
│   │   ├── facebook-mcp-server/
│   │   └── twitter-mcp-server/
│   └── task-management-mcp-server/     # Task operations
│
├── Cloud Deployment (Platinum Tier)
│   ├── cloud-deployment/
│   │   ├── scripts/                    # Cloud agent scripts
│   │   ├── deploy-odoo-cloud.sh        # Odoo deployment
│   │   └── oracle-cloud-setup.sh       # Oracle VM setup
│   ├── railway_all_in_one.py           # Railway deployment
│   ├── railway_cloud_orchestrator.py   # Cloud orchestration
│   └── cloud_deployment_validator.py   # Deployment validation
│
└── Documentation
    ├── CLEANUP_PLAN.md                 # Cleanup documentation
    └── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md
```

## 🎯 Key Features

### Autonomous Operations
- **Ralph Wiggum Loop**: Continuous autonomous agent that manages business operations
- **Email Monitoring**: Automatic email processing with intelligent response generation
- **Social Media Automation**: Scheduled LinkedIn posts for lead generation
- **Task Management**: Automatic task creation, prioritization, and tracking

### Business Intelligence
- **Daily CEO Briefings**: Automated executive summaries
- **Weekly Business Audits**: Comprehensive performance analysis across all domains
- **Financial Tracking**: Revenue, expenses, and invoice management
- **Performance Metrics**: Real-time KPI tracking and reporting

### Cross-Domain Integration
- **Email System**: Gmail integration with automatic response drafting
- **Social Media**: LinkedIn, Facebook, Instagram, Twitter automation
- **Accounting**: Odoo Community integration for financial management
- **Task Management**: Automated workflow orchestration

### Security & Compliance
- **Human-in-the-Loop**: Approval workflow for sensitive actions
- **Comprehensive Audit Logging**: Complete audit trail with tamper detection
- **Error Recovery**: Graceful degradation and automatic recovery
- **Data Privacy**: Local-first architecture with encrypted vault sync

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```bash
# Gmail Configuration
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Odoo Configuration (if using)
ODOO_URL=http://localhost:8069
ODOO_DB=your-database
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# LinkedIn (optional)
LINKEDIN_EMAIL=your-email
LINKEDIN_PASSWORD=your-password

# API Keys (as needed)
ANTHROPIC_API_KEY=your-key
```

### Agent Skills
The system includes 4 Agent Skills in `skills/`:
- email_monitor_skill.md - Email monitoring and processing
- linkedin_automation_skill.md - LinkedIn content generation and posting
- plan_creation_skill.md - Automated plan generation
- whatsapp_monitor_skill.md - WhatsApp integration

## 📊 System Monitoring

**Check system status:**
```bash
python ai_employee_monitor.py
```

**View logs:**
```bash
# System logs
tail -f AI_Employee_Vault/Logs/*.log

# Audit logs
cat AI_Employee_Vault/Logs/Audit/audit_*.json
```

**View briefings:**
```bash
# Daily briefings
cat AI_Employee_Vault/Briefings/CEO_Daily_Briefing_*.md

# Business audits
cat AI_Employee_Vault/Audits/audit_*.md
```

## 🔄 Workflow Examples

### Email Response Workflow
1. Gmail watcher detects new email
2. Creates task in `/Needs_Action/`
3. AI analyzes email and drafts response
4. Creates approval request in `/Pending_Approval/`
5. Human reviews and moves to `/Approved/`
6. System sends email via MCP server
7. Logs action and moves to `/Done/`

### LinkedIn Posting Workflow
1. Ralph Wiggum loop triggers social media action
2. Content generator creates post
3. LinkedIn automation posts directly (or creates approval)
4. System logs post and tracks engagement
5. Analytics stored in `/LinkedIn_Analytics/`

### Business Audit Workflow
1. CEO briefing system runs weekly
2. Collects data from all domains (email, social, accounting, tasks)
3. Analyzes performance metrics
4. Generates comprehensive audit report
5. Identifies issues and opportunities
6. Creates actionable recommendations
7. Saves to `/Audits/` and `/Briefings/`

## 🚀 Deployment (Platinum Tier)

### Railway Deployment
```bash
# Configure Railway
python railway_config_helper.py

# Deploy to Railway
python railway_all_in_one.py
```

### Oracle Cloud Deployment
```bash
cd cloud-deployment

# Set up Oracle VM
./oracle-cloud-setup.sh

# Deploy Odoo
./deploy-odoo-cloud.sh

# Start cloud agent
python scripts/cloud_orchestrator.py
```

## 🛡️ Security Best Practices

1. **Never commit credentials**: Use `.env` files (already in .gitignore)
2. **Rotate credentials monthly**: Update API keys and passwords regularly
3. **Review approval queue daily**: Check `/Pending_Approval/` folder
4. **Monitor audit logs**: Review `/Logs/Audit/` for suspicious activity
5. **Backup vault regularly**: Use Git for version control
6. **Test in dev mode first**: Use `DRY_RUN=true` for testing

## 📚 Documentation

- **Hackathon Guide**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Cleanup Plan**: `CLEANUP_PLAN.md`
- **Company Handbook**: `AI_Employee_Vault/Company_Handbook.md`
- **Business Goals**: `AI_Employee_Vault/Business_Goals.md`

## 🤝 Contributing

This is a hackathon project. For improvements:
1. Test thoroughly in development mode
2. Follow existing code patterns
3. Update documentation
4. Add Agent Skills for new functionality

## 📝 License

This project is part of the Personal AI Employee Hackathon 0.

## 🎓 Learning Resources

- [Claude Code Documentation](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
- [Agent Skills Guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Model Context Protocol](https://modelcontextprotocol.io/introduction)
- [Obsidian Documentation](https://help.obsidian.md/)

## 🏅 Achievements

- ✅ Bronze Tier: Foundation complete
- ✅ Silver Tier: Functional assistant operational
- ✅ Gold Tier: Autonomous employee fully functional
- ⚠️ Platinum Tier: Infrastructure ready (deployment pending)

---

**Built with:** Claude Code, Obsidian, Python, Node.js, MCP, Playwright

**Status:** Production-ready for Gold Tier | Infrastructure-ready for Platinum Tier

**Last Updated:** 2026-04-05
