# MCP Servers Setup Guide

## Overview

Model Context Protocol (MCP) servers provide standardized interfaces for Claude Code to interact with external systems. This guide covers setup for all MCP servers in the AI Employee system.

---

## 📦 Installed MCP Servers

### 1. Email MCP Server
**Location:** `mcp_servers/email_mcp/`
**Purpose:** Gmail integration, send/receive emails
**Tools:**
- `send_email` - Send emails via SMTP
- `list_emails` - List recent Gmail messages
- `read_email` - Read specific email by ID

### 2. WhatsApp MCP Server
**Location:** `mcp_servers/whatsapp_mcp/`
**Purpose:** WhatsApp Cloud API integration
**Tools:**
- `send_whatsapp_message` - Send text messages
- `send_whatsapp_template` - Send template messages
- `get_whatsapp_media` - Retrieve media files

### 3. Browser MCP Server
**Package:** `@modelcontextprotocol/server-playwright`
**Purpose:** Web automation for payments, forms
**Tools:** Navigate, click, fill forms, screenshot

### 4. Filesystem MCP Server
**Package:** `@modelcontextprotocol/server-filesystem`
**Purpose:** Vault file operations
**Tools:** Read, write, list files in vault

---

## 🚀 Installation

### Step 1: Install MCP SDK Dependencies

```bash
cd mcp_servers/email_mcp
npm install

cd ../whatsapp_mcp
npm install
```

### Step 2: Install Standard MCP Servers

```bash
npm install -g @modelcontextprotocol/server-playwright
npm install -g @modelcontextprotocol/server-filesystem
```

### Step 3: Configure Claude Code

The MCP configuration is already set in `.claude/mcp_config.json`.

To activate, copy to Claude Code settings:

**Windows:**
```bash
copy .claude\mcp_config.json %USERPROFILE%\.config\claude-code\mcp.json
```

**Mac/Linux:**
```bash
cp .claude/mcp_config.json ~/.config/claude-code/mcp.json
```

---

## 🔧 Configuration

### Environment Variables Required

Add to your `.env` file:

```bash
# Email MCP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# WhatsApp MCP
WHATSAPP_ACCESS_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-id

# Gmail API (for reading emails)
GMAIL_CREDENTIALS=path/to/credentials.json
```

### Gmail App Password Setup

1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate new
4. Use generated password in `SMTP_PASS`

---

## 🧪 Testing MCP Servers

### Test Email MCP

```bash
cd mcp_servers/email_mcp
node index.js
```

Then in Claude Code:
```
Use the send_email tool to send a test email to test@example.com
```

### Test WhatsApp MCP

```bash
cd mcp_servers/whatsapp_mcp
node index.js
```

Then in Claude Code:
```
Use the send_whatsapp_message tool to send "Test message" to 923122955972
```

---

## 📋 Using MCP Tools in Agent Skills

### Example: Email Skill with MCP

```markdown
# Email Processor Skill

Use the email MCP server to handle email operations:

1. List unread emails:
   - Use `list_emails` tool with query "is:unread"

2. Read specific email:
   - Use `read_email` tool with messageId

3. Send response:
   - Use `send_email` tool with to, subject, body
```

### Example: WhatsApp Skill with MCP

```markdown
# WhatsApp Handler Skill

Use the whatsapp MCP server for messaging:

1. Send message:
   - Use `send_whatsapp_message` tool
   - Provide phone number (without +)
   - Provide message text

2. Follow Company Handbook rules for approval
```

---

## 🔍 Troubleshooting

### MCP Server Not Found

**Error:** `MCP server 'email' not found`

**Fix:**
1. Check MCP config path is correct
2. Verify npm packages installed
3. Restart Claude Code

### Authentication Errors

**Error:** `401 Unauthorized`

**Fix:**
1. Check environment variables loaded
2. Verify tokens not expired
3. Test credentials manually

### Connection Timeout

**Error:** `ETIMEDOUT`

**Fix:**
1. Check internet connection
2. Verify API endpoints accessible
3. Check firewall settings

---

## 🎯 Integration with Orchestrator

The orchestrator can trigger MCP operations via Claude Code:

```python
# In orchestrator.py
def trigger_email_processing():
    subprocess.run([
        'claude',
        '--cwd', str(VAULT_PATH),
        'Process emails in Needs_Action using email MCP server'
    ])
```

---

## 📊 MCP Server Status

| Server | Status | Tools | Integration |
|--------|--------|-------|-------------|
| Email | ✅ Ready | 3 | Email skill |
| WhatsApp | ✅ Ready | 3 | WhatsApp skill |
| Browser | ✅ Ready | Multiple | Payment automation |
| Filesystem | ✅ Ready | Multiple | Vault operations |

---

## 🚀 Next Steps

1. ✅ Install all MCP servers
2. ✅ Configure environment variables
3. ✅ Test each MCP server
4. ✅ Update agent skills to use MCP tools
5. ✅ Integrate with orchestrator
6. ✅ Deploy to production

---

**MCP servers provide the "hands" for your AI Employee to interact with external systems!**
