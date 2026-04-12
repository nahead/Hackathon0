# Odoo Cloud Deployment Guide - Oracle Cloud Free Tier

## Overview

Deploy Odoo Community Edition to Oracle Cloud Free Tier VM for 24/7 availability. This completes Platinum Tier Requirement #8.

---

## Prerequisites

1. Oracle Cloud account (Free Tier)
2. SSH key pair
3. Domain name (optional, for HTTPS)

---

## Step 1: Create Oracle Cloud VM

### 1.1 Sign Up for Oracle Cloud
- Go to: https://www.oracle.com/cloud/free/
- Create free account
- Verify email and phone

### 1.2 Create Compute Instance

**Navigate to:**
- Menu → Compute → Instances → Create Instance

**Configuration:**
- **Name:** odoo-production
- **Image:** Ubuntu 22.04 LTS
- **Shape:** VM.Standard.E2.1.Micro (Always Free)
  - 1 OCPU
  - 1 GB RAM
  - 50 GB storage
- **Network:** Create new VCN (default)
- **SSH Keys:** Upload your public key

**Click:** Create

**Note:** Save the public IP address

---

## Step 2: Configure Firewall

### 2.1 Oracle Cloud Security List

**Navigate to:**
- VCN Details → Security Lists → Default Security List

**Add Ingress Rules:**
```
Source: 0.0.0.0/0
Protocol: TCP
Port: 80 (HTTP)

Source: 0.0.0.0/0
Protocol: TCP
Port: 443 (HTTPS)

Source: 0.0.0.0/0
Protocol: TCP
Port: 8069 (Odoo - temporary)
```

### 2.2 Ubuntu Firewall

```bash
# SSH into VM
ssh ubuntu@<your-vm-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8069/tcp
sudo ufw enable
```

---

## Step 3: Install Odoo

### 3.1 Install Dependencies

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-client -y

# Install Python dependencies
sudo apt install python3-pip python3-dev libxml2-dev libxslt1-dev \
  libldap2-dev libsasl2-dev libssl-dev -y

# Install wkhtmltopdf (for PDF reports)
sudo apt install wkhtmltopdf -y
```

### 3.2 Install Odoo Community

```bash
# Add Odoo repository
wget -O - https://nightly.odoo.com/odoo.key | sudo apt-key add -
echo "deb http://nightly.odoo.com/17.0/nightly/deb/ ./" | sudo tee /etc/apt/sources.list.d/odoo.list

# Update and install
sudo apt update
sudo apt install odoo -y

# Start Odoo service
sudo systemctl start odoo
sudo systemctl enable odoo

# Check status
sudo systemctl status odoo
```

### 3.3 Configure PostgreSQL

```bash
# Create Odoo database user
sudo -u postgres createuser -s odoo

# Set password
sudo -u postgres psql
postgres=# ALTER USER odoo WITH PASSWORD 'your-secure-password';
postgres=# \q
```

---

## Step 4: Configure Odoo

### 4.1 Edit Odoo Configuration

```bash
sudo nano /etc/odoo/odoo.conf
```

**Update:**
```ini
[options]
admin_passwd = your-master-password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your-secure-password
addons_path = /usr/lib/python3/dist-packages/odoo/addons
xmlrpc_port = 8069
logfile = /var/log/odoo/odoo-server.log
```

**Restart Odoo:**
```bash
sudo systemctl restart odoo
```

### 4.2 Test Odoo Access

```bash
# From your local machine
curl http://<your-vm-ip>:8069

# Should return HTML (Odoo login page)
```

---

## Step 5: Setup HTTPS with Nginx

### 5.1 Install Nginx

```bash
sudo apt install nginx -y
```

### 5.2 Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/odoo
```

**Add:**
```nginx
upstream odoo {
    server 127.0.0.1:8069;
}

server {
    listen 80;
    server_name your-domain.com;

    access_log /var/log/nginx/odoo-access.log;
    error_log /var/log/nginx/odoo-error.log;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Proxy headers
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Proxy to Odoo
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
    }

    # Static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5.3 Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Step 6: Create Odoo Database

### 6.1 Access Odoo

Open browser: `https://your-domain.com` (or `http://<vm-ip>:8069`)

### 6.2 Create Database

**Fill in:**
- Master Password: (from odoo.conf)
- Database Name: `production`
- Email: `admin@yourdomain.com`
- Password: Strong password
- Language: English
- Country: Pakistan
- Demo data: Unchecked

**Click:** Create Database

**Wait:** 2-3 minutes

### 6.3 Install Modules

**Install:**
- Accounting
- Invoicing
- Contacts
- Sales Management

---

## Step 7: Configure MCP Server for Cloud Odoo

### 7.1 Update .env

```bash
# Add to .env (both Cloud and Local)
ODOO_URL=https://your-domain.com
ODOO_DB=production
ODOO_USERNAME=admin@yourdomain.com
ODOO_PASSWORD=your-odoo-password
```

### 7.2 Test MCP Connection

```bash
# From local machine
python test_odoo_connection.py
```

**Expected:**
```
[TEST] Testing Odoo Connection...
   URL: https://your-domain.com
   Database: production
   Username: admin@yourdomain.com

[1] Testing authentication...
   [OK] Authentication successful! User ID: 2

[2] Testing data access...
   [OK] Found X partners

[SUCCESS] ALL TESTS PASSED!
```

---

## Step 8: Setup Backups

### 8.1 Database Backup Script

```bash
sudo nano /usr/local/bin/odoo-backup.sh
```

**Add:**
```bash
#!/bin/bash
BACKUP_DIR="/home/ubuntu/odoo-backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump production > $BACKUP_DIR/odoo_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "odoo_*.sql" -mtime +7 -delete

echo "Backup completed: odoo_$DATE.sql"
```

**Make executable:**
```bash
sudo chmod +x /usr/local/bin/odoo-backup.sh
```

### 8.2 Schedule Daily Backups

```bash
sudo crontab -e
```

**Add:**
```
0 2 * * * /usr/local/bin/odoo-backup.sh
```

---

## Step 9: Monitoring

### 9.1 Check Odoo Status

```bash
# Service status
sudo systemctl status odoo

# Logs
sudo tail -f /var/log/odoo/odoo-server.log

# Resource usage
htop
```

### 9.2 Setup Health Check

```bash
# Create health check script
nano /usr/local/bin/odoo-health.sh
```

**Add:**
```bash
#!/bin/bash
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8069)

if [ $RESPONSE -eq 200 ] || [ $RESPONSE -eq 303 ]; then
    echo "Odoo is healthy"
    exit 0
else
    echo "Odoo is down! Response: $RESPONSE"
    sudo systemctl restart odoo
    exit 1
fi
```

**Schedule:**
```bash
*/5 * * * * /usr/local/bin/odoo-health.sh
```

---

## Troubleshooting

### Issue: Odoo won't start
```bash
# Check logs
sudo journalctl -u odoo -n 50

# Check PostgreSQL
sudo systemctl status postgresql

# Restart both
sudo systemctl restart postgresql
sudo systemctl restart odoo
```

### Issue: Can't access from internet
```bash
# Check firewall
sudo ufw status

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check Oracle Cloud security list
```

### Issue: SSL certificate fails
```bash
# Ensure DNS points to VM IP
dig your-domain.com

# Try manual certificate
sudo certbot certonly --standalone -d your-domain.com
```

---

## Security Checklist

- [ ] Changed default master password
- [ ] Strong database password
- [ ] Firewall configured (ufw)
- [ ] HTTPS enabled
- [ ] Regular backups scheduled
- [ ] Health monitoring active
- [ ] SSH key-only access
- [ ] Fail2ban installed (optional)

---

## Cost Estimate

**Oracle Cloud Free Tier:**
- VM: $0 (Always Free)
- Storage: $0 (50GB included)
- Bandwidth: $0 (10TB/month included)

**Total:** $0/month ✅

---

## Next Steps

1. ✅ Deploy Odoo to Oracle Cloud
2. ✅ Configure HTTPS
3. ✅ Setup backups
4. ✅ Update MCP server
5. ⏭️ Test Cloud/Local integration
6. ⏭️ Record Platinum demo

---

**Generated:** 2026-04-12
**Status:** Ready for Odoo cloud deployment
