@echo off
REM Complete AI Employee Email System Startup Script
REM Starts all components for automated email handling

echo ============================================================
echo    AI EMPLOYEE EMAIL AUTOMATION SYSTEM
echo ============================================================
echo.
echo Starting all components...
echo.

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file with:
    echo SMTP_USER=your-email@gmail.com
    echo SMTP_PASS=your-16-char-app-password
    echo.
    pause
    exit /b 1
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.13+
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install dependencies if needed
echo [STEP 1] Checking dependencies...
pip install -q python-dotenv 2>nul
echo [OK] Dependencies ready
echo.

REM Start Gmail Watcher in background
echo [STEP 2] Starting Gmail Watcher...
start "Gmail Watcher" /MIN python simple_gmail_watcher.py
timeout /t 2 /nobreak >nul
echo [OK] Gmail Watcher started
echo.

REM Start Email Workflow Orchestrator in background
echo [STEP 3] Starting Email Workflow Orchestrator...
start "Email Orchestrator" /MIN python email_workflow_orchestrator.py
timeout /t 2 /nobreak >nul
echo [OK] Email Orchestrator started
echo.

echo ============================================================
echo    SYSTEM RUNNING!
echo ============================================================
echo.
echo Components running:
echo   1. Gmail Watcher - Monitors inbox for new emails
echo   2. Email Orchestrator - Drafts responses and sends approved emails
echo.
echo Workflow:
echo   Email arrives ^> Needs_Action ^> Draft ^> Pending_Approval
echo   You approve ^> Approved ^> Email sent ^> Done
echo.
echo Folders to monitor:
echo   - AI_Employee_Vault/Pending_Approval (review drafts here)
echo   - AI_Employee_Vault/Approved (move approved drafts here)
echo.
echo Logs:
echo   - AI_Employee_Vault/Logs/gmail_watcher.log
echo   - AI_Employee_Vault/Logs/email_workflow.log
echo.
echo Press any key to stop all services...
pause >nul

REM Stop all services
echo.
echo Stopping services...
taskkill /FI "WINDOWTITLE eq Gmail Watcher*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Email Orchestrator*" /F >nul 2>&1
echo [OK] All services stopped
echo.
pause
