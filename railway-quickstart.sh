#!/bin/bash
# Railway Deployment - Quick Start Script

echo "=== Railway Deployment - Quick Start ==="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
    echo "✓ Railway CLI installed"
else
    echo "✓ Railway CLI already installed"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Login to Railway:"
echo "   railway login"
echo ""
echo "2. Initialize project:"
echo "   railway init"
echo ""
echo "3. Set environment variables:"
echo "   railway variables set AGENT_TYPE=cloud"
echo "   railway variables set SMTP_USER=your-email@gmail.com"
echo "   railway variables set SMTP_PASS=your-app-password"
echo ""
echo "4. Deploy:"
echo "   railway up"
echo ""
echo "5. Monitor:"
echo "   railway logs --follow"
echo ""
echo "Full guide: RAILWAY_DEPLOYMENT_GUIDE.md"
