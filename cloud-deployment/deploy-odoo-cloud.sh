#!/bin/bash
# Odoo Community Cloud Deployment Script
# Deploys Odoo 19 Community Edition on Oracle Cloud Always Free VM

set -e

echo "🏢 Deploying Odoo Community Edition - Cloud"
echo "==========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (sudo ./deploy-odoo-cloud.sh)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install PostgreSQL
echo "🗄️ Installing PostgreSQL..."
apt install -y postgresql postgresql-contrib

# Create Odoo user and database
echo "👤 Setting up Odoo database user..."
sudo -u postgres createuser -s odoo
sudo -u postgres createdb -O odoo odoo

# Set PostgreSQL password for odoo user
sudo -u postgres psql -c "ALTER USER odoo PASSWORD 'odoo_secure_password_2026';"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
apt install -y python3-pip python3-dev python3-venv python3-wheel libxml2-dev libxslt1-dev libevent-dev libsasl2-dev libldap2-dev pkg-config libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev libxcb1-dev

# Install wkhtmltopdf (for PDF reports)
echo "📄 Installing wkhtmltopdf..."
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb || apt-get install -f -y
rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Create Odoo system user
echo "👤 Creating Odoo system user..."
adduser --system --home=/opt/odoo --group odoo

# Download and install Odoo Community 19
echo "📥 Downloading Odoo Community 19..."
cd /opt/odoo
sudo -u odoo git clone https://www.github.com/odoo/odoo --depth 1 --branch 19.0 --single-branch .

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u odoo python3 -m venv venv
sudo -u odoo /opt/odoo/venv/bin/pip install --upgrade pip

# Install Odoo dependencies
echo "📦 Installing Odoo Python dependencies..."
sudo -u odoo /opt/odoo/venv/bin/pip install -r requirements.txt

# Create Odoo configuration file
echo "⚙️ Creating Odoo configuration..."
cat > /etc/odoo.conf << 'EOF'
[options]
; This is the password that allows database operations:
admin_passwd = admin_secure_password_2026
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo_secure_password_2026
addons_path = /opt/odoo/addons
logfile = /var/log/odoo/odoo.log
log_level = info

; HTTP Configuration
http_port = 8069
http_interface = 0.0.0.0

; Security
list_db = False
proxy_mode = True

; Performance
workers = 2
max_cron_threads = 1
EOF

# Set proper permissions
chown odoo:odoo /etc/odoo.conf
chmod 640 /etc/odoo.conf

# Create log directory
mkdir -p /var/log/odoo
chown odoo:odoo /var/log/odoo

# Create systemd service
echo "🔄 Creating systemd service..."
cat > /etc/systemd/system/odoo.service << 'EOF'
[Unit]
Description=Odoo Community Edition
Documentation=http://www.odoo.com
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/venv/bin/python /opt/odoo/odoo-bin -c /etc/odoo.conf
StandardOutput=journal+console
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Odoo service
systemctl daemon-reload
systemctl enable odoo
systemctl start odoo

# Install Nginx for reverse proxy
echo "🌐 Installing and configuring Nginx..."
apt install -y nginx

# Create Nginx configuration for Odoo
cat > /etc/nginx/sites-available/odoo << 'EOF'
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

server {
    listen 80;
    server_name _;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;

    # SSL Configuration (will be updated by Certbot)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    # Log files
    access_log /var/log/nginx/odoo.access.log;
    error_log /var/log/nginx/odoo.error.log;

    # Handle longpoll requests
    location /longpolling {
        proxy_pass http://odoochat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Handle all other requests
    location / {
        proxy_pass http://odoo;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    gzip_disable "MSIE [1-6]\.";

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Install Certbot for SSL
echo "🔒 Installing Certbot for SSL certificates..."
apt install -y certbot python3-certbot-nginx

# Start Nginx
systemctl enable nginx
systemctl restart nginx

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 'Nginx Full'
ufw allow ssh
ufw --force enable

# Create backup script
echo "💾 Creating backup script..."
mkdir -p /opt/odoo-backups
cat > /opt/odoo-backups/backup-odoo.sh << 'EOF'
#!/bin/bash
# Odoo Backup Script

BACKUP_DIR="/opt/odoo-backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="odoo"

# Create backup directory for today
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
echo "Backing up database..."
sudo -u postgres pg_dump $DB_NAME > "$BACKUP_DIR/$DATE/odoo_db_$DATE.sql"

# Backup filestore
echo "Backing up filestore..."
tar -czf "$BACKUP_DIR/$DATE/odoo_filestore_$DATE.tar.gz" -C /opt/odoo/.local/share/Odoo/filestore .

# Backup configuration
echo "Backing up configuration..."
cp /etc/odoo.conf "$BACKUP_DIR/$DATE/odoo.conf"

# Remove backups older than 30 days
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
EOF

chmod +x /opt/odoo-backups/backup-odoo.sh

# Schedule daily backups
echo "📅 Scheduling daily backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/odoo-backups/backup-odoo.sh") | crontab -

# Create health check script
cat > /opt/odoo/health-check.sh << 'EOF'
#!/bin/bash
# Odoo Health Check Script

# Check if Odoo service is running
if ! systemctl is-active --quiet odoo; then
    echo "❌ Odoo service is not running"
    systemctl restart odoo
    echo "🔄 Restarted Odoo service"
fi

# Check if Nginx is running
if ! systemctl is-active --quiet nginx; then
    echo "❌ Nginx service is not running"
    systemctl restart nginx
    echo "🔄 Restarted Nginx service"
fi

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL service is not running"
    systemctl restart postgresql
    echo "🔄 Restarted PostgreSQL service"
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ Disk usage is at ${DISK_USAGE}%"
fi

echo "✅ Health check completed at $(date)"
EOF

chmod +x /opt/odoo/health-check.sh

# Schedule health checks every 15 minutes
(crontab -l 2>/dev/null; echo "*/15 * * * * /opt/odoo/health-check.sh >> /var/log/odoo/health-check.log 2>&1") | crontab -

# Wait for Odoo to start
echo "⏳ Waiting for Odoo to start..."
sleep 30

# Check if Odoo is running
if systemctl is-active --quiet odoo; then
    echo "✅ Odoo service is running"
else
    echo "❌ Odoo service failed to start"
    systemctl status odoo
    exit 1
fi

# Display final information
echo ""
echo "🎉 Odoo Community Edition Deployment Complete!"
echo "=============================================="
echo ""
echo "📊 Service Status:"
echo "  - Odoo: $(systemctl is-active odoo)"
echo "  - PostgreSQL: $(systemctl is-active postgresql)"
echo "  - Nginx: $(systemctl is-active nginx)"
echo ""
echo "🌐 Access Information:"
echo "  - HTTP: http://$(curl -s ifconfig.me) (redirects to HTTPS)"
echo "  - HTTPS: https://$(curl -s ifconfig.me) (self-signed cert initially)"
echo "  - Database: odoo"
echo "  - Admin Password: admin_secure_password_2026"
echo ""
echo "🔒 SSL Certificate Setup:"
echo "  Run: certbot --nginx -d your-domain.com"
echo "  Or use IP: certbot --nginx --register-unsafely-without-email --agree-tos"
echo ""
echo "💾 Backup Information:"
echo "  - Location: /opt/odoo-backups/"
echo "  - Schedule: Daily at 2:00 AM"
echo "  - Retention: 30 days"
echo ""
echo "📋 Management Commands:"
echo "  - Restart Odoo: systemctl restart odoo"
echo "  - View logs: journalctl -u odoo -f"
echo "  - Manual backup: /opt/odoo-backups/backup-odoo.sh"
echo "  - Health check: /opt/odoo/health-check.sh"
echo ""
echo "🔧 Configuration Files:"
echo "  - Odoo: /etc/odoo.conf"
echo "  - Nginx: /etc/nginx/sites-available/odoo"
echo "  - Logs: /var/log/odoo/"
echo ""
echo "🚀 Odoo Community is now ready for production use!"