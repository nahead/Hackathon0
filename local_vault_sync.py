#!/usr/bin/env python3
"""
Local Vault Sync - Platinum Tier
Handles local side of vault synchronization with cloud agent
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('AI_Employee_Vault/Logs/local_vault_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('LocalVaultSync')

class LocalVaultSync:
    """Local vault synchronization for Platinum tier"""

    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.sync_interval = 60  # 1 minute

        # Initialize git if not already done
        self.initialize_git_repo()

        logger.info("Local Vault Sync initialized")

    def initialize_git_repo(self):
        """Initialize git repository if needed"""
        git_dir = self.vault_path / '.git'

        if not git_dir.exists():
            logger.info("Initializing git repository...")
            try:
                subprocess.run(['git', 'init'], cwd=self.vault_path, check=True)
                logger.info("Git repository initialized")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to initialize git: {e}")

    def sync_with_cloud(self):
        """Sync vault with cloud repository"""
        try:
            logger.info("Syncing vault with cloud...")

            # Check if remote is configured
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.warning("No remote repository configured. Skipping sync.")
                return False

            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=self.vault_path, check=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                # Commit changes
                commit_msg = f"Local agent sync - {datetime.now().isoformat()}"
                subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=self.vault_path,
                    check=True
                )
                logger.info("Local changes committed")

            # Pull remote changes
            subprocess.run(['git', 'pull', 'origin', 'main'], cwd=self.vault_path, check=True)

            # Push local changes
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=self.vault_path, check=True)

            logger.info("Vault sync completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Git sync failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return False

    def run_daemon(self):
        """Run sync daemon"""
        logger.info(f"Starting Local Vault Sync daemon (interval: {self.sync_interval}s)")

        while True:
            try:
                self.sync_with_cloud()
                time.sleep(self.sync_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down Local Vault Sync...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(60)

def main():
    sync = LocalVaultSync()

    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        sync.run_daemon()
    else:
        sync.sync_with_cloud()

if __name__ == "__main__":
    main()
