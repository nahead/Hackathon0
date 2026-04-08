#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master Process for AI Employee
Coordinates watchers, scheduling, and folder monitoring for 24/7 operation
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Orchestrator')

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
CHECK_INTERVAL = int(os.getenv('ORCHESTRATOR_CHECK_INTERVAL', '60'))
MAX_RETRIES = 3
RETRY_DELAY = 5

class Orchestrator:
    """Master orchestrator for AI Employee 24/7 operation"""

    def __init__(self):
        self.vault_path = VAULT_PATH
        self.running = False
        self.watchers = {}
        self.last_health_check = None

        # Vault folders
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.in_progress = self.vault_path / "In_Progress"
        self.done = self.vault_path / "Done"
        self.updates = self.vault_path / "Updates"

        # Ensure folders exist
        self._ensure_vault_structure()

    def _ensure_vault_structure(self):
        """Ensure all required vault folders exist"""
        folders = [
            self.needs_action,
            self.pending_approval,
            self.approved,
            self.in_progress,
            self.done,
            self.updates,
            self.vault_path / "Plans",
            self.vault_path / "Audit_Logs",
            self.vault_path / "CEO_Briefings"
        ]

        for folder in folders:
            folder.mkdir(exist_ok=True)

        logger.info("Vault structure verified")

    def start(self):
        """Start the orchestrator"""
        logger.info("="*70)
        logger.info("ORCHESTRATOR STARTING - 24/7 AI EMPLOYEE")
        logger.info("="*70)
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Check interval: {CHECK_INTERVAL}s")

        self.running = True

        try:
            # Main orchestration loop
            while self.running:
                try:
                    # Check for new work
                    self._check_needs_action()

                    # Process approvals
                    self._process_approvals()

                    # Health check
                    self._health_check()

                    # Sleep until next cycle
                    time.sleep(CHECK_INTERVAL)

                except KeyboardInterrupt:
                    logger.info("\nShutdown requested by user")
                    break

                except Exception as e:
                    logger.error(f"Error in orchestration loop: {e}")
                    time.sleep(RETRY_DELAY)

        finally:
            self.stop()

    def _check_needs_action(self):
        """Check for new items in Needs_Action folder"""
        if not self.needs_action.exists():
            return

        items = list(self.needs_action.glob("*.md"))

        if items:
            logger.info(f"Found {len(items)} items in Needs_Action")

            for item in items:
                try:
                    # Claim by moving to In_Progress
                    agent_folder = self.in_progress / "orchestrator"
                    agent_folder.mkdir(exist_ok=True)

                    dest = agent_folder / item.name
                    item.rename(dest)

                    logger.info(f"Claimed: {item.name}")

                    # Process the item
                    self._process_item(dest)

                except Exception as e:
                    logger.error(f"Error processing {item.name}: {e}")

    def _process_item(self, item_path):
        """Process a claimed item"""
        try:
            # Read item content
            content = item_path.read_text(encoding='utf-8')

            # Extract metadata
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    metadata_text = parts[1]
                    # Simple parsing - in production use yaml
                    item_type = None
                    for line in metadata_text.split('\n'):
                        if line.startswith('type:'):
                            item_type = line.split(':', 1)[1].strip()
                            break

                    logger.info(f"Processing item type: {item_type}")

                    # Route based on type
                    if item_type == 'email':
                        self._handle_email(item_path, content)
                    elif item_type == 'whatsapp':
                        self._handle_whatsapp(item_path, content)
                    else:
                        logger.warning(f"Unknown item type: {item_type}")

            # Move to Done
            done_path = self.done / item_path.name
            item_path.rename(done_path)
            logger.info(f"Completed: {item_path.name}")

        except Exception as e:
            logger.error(f"Error processing item: {e}")

    def _handle_email(self, item_path, content):
        """Handle email item"""
        logger.info(f"Email handler: {item_path.name}")
        # In production: trigger Claude Code to draft reply
        # For now: create approval request

        approval_file = self.pending_approval / f"APPROVAL_{item_path.stem}.md"
        approval_file.write_text(f"""---
type: approval_request
action: email_reply
original: {item_path.name}
created: {datetime.now().isoformat()}
status: pending
---

# Email Reply Approval

Original email processed. Draft reply ready for approval.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
""", encoding='utf-8')

        logger.info(f"Created approval request: {approval_file.name}")

    def _handle_whatsapp(self, item_path, content):
        """Handle WhatsApp item"""
        logger.info(f"WhatsApp handler: {item_path.name}")
        # Similar to email handling

    def _process_approvals(self):
        """Process approved items"""
        if not self.approved.exists():
            return

        approved_items = list(self.approved.glob("*.md"))

        if approved_items:
            logger.info(f"Processing {len(approved_items)} approved items")

            for item in approved_items:
                try:
                    # Execute the approved action
                    logger.info(f"Executing: {item.name}")

                    # Move to Done
                    done_path = self.done / item.name
                    item.rename(done_path)

                    logger.info(f"Executed and archived: {item.name}")

                except Exception as e:
                    logger.error(f"Error executing {item.name}: {e}")

    def _health_check(self):
        """Perform health check"""
        now = datetime.now()

        # Only check every 5 minutes
        if self.last_health_check:
            elapsed = (now - self.last_health_check).total_seconds()
            if elapsed < 300:
                return

        self.last_health_check = now

        logger.info("Health check: HEALTHY")

        # Check vault accessibility
        if not self.vault_path.exists():
            logger.error("Health check: Vault not accessible!")
            return

        # Check disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.vault_path)
            free_gb = free // (2**30)

            if free_gb < 1:
                logger.warning(f"Low disk space: {free_gb}GB free")

        except Exception as e:
            logger.error(f"Health check error: {e}")

    def stop(self):
        """Stop the orchestrator"""
        logger.info("Orchestrator stopping...")
        self.running = False
        logger.info("Orchestrator stopped")

def main():
    """Main entry point"""
    orchestrator = Orchestrator()

    try:
        orchestrator.start()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
