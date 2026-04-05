#!/bin/bash
# Oracle Cloud Always Free VM Setup Script
# Run this script on your Oracle Cloud VM after initial setup

set -e

echo "🚀 AI Employee Cloud Infrastructure Setup"
echo "========================================"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-pip python3.11-venv python3.11-dev

# Install Node.js 20 LTS
echo "📦 Installing Node.js 20 LTS..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 globally
echo "⚡ Installing PM2 process manager..."
sudo npm install -g pm2

# Install Git
echo "📝 Installing Git..."
sudo apt install -y git

# Install additional dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y curl wget unzip htop nano vim screen tmux

# Create AI Employee directory structure
echo "📁 Creating directory structure..."
mkdir -p ~/ai-employee/{logs,config,scripts,vault-sync}
cd ~/ai-employee

# Install Python dependencies
echo "🐍 Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Create requirements file for cloud deployment
cat > requirements.txt << 'EOF'
watchdog==3.0.0
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
playwright==1.40.0
requests==2.31.0
python-dotenv==1.0.0
schedule==1.2.0
psutil==5.9.6
gitpython==3.1.40
cryptography==41.0.7
EOF

pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create systemd service for auto-start
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/ai-employee.service > /dev/null << EOF
[Unit]
Description=AI Employee Cloud Agent
After=network.target

[Service]
Type=forking
User=$USER
WorkingDirectory=/home/$USER/ai-employee
Environment=PATH=/home/$USER/ai-employee/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/pm2 start ecosystem.config.js --env production
ExecReload=/usr/bin/pm2 reload ecosystem.config.js --env production
ExecStop=/usr/bin/pm2 delete ecosystem.config.js
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl enable ai-employee.service

# Set up firewall (basic security)
echo "🔒 Configuring firewall..."
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# Create PM2 startup script
pm2 startup
echo "⚠️  Run the command above to complete PM2 startup configuration"

echo "✅ Oracle Cloud VM setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your AI Employee repository"
echo "2. Configure environment variables"
echo "3. Start the cloud agent with PM2"
echo "4. Test vault synchronization"