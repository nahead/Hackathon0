#!/usr/bin/env python3
"""
Local Orchestrator - Platinum Tier
Runs on local machine, handles approvals and final actions
"""
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
PENDING_APPROVAL = VAULT_PATH / 'Pending_Approval'
APPROVED = VAULT_PATH / 'Approved'
DONE = VAULT_PATH / 'Done'
IN_PROGRESS_LOCAL = VAULT_PATH / 'In_Progress' / 'local'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[LOCAL] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LocalOrchestrator')

class ApprovalHandler(FileSystemEventHandler):
    """Monitors Pending_Approval folder for new approval requests"""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)
        if filepath.suffix != '.md':
            return

        logger.info(f"New approval request detected: {filepath.name}")
        self.process_approval_request(filepath)

    def process_approval_request(self, filepath: Path):
        """Process approval request - wait for human to move to Approved"""
        logger.info(f"Waiting for human approval: {filepath.name}")
        logger.info(f"To approve: Move {filepath.name} to Approved/ folder")
        logger.info(f"To reject: Move {filepath.name} to Rejected/ folder")

class ApprovedHandler(FileSystemEventHandler):
    """Monitors Approved folder for approved actions"""

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = Path(event.src_path)
        if filepath.suffix != '.md':
            return

        logger.info(f"Approved action detected: {filepath.name}")
        self.execute_approved_action(filepath)

    def execute_approved_action(self, filepath: Path):
        """Execute the approved action via MCP"""
        try:
            # Read the approval file
            content = filepath.read_text()

            # Parse action type from filename or content
            if 'EMAIL' in filepath.name:
                self.execute_email_action(filepath, content)
            elif 'WHATSAPP' in filepath.name:
                self.execute_whatsapp_action(filepath, content)
            elif 'LINKEDIN' in filepath.name:
                self.execute_linkedin_action(filepath, content)
            elif 'FACEBOOK' in filepath.name:
                self.execute_facebook_action(filepath, content)
            elif 'TWITTER' in filepath.name:
                self.execute_twitter_action(filepath, content)
            else:
                logger.warning(f"Unknown action type: {filepath.name}")
                return

            # Move to Done
            done_path = DONE / filepath.name
            filepath.rename(done_path)
            logger.info(f"Action completed and moved to Done: {filepath.name}")

        except Exception as e:
            logger.error(f"Error executing action: {e}")

    def execute_email_action(self, filepath: Path, content: str):
        """Execute email send via MCP"""
        logger.info(f"[LOCAL] Executing email send: {filepath.name}")
        # TODO: Call Email MCP server
        # For now, just log
        logger.info("[LOCAL] Email sent successfully (MCP integration pending)")

    def execute_whatsapp_action(self, filepath: Path, content: str):
        """Execute WhatsApp send via MCP"""
        logger.info(f"[LOCAL] Executing WhatsApp send: {filepath.name}")
        # TODO: Call WhatsApp MCP server
        logger.info("[LOCAL] WhatsApp message sent successfully (MCP integration pending)")

    def execute_linkedin_action(self, filepath: Path, content: str):
        """Execute LinkedIn post via API"""
        logger.info(f"[LOCAL] Executing LinkedIn post: {filepath.name}")
        # TODO: Call LinkedIn API
        logger.info("[LOCAL] LinkedIn post published successfully (API integration pending)")

    def execute_facebook_action(self, filepath: Path, content: str):
        """Execute Facebook post via API"""
        logger.info(f"[LOCAL] Executing Facebook post: {filepath.name}")
        # TODO: Call Facebook API
        logger.info("[LOCAL] Facebook post published successfully (API integration pending)")

    def execute_twitter_action(self, filepath: Path, content: str):
        """Execute Twitter post via API"""
        logger.info(f"[LOCAL] Executing Twitter post: {filepath.name}")
        # TODO: Call Twitter API
        logger.info("[LOCAL] Twitter post published successfully (API integration pending)")

def sync_vault():
    """Pull latest changes from vault Git repository"""
    try:
        logger.info("Syncing vault from Git...")
        os.system(f'cd {VAULT_PATH} && git pull origin main')
        logger.info("Vault synced successfully")
    except Exception as e:
        logger.error(f"Vault sync failed: {e}")

def main():
    """Main local orchestrator loop"""
    logger.info("="*60)
    logger.info("LOCAL ORCHESTRATOR - PLATINUM TIER")
    logger.info("="*60)
    logger.info(f"Vault Path: {VAULT_PATH}")
    logger.info(f"Monitoring: {PENDING_APPROVAL}")
    logger.info(f"Monitoring: {APPROVED}")
    logger.info("="*60)

    # Ensure folders exist
    PENDING_APPROVAL.mkdir(parents=True, exist_ok=True)
    APPROVED.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)
    IN_PROGRESS_LOCAL.mkdir(parents=True, exist_ok=True)

    # Initial vault sync
    sync_vault()

    # Setup file watchers
    approval_observer = Observer()
    approval_observer.schedule(ApprovalHandler(), str(PENDING_APPROVAL), recursive=False)
    approval_observer.start()

    approved_observer = Observer()
    approved_observer.schedule(ApprovedHandler(), str(APPROVED), recursive=False)
    approved_observer.start()

    logger.info("Local Orchestrator started. Monitoring for approvals...")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            # Sync vault every 60 seconds
            time.sleep(60)
            sync_vault()
    except KeyboardInterrupt:
        logger.info("Stopping Local Orchestrator...")
        approval_observer.stop()
        approved_observer.stop()

    approval_observer.join()
    approved_observer.join()
    logger.info("Local Orchestrator stopped")

if __name__ == '__main__':
    main()
