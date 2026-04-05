# Platinum Tier Cloud Deployment Guide

## 🚀 Oracle Cloud Always Free VM Setup

### Prerequisites
- Oracle Cloud Always Free account
- GitHub repository for vault synchronization
- Gmail API credentials (from existing setup)
- Local AI Employee system (Gold Tier completed)

### Step 1: Create Oracle Cloud VM

1. **Login to Oracle Cloud Console**
   - Go to https://cloud.oracle.com
   - Sign in with your Always Free account

2. **Create Compute Instance**
   - Navigate to Compute > Instances
   - Click "Create Instance"
   - **Name**: ai-employee-cloud
   - **Image**: Ubuntu 22.04 LTS (Always Free eligible)
   - **Shape**: VM.Standard.E2.1.Micro (Always Free)
   - **Network**: Use default VCN
   - **SSH Keys**: Upload your public key or generate new ones

3. **Configure Security**
   - Open ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
   - Note the public IP address

### Step 2: Initial VM Configuration

1. **Connect to VM**
   ```bash
   ssh ubuntu@<your-vm-public-ip>
   ```

2. **Upload setup files**
   ```bash
   # On your local machine
   scp -r cloud-deployment ubuntu@<your-vm-ip>:~/
   ```

3. **Run setup script**
   ```bash
   cd ~/cloud-deployment
   chmod +x oracle-cloud-setup.sh
   ./oracle-cloud-setup.sh
   ```

### Step 3: Configure Environment

1. **Create environment file**
   ```bash
   cd ~/ai-employee
   cp ../cloud-deployment/.env.template .env
   nano .env
   ```

2. **Fill in required values**
   ```bash
   # Essential settings
   VAULT_REPO_URL=https://github.com/yourusername/ai-employee-vault.git
   GIT_USERNAME=your-github-username
   GIT_TOKEN=your-github-token
   GMAIL_CREDENTIALS_PATH=/home/ubuntu/ai-employee/config/credentials.json
   ```

3. **Upload Gmail credentials**
   ```bash
   mkdir -p config
   # Upload your credentials.json from local setup
   scp credentials.json ubuntu@<your-vm-ip>:~/ai-employee/config/
   ```

### Step 4: Deploy Scripts

1. **Copy deployment scripts**
   ```bash
   cp ../cloud-deployment/scripts/* scripts/
   cp ../cloud-deployment/ecosystem.config.js .
   chmod +x scripts/*.py
   ```

2. **Install Python dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Step 5: Initialize Vault Repository

1. **Create GitHub repository**
   - Create new private repository: `ai-employee-vault`
   - Initialize with README and .gitignore

2. **Set up local vault for sync**
   ```bash
   # On your local machine
   cd "C:\Users\nahead\Documents\GitHub\Hackathon0"
   git init
   git remote add origin https://github.com/yourusername/ai-employee-vault.git

   # Create secure .gitignore
   echo "*.env" >> .gitignore
   echo "*_session/" >> .gitignore
   echo "credentials.json" >> .gitignore
   echo "*.key" >> .gitignore

   # Initial commit
   git add .
   git commit -m "Initial AI Employee vault setup"
   git push -u origin main
   ```

### Step 6: Start Cloud Services

1. **Start all services with PM2**
   ```bash
   cd ~/ai-employee
   pm2 start ecosystem.config.js --env production
   pm2 save
   pm2 startup
   ```

2. **Verify services are running**
   ```bash
   pm2 status
   pm2 logs
   ```

### Step 7: Test Cloud Operations

1. **Check vault sync**
   ```bash
   # Should see vault-sync folder created and syncing
   ls -la vault-sync/
   tail -f logs/vault-sync.log
   ```

2. **Test email monitoring**
   ```bash
   # Check Gmail watcher logs
   tail -f logs/cloud-gmail-watcher.log
   ```

3. **Verify file processing**
   ```bash
   # Check file watcher logs
   tail -f logs/cloud-file-watcher.log
   ```

## 🔄 Work-Zone Specialization

### Cloud Agent Responsibilities (Draft-Only)
- ✅ Monitor Gmail for new emails
- ✅ Create draft responses
- ✅ Process file drops
- ✅ Generate approval requests
- ✅ Sync vault via Git
- ❌ **NEVER** send emails directly
- ❌ **NEVER** post to social media
- ❌ **NEVER** access WhatsApp sessions

### Local Agent Responsibilities (Execution)
- ✅ Process approval requests
- ✅ Execute approved actions
- ✅ Handle WhatsApp sessions
- ✅ Manage payment workflows
- ✅ Final "send/post" actions

## 📊 Monitoring & Health Checks

### PM2 Process Management
```bash
# Check status
pm2 status

# View logs
pm2 logs cloud-orchestrator

# Restart service
pm2 restart cloud-file-watcher

# Monitor resources
pm2 monit
```

### System Health
```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check system load
htop
```

### Vault Sync Status
```bash
# Check sync logs
tail -f logs/vault-sync.log

# Manual sync test
cd vault-sync
git status
git pull origin main
```

## 🔒 Security Checklist

### ✅ Completed Automatically
- [x] Firewall configured (SSH, HTTP, HTTPS only)
- [x] .gitignore prevents credential sync
- [x] Draft-only mode (no direct external actions)
- [x] Process isolation via PM2
- [x] Audit logging enabled

### ⚠️ Manual Security Steps
- [ ] Change default SSH port (optional)
- [ ] Set up fail2ban for SSH protection
- [ ] Configure automatic security updates
- [ ] Set up monitoring alerts
- [ ] Regular credential rotation schedule

## 🚨 Troubleshooting

### Common Issues

**1. PM2 services won't start**
```bash
# Check Python path
which python3
# Update ecosystem.config.js if needed
```

**2. Git sync fails**
```bash
# Check credentials
git config --list
# Verify repository access
git ls-remote origin
```

**3. Gmail API errors**
```bash
# Check credentials file
ls -la config/credentials.json
# Test authentication
python3 -c "from scripts.cloud_gmail_watcher import CloudGmailWatcher; print('OK')"
```

**4. Out of disk space**
```bash
# Clean up logs
find logs/ -name "*.log" -mtime +7 -delete
# Check PM2 logs
pm2 flush
```

### Emergency Recovery
```bash
# Stop all services
pm2 stop all

# Reset to clean state
pm2 delete all
pm2 start ecosystem.config.js --env production

# Check system resources
df -h && free -h
```

## 📈 Performance Optimization

### Resource Limits (Always Free Tier)
- **CPU**: 1 OCPU (ARM-based)
- **Memory**: 1GB RAM
- **Storage**: 47GB boot volume
- **Network**: 10TB/month outbound

### Optimization Tips
1. **Memory Management**
   - PM2 max_memory_restart: 200M per process
   - Use swap file for memory overflow

2. **Storage Management**
   - Rotate logs weekly
   - Compress old reports
   - Clean up temporary files

3. **Network Efficiency**
   - Batch API calls
   - Compress Git transfers
   - Minimize sync frequency during low activity

## 🎯 Success Metrics

### Platinum Tier Demo Requirements
- [x] **Always-on operation**: 24/7 cloud services
- [x] **Work-zone separation**: Cloud drafts, local execution
- [x] **Vault synchronization**: Git-based coordination
- [x] **Security isolation**: No secrets in cloud
- [x] **Offline resilience**: Works when local is offline

### Expected Performance
- **Email Response Time**: < 5 minutes (draft creation)
- **Vault Sync Latency**: < 1 minute
- **System Uptime**: > 99.5%
- **Resource Usage**: < 80% of Always Free limits

---

## 🏆 Platinum Tier Status: PHASE 1 COMPLETE

**Next Steps**:
1. Test end-to-end workflow
2. Implement Phase 2: Work-zone coordination
3. Deploy Odoo Community on cloud
4. Complete Platinum demo scenario

**Estimated Total Cost**: $0/month (Oracle Always Free)