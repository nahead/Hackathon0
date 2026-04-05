#!/bin/bash
# Quick deployment script for testing cloud infrastructure
# Run this after completing the main setup

set -e

echo "🧪 Testing Cloud Infrastructure Deployment"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "ecosystem.config.js" ]; then
    echo "❌ Error: Run this script from the ai-employee directory"
    exit 1
fi

# Test 1: Verify Python environment
echo "📋 Test 1: Python Environment"
if source venv/bin/activate && python --version; then
    echo "✅ Python environment OK"
else
    echo "❌ Python environment failed"
    exit 1
fi

# Test 2: Check required scripts
echo "📋 Test 2: Required Scripts"
required_scripts=(
    "scripts/cloud_file_watcher.py"
    "scripts/cloud_gmail_watcher.py"
    "scripts/vault_sync_daemon.py"
    "scripts/cloud_orchestrator.py"
)

for script in "${required_scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "✅ $script exists"
    else
        echo "❌ $script missing"
        exit 1
    fi
done

# Test 3: Verify PM2 configuration
echo "📋 Test 3: PM2 Configuration"
if pm2 --version > /dev/null 2>&1; then
    echo "✅ PM2 installed"

    # Validate ecosystem config
    if node -e "require('./ecosystem.config.js')"; then
        echo "✅ PM2 configuration valid"
    else
        echo "❌ PM2 configuration invalid"
        exit 1
    fi
else
    echo "❌ PM2 not installed"
    exit 1
fi

# Test 4: Check environment configuration
echo "📋 Test 4: Environment Configuration"
if [ -f ".env" ]; then
    echo "✅ .env file exists"

    # Check critical variables
    if grep -q "VAULT_REPO_URL" .env && grep -q "VAULT_PATH" .env; then
        echo "✅ Critical environment variables configured"
    else
        echo "⚠️  Warning: Some environment variables may be missing"
    fi
else
    echo "⚠️  Warning: .env file not found (using .env.template)"
fi

# Test 5: Directory structure
echo "📋 Test 5: Directory Structure"
required_dirs=(
    "logs"
    "config"
    "scripts"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir directory exists"
    else
        echo "📁 Creating $dir directory"
        mkdir -p "$dir"
    fi
done

# Test 6: Permissions
echo "📋 Test 6: File Permissions"
chmod +x scripts/*.py
echo "✅ Script permissions set"

# Test 7: Python dependencies
echo "📋 Test 7: Python Dependencies"
source venv/bin/activate
if pip check > /dev/null 2>&1; then
    echo "✅ Python dependencies OK"
else
    echo "⚠️  Warning: Some Python dependencies may have issues"
fi

# Test 8: Git configuration
echo "📋 Test 8: Git Configuration"
if git --version > /dev/null 2>&1; then
    echo "✅ Git installed"

    if git config user.name > /dev/null 2>&1; then
        echo "✅ Git user configured"
    else
        echo "⚠️  Warning: Git user not configured"
    fi
else
    echo "❌ Git not installed"
    exit 1
fi

echo ""
echo "🎉 Cloud Infrastructure Test Complete!"
echo ""
echo "Next steps:"
echo "1. Configure .env file with your actual values"
echo "2. Upload Gmail credentials to config/ directory"
echo "3. Set up GitHub repository for vault sync"
echo "4. Run: pm2 start ecosystem.config.js --env production"
echo "5. Monitor with: pm2 status && pm2 logs"
echo ""
echo "🚀 Ready for Platinum Tier deployment!"