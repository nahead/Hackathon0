#!/usr/bin/env python3
"""
Vault Sync Automation - Platinum Tier
Automatically syncs vault between Cloud and Local agents via Git
"""
import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

logging.basicConfig(
    level=logging.INFO,
    format='[VAULT-SYNC] %(asctime)s - %(message)s'
)
logger = logging.getLogger('VaultSync')

def git_pull():
    """Pull latest changes from remote"""
    try:
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            logger.info("✓ Pulled latest changes")
            return True
        else:
            logger.error(f"Pull failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Pull error: {e}")
        return False

def git_push():
    """Push local changes to remote"""
    try:
        # Add all changes
        subprocess.run(
            ['git', 'add', '.'],
            cwd=VAULT_PATH,
            check=True,
            timeout=10
        )

        # Check if there are changes to commit
        status = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True,
            timeout=10
        )

        if not status.stdout.strip():
            logger.info("No changes to push")
            return True

        # Commit changes
        commit_msg = f"Auto-sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=VAULT_PATH,
            check=True,
            timeout=10
        )

        # Push to remote
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=VAULT_PATH,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info("✓ Pushed local changes")
            return True
        else:
            logger.error(f"Push failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Push error: {e}")
        return False

def sync_vault():
    """Full sync: pull then push"""
    logger.info("="*50)
    logger.info("Starting vault sync...")

    # Pull first to get latest changes
    if not git_pull():
        logger.warning("Pull failed, attempting to continue...")

    # Push local changes
    if not git_push():
        logger.warning("Push failed")
        return False

    logger.info("Vault sync complete")
    logger.info("="*50)
    return True

if __name__ == '__main__':
    sync_vault()
