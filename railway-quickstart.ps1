# Railway Deployment - Quick Start Script

# Step 1: Install Railway CLI
Write-Host "=== Railway Deployment - Quick Start ===" -ForegroundColor Cyan
Write-Host ""

# Check if Railway CLI is installed
$railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayInstalled) {
    Write-Host "Installing Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
    Write-Host "✓ Railway CLI installed" -ForegroundColor Green
} else {
    Write-Host "✓ Railway CLI already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Login to Railway:"
Write-Host "   railway login" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Initialize project:"
Write-Host "   railway init" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Set environment variables:"
Write-Host "   railway variables set AGENT_TYPE=cloud" -ForegroundColor Yellow
Write-Host "   railway variables set SMTP_USER=your-email@gmail.com" -ForegroundColor Yellow
Write-Host "   railway variables set SMTP_PASS=your-app-password" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Deploy:"
Write-Host "   railway up" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Monitor:"
Write-Host "   railway logs --follow" -ForegroundColor Yellow
Write-Host ""
Write-Host "Full guide: RAILWAY_DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
