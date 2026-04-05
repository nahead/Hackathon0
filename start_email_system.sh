#!/bin/bash
# Complete AI Employee Email System Startup Script (Bash Version)
# Starts all components for automated email handling

echo "============================================================"
echo "   AI EMPLOYEE EMAIL AUTOMATION SYSTEM"
echo "============================================================"
echo ""
echo "Starting all components..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    echo ""
    echo "Please create .env file with:"
    echo "SMTP_USER=your-email@gmail.com"
    echo "SMTP_PASS=your-16-char-app-password"
    echo ""
    exit 1
fi

# Check Python
if ! command -v python &> /dev/null; then
    echo "[ERROR] Python not found! Please install Python 3.13+"
    exit 1
fi

echo "[OK] Python found"
echo ""

# Install dependencies if needed
echo "[STEP 1] Checking dependencies..."
pip install -q python-dotenv 2>/dev/null
echo "[OK] Dependencies ready"
echo ""

# Start Gmail Watcher in background
echo "[STEP 2] Starting Gmail Watcher..."
python simple_gmail_watcher.py > AI_Employee_Vault/Logs/gmail_watcher.log 2>&1 &
GMAIL_PID=$!
sleep 2
echo "[OK] Gmail Watcher started (PID: $GMAIL_PID)"
echo ""

# Start Email Workflow Orchestrator in background
echo "[STEP 3] Starting Email Workflow Orchestrator..."
python email_workflow_orchestrator.py > AI_Employee_Vault/Logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
sleep 2
echo "[OK] Email Orchestrator started (PID: $ORCHESTRATOR_PID)"
echo ""

echo "============================================================"
echo "   SYSTEM RUNNING!"
echo "============================================================"
echo ""
echo "Components running:"
echo "  1. Gmail Watcher (PID: $GMAIL_PID)"
echo "  2. Email Orchestrator (PID: $ORCHESTRATOR_PID)"
echo ""
echo "Workflow:"
echo "  Email arrives → Needs_Action → Draft → Pending_Approval"
echo "  You approve → Approved → Email sent → Done"
echo ""
echo "Folders to monitor:"
echo "  - AI_Employee_Vault/Pending_Approval (review drafts here)"
echo "  - AI_Employee_Vault/Approved (move approved drafts here)"
echo ""
echo "Logs:"
echo "  - AI_Employee_Vault/Logs/gmail_watcher.log"
echo "  - AI_Employee_Vault/Logs/email_workflow.log"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Save PIDs to file for cleanup
echo $GMAIL_PID > /tmp/ai_employee_gmail.pid
echo $ORCHESTRATOR_PID > /tmp/ai_employee_orchestrator.pid

# Wait for Ctrl+C
trap cleanup INT

cleanup() {
    echo ""
    echo "Stopping services..."
    kill $GMAIL_PID 2>/dev/null
    kill $ORCHESTRATOR_PID 2>/dev/null
    rm -f /tmp/ai_employee_gmail.pid
    rm -f /tmp/ai_employee_orchestrator.pid
    echo "[OK] All services stopped"
    exit 0
}

# Keep script running
while true; do
    # Check if processes are still running
    if ! kill -0 $GMAIL_PID 2>/dev/null; then
        echo "[WARNING] Gmail Watcher stopped unexpectedly!"
        echo "Check logs: AI_Employee_Vault/Logs/gmail_watcher.log"
    fi

    if ! kill -0 $ORCHESTRATOR_PID 2>/dev/null; then
        echo "[WARNING] Email Orchestrator stopped unexpectedly!"
        echo "Check logs: AI_Employee_Vault/Logs/orchestrator.log"
    fi

    sleep 10
done
