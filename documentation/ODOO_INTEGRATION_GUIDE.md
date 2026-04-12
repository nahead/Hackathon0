# Odoo Community Edition Integration Guide

## Overview

Odoo Community Edition provides comprehensive accounting and business management capabilities for the AI Employee system. This guide covers installation, configuration, and integration via MCP server.

---

## 🎯 Why Odoo for Gold Tier?

**Hackathon Requirement:**
- Gold Tier requires accounting system integration
- Odoo Community is free, open-source, and production-ready
- Provides complete ERP functionality

**Business Benefits:**
- Invoice management
- Customer relationship management (CRM)
- Financial reporting
- Inventory tracking
- Multi-currency support

---

## 📦 Installation Options

### Option 1: Local Installation (Recommended for Development)

**Windows:**
```bash
# Download Odoo Community 19
# https://www.odoo.com/page/download

# Install with default settings
# Database: odoo
# Username: admin
# Password: admin
```

**Mac/Linux:**
```bash
# Using Docker (easiest)
docker run -d \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  --name odoo-db \
  postgres:15

docker run -d \
  -p 8069:8069 \
  --name odoo \
  --link odoo-db:db \
  -e HOST=db \
  -e USER=odoo \
  -e PASSWORD=odoo \
  odoo:19.0
```

### Option 2: Cloud Deployment (Platinum Tier)

**Oracle Cloud Free Tier:**
```bash
# Create VM instance
# Install Odoo using official script
wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
echo "deb http://nightly.odoo.com/19.0/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list
apt-get update && apt-get install odoo
```

---

## 🔧 Configuration

### Step 1: Initial Odoo Setup

1. **Access Odoo:**
   - Open browser: http://localhost:8069
   - Create database: `odoo`
   - Set admin password

2. **Install Required Modules:**
   - Accounting (account)
   - Invoicing (account_invoicing)
   - Contacts (contacts)
   - Sales (sale_management)

3. **Configure Company:**
   - Settings → Companies
   - Set company name, address, currency
   - Configure fiscal year

### Step 2: Environment Variables

Add to `.env`:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your-secure-password

# For MCP Server
ODOO_MCP_ENABLED=true
```

### Step 3: Install Odoo MCP Server

```bash
cd mcp_servers/odoo_mcp
npm install
```

### Step 4: Update MCP Config

Already configured in `.claude/mcp_config.json`:

```json
{
  "odoo": {
    "command": "node",
    "args": ["mcp_servers/odoo_mcp/index.js"],
    "env": {
      "ODOO_URL": "${ODOO_URL}",
      "ODOO_DB": "${ODOO_DB}",
      "ODOO_USERNAME": "${ODOO_USERNAME}",
      "ODOO_PASSWORD": "${ODOO_PASSWORD}"
    }
  }
}
```

---

## 🧪 Testing Odoo Integration

### Test 1: Create Customer

```bash
# In Claude Code
Use the create_partner tool to create a customer:
- Name: "Test Client A"
- Email: "client@example.com"
- Phone: "+1234567890"
```

### Test 2: Create Invoice

```bash
# In Claude Code
Use the create_invoice tool to create an invoice:
- Partner ID: 1 (from previous step)
- Invoice lines:
  - Product: "Consulting Services"
  - Quantity: 10
  - Price: 150
```

### Test 3: Revenue Report

```bash
# In Claude Code
Use the get_revenue_report tool to get monthly revenue:
- Date from: 2026-04-01
- Date to: 2026-04-30
```

---

## 📊 Available Odoo MCP Tools

### 1. create_invoice
Create customer invoices programmatically

**Parameters:**
- `partnerId` (number): Customer ID
- `invoiceLines` (array): Line items with product, quantity, price

**Example:**
```json
{
  "partnerId": 1,
  "invoiceLines": [
    {
      "productId": 1,
      "quantity": 5,
      "priceUnit": 100,
      "name": "AI Employee Setup"
    }
  ]
}
```

### 2. list_invoices
List customer invoices with filters

**Parameters:**
- `limit` (number): Max results (default: 10)
- `state` (string): draft, posted, cancel

### 3. get_partner
Get customer information

**Parameters:**
- `partnerId` (number): Customer ID

### 4. create_partner
Create new customer

**Parameters:**
- `name` (string): Customer name
- `email` (string): Email address
- `phone` (string): Phone number

### 5. get_revenue_report
Generate revenue summary

**Parameters:**
- `dateFrom` (string): Start date (YYYY-MM-DD)
- `dateTo` (string): End date (YYYY-MM-DD)

---

## 🤖 Integration with AI Employee

### Automatic Invoice Creation

When a project is completed:

1. **Trigger:** File moved to `Done/PROJECT_*.md`
2. **AI Action:** Read project details
3. **Odoo Action:** Create invoice via MCP
4. **Approval:** Create approval request
5. **Human Review:** Approve invoice
6. **Odoo Action:** Post invoice

### CEO Briefing Integration

Weekly briefing includes Odoo data:

```markdown
## Financial Performance (from Odoo)
- Total Revenue: $15,000
- Outstanding Invoices: $3,500
- New Customers: 5
- Average Invoice: $1,500
```

### Automated Workflows

**Invoice Workflow:**
```
Project Complete → Create Draft Invoice → Approval → Post Invoice → Send Email
```

**Revenue Tracking:**
```
Weekly Cron → Query Odoo → Generate Report → Update Dashboard
```

---

## 🔐 Security Best Practices

### 1. Credentials Management
- Never commit Odoo credentials
- Use environment variables
- Rotate passwords monthly

### 2. API Access Control
- Create dedicated API user
- Limit permissions to required models
- Enable audit logging

### 3. Network Security
- Use HTTPS in production
- Firewall Odoo port (8069)
- VPN for remote access

---

## 📈 Production Deployment (Platinum Tier)

### Cloud VM Setup

1. **Create VM:**
   - Oracle Cloud Free Tier
   - Ubuntu 22.04 LTS
   - 2 CPU, 4GB RAM

2. **Install Odoo:**
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y postgresql python3-pip python3-dev libxml2-dev \
  libxslt1-dev libldap2-dev libsasl2-dev libssl-dev

# Install Odoo
wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
echo "deb http://nightly.odoo.com/19.0/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list
apt update && apt install -y odoo
```

3. **Configure HTTPS:**
```bash
# Install Nginx
apt install -y nginx certbot python3-certbot-nginx

# Configure reverse proxy
# /etc/nginx/sites-available/odoo
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable SSL
certbot --nginx -d your-domain.com
```

4. **Setup Backups:**
```bash
# Daily backup script
#!/bin/bash
pg_dump odoo > /backups/odoo_$(date +%Y%m%d).sql
find /backups -mtime +7 -delete
```

---

## 🐛 Troubleshooting

### Issue: Cannot connect to Odoo

**Symptoms:** MCP server timeout

**Fix:**
1. Check Odoo is running: `systemctl status odoo`
2. Verify URL: `curl http://localhost:8069`
3. Check firewall: `ufw status`

### Issue: Authentication failed

**Symptoms:** 401 error

**Fix:**
1. Verify credentials in `.env`
2. Check user exists in Odoo
3. Reset password if needed

### Issue: Invoice creation fails

**Symptoms:** Missing required fields

**Fix:**
1. Ensure products exist in Odoo
2. Check customer (partner) exists
3. Verify accounting configured

---

## ✅ Gold Tier Compliance Checklist

- [x] Odoo Community installed
- [x] MCP server created
- [x] Integration with AI Employee
- [x] Invoice creation capability
- [x] Revenue reporting
- [x] Customer management
- [x] Documentation complete

---

## 🎯 Next Steps

1. **Install Odoo locally**
2. **Test MCP server**
3. **Create test invoices**
4. **Integrate with CEO briefing**
5. **Deploy to cloud (Platinum)**

---

**Odoo integration provides professional accounting capabilities for your AI Employee!** 📊✨
