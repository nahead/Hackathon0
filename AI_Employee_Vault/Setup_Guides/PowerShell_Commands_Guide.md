# AI Employee - PowerShell Commands Guide
# Correct Commands for Windows PowerShell Users

## 🚀 DAILY POWERSHELL OPERATIONS

### 1. Start Your AI Employee System:
```powershell
python start_ai_employee_system.py
```

### 2. Check Daily CEO Briefing:
```powershell
Get-Content "AI_Employee_Vault\Briefings\CEO_Daily_Briefing_$(Get-Date -Format 'yyyy-MM-dd').md"
```

### 3. Check Pending Approvals:
```powershell
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md"
```

### 4. Approve LinkedIn Posts (Correct PowerShell Syntax):
```powershell
# Check what's pending first
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "LINKEDIN_POST_*.md"

# Move specific file to approved
Move-Item "AI_Employee_Vault\Pending_Approval\LINKEDIN_POST_*.md" "AI_Employee_Vault\Approved\"

# Or move all .md files from pending to approved
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md" | Move-Item -Destination "AI_Employee_Vault\Approved\"
```

### 5. Monitor Ralph Loop Activity:
```powershell
Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" -Tail 5
```

### 6. Check System Health:
```powershell
Get-Content "AI_Employee_Vault\Logs\error_recovery.log" -Tail 10
```

### 7. Generate Content Manually:
```powershell
python linkedin_automation.py
python ceo_briefing_system.py
```

## 📊 POWERSHELL MONITORING COMMANDS

### Real-Time Monitoring:
```powershell
# Watch Ralph loop activity (refresh every 5 seconds)
while ($true) {
    Clear-Host
    Write-Host "=== Ralph Loop Activity ===" -ForegroundColor Green
    Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" -Tail 5
    Start-Sleep 5
}
```

### System Performance:
```powershell
# Count total Ralph loops
(Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" | Select-String "Loop #").Count

# Check system data size
Get-ChildItem "AI_Employee_Vault\" -Recurse | Measure-Object -Property Length -Sum | Select-Object @{Name="Size(MB)";Expression={[math]::Round($_.Sum/1MB,2)}}

# Count generated files
(Get-ChildItem "AI_Employee_Vault\" -Recurse -Include "*.json","*.md","*.log").Count
```

### Business Intelligence:
```powershell
# List all CEO briefings
Get-ChildItem "AI_Employee_Vault\Briefings\" -Filter "*.md" | Sort-Object LastWriteTime -Descending

# List latest business audits
Get-ChildItem "AI_Employee_Vault\Audits\" -Filter "*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Check approved content
Get-ChildItem "AI_Employee_Vault\Approved\" -Filter "*.md" | Sort-Object LastWriteTime -Descending
```

## 🔧 POWERSHELL SYSTEM CONTROL

### Start/Stop System:
```powershell
# Start system
python start_ai_employee_system.py

# Check if Python processes are running
Get-Process python -ErrorAction SilentlyContinue

# Stop all Python processes (if needed)
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Restart system
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
python start_ai_employee_system.py
```

## 📱 CONTENT APPROVAL WORKFLOW (PowerShell)

### Step-by-Step Content Management:
```powershell
# 1. Check what needs approval
Write-Host "=== Pending Approvals ===" -ForegroundColor Yellow
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md" | Format-Table Name, LastWriteTime

# 2. Read content before approving
$pendingFiles = Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "LINKEDIN_POST_*.md"
foreach ($file in $pendingFiles) {
    Write-Host "=== Content: $($file.Name) ===" -ForegroundColor Cyan
    Get-Content $file.FullName | Select-Object -First 20
    Write-Host "========================" -ForegroundColor Cyan
}

# 3. Approve specific file
$fileToApprove = "LINKEDIN_POST_20260302_*.md"  # Replace with actual filename
Move-Item "AI_Employee_Vault\Pending_Approval\$fileToApprove" "AI_Employee_Vault\Approved\"

# 4. Approve all pending content
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md" | ForEach-Object {
    Write-Host "Approving: $($_.Name)" -ForegroundColor Green
    Move-Item $_.FullName "AI_Employee_Vault\Approved\"
}
```

## 🎯 POWERSHELL DAILY ROUTINE SCRIPT

### Create a Daily Check Script:
```powershell
# Save this as "Check-AIEmployee.ps1"
Write-Host "=== AI Employee Daily Status ===" -ForegroundColor Green

# Check if system is running
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "✅ System is running ($($pythonProcesses.Count) Python processes)" -ForegroundColor Green
} else {
    Write-Host "❌ System is not running" -ForegroundColor Red
}

# Check Ralph activity
Write-Host "`n=== Latest Ralph Activity ===" -ForegroundColor Cyan
Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" -Tail 3

# Check pending approvals
Write-Host "`n=== Pending Approvals ===" -ForegroundColor Yellow
$pending = Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md"
if ($pending) {
    $pending | Format-Table Name, LastWriteTime
} else {
    Write-Host "No pending approvals" -ForegroundColor Gray
}

# Check today's briefing
$todayBriefing = "AI_Employee_Vault\Briefings\CEO_Daily_Briefing_$(Get-Date -Format 'yyyy-MM-dd').md"
if (Test-Path $todayBriefing) {
    Write-Host "`n=== Today's CEO Briefing Available ===" -ForegroundColor Green
    Write-Host "Location: $todayBriefing"
} else {
    Write-Host "`n=== No CEO Briefing for Today ===" -ForegroundColor Yellow
}

# System performance
$totalLoops = (Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" | Select-String "Loop #").Count
$totalFiles = (Get-ChildItem "AI_Employee_Vault\" -Recurse -Include "*.json","*.md","*.log").Count
Write-Host "`n=== Performance Metrics ===" -ForegroundColor Magenta
Write-Host "Ralph Loops Completed: $totalLoops"
Write-Host "Total Files Generated: $totalFiles"
```

## 🚀 QUICK POWERSHELL COMMANDS

### Essential Daily Commands:
```powershell
# Start system
python start_ai_employee_system.py

# Quick status check
Get-Content "AI_Employee_Vault\Logs\ralph_loop.log" -Tail 3

# Check pending approvals
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md"

# Approve all content
Get-ChildItem "AI_Employee_Vault\Pending_Approval\" -Filter "*.md" | Move-Item -Destination "AI_Employee_Vault\Approved\"

# Read today's briefing
Get-Content "AI_Employee_Vault\Briefings\CEO_Daily_Briefing_$(Get-Date -Format 'yyyy-MM-dd').md"
```

---
**Now you have the correct PowerShell commands for your AI Employee!**
Use these commands in your Windows PowerShell terminal.