#!/usr/bin/env python3
"""
Vault Sync Daemon - Platinum Tier
Handles Git-based synchronization between local and cloud vaults
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import json
import subprocess
import shutil
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-employee/logs/vault-sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VaultSyncDaemon')

class VaultSyncDaemon:
    """Git-based vault synchronization for cloud/local coordination"""

    def __init__(self, vault_path: str, repo_url: str, sync_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.repo_url = repo_url
        self.sync_interval = sync_interval

        # Git configuration
        self.git_config = {
            'user.name': 'AI Employee Cloud Agent',
            'user.email': 'cloud-agent@ai-employee.local'
        }

        # Sync status tracking
        self.last_sync = None
        self.sync_errors = 0
        self.max_errors = 5

        # Security: Files that should NEVER be synced
        self.excluded_patterns = {
            '*.env',
            '*.key',
            '*.pem',
            '*_session/',
            'whatsapp_session/',
            'linkedin_session/',
            'facebook_session/',
            'instagram_session/',
            'twitter_session/',
            '.wwebjs_*/',
            'credentials.json',
            'token.json',
            '*_token.json',
            'secrets/',
            '.secrets/',
            '__pycache__/',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        }

        self.initialize_repo()
        logger.info("Vault Sync Daemon initialized")

    def initialize_repo(self):
        """Initialize or clone the vault repository"""
        if not self.vault_path.exists():
            logger.info("Cloning vault repository...")
            self.run_git_command(['clone', self.repo_url, str(self.vault_path)])
        else:
            # Check if it's a git repository
            if not (self.vault_path / '.git').exists():
                logger.info("Initializing git repository...")
                self.run_git_command(['init'], cwd=self.vault_path)
                self.run_git_command(['remote', 'add', 'origin', self.repo_url], cwd=self.vault_path)

        # Configure git
        for key, value in self.git_config.items():
            self.run_git_command(['config', key, value], cwd=self.vault_path)

        # Ensure .gitignore exists with security patterns
        self.create_gitignore()

    def create_gitignore(self):
        """Create comprehensive .gitignore for security"""
        gitignore_path = self.vault_path / '.gitignore'

        gitignore_content = """# Security - NEVER commit these files
*.env
*.key
*.pem
*_session/
whatsapp_session/
linkedin_session/
facebook_session/
instagram_session/
twitter_session/
.wwebjs_*/
credentials.json
token.json
*_token.json
secrets/
.secrets/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# System files
.DS_Store
Thumbs.db
*.swp
*.swo
*~

# Logs (keep structure but not content)
logs/*.log
*.log

# Temporary files
tmp/
temp/
.tmp/

# Node modules
node_modules/

# IDE files
.vscode/
.idea/
*.sublime-*

# OS generated files
.directory
.fuse_hidden*
.nfs*
"""

        gitignore_path.write_text(gitignore_content)
        logger.info("Created secure .gitignore")

    def run_git_command(self, args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run git command with error handling"""
        cmd = ['git'] + args
        working_dir = cwd or self.vault_path

        try:
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"Git command failed: {' '.join(cmd)}")
                logger.error(f"Error: {result.stderr}")

            return result

        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Git command error: {e}")
            raise

    def pull_changes(self) -> bool:
        """Pull changes from remote repository"""
        try:
            logger.info("Pulling changes from remote...")

            # Fetch latest changes
            result = self.run_git_command(['fetch', 'origin'])
            if result.returncode != 0:
                return False

            # Check if there are changes to pull
            result = self.run_git_command(['rev-list', '--count', 'HEAD..origin/main'])
            if result.returncode == 0 and result.stdout.strip() != '0':
                # Pull changes
                result = self.run_git_command(['pull', 'origin', 'main'])
                if result.returncode == 0:
                    logger.info("Successfully pulled changes")
                    return True
                else:
                    logger.error("Failed to pull changes")
                    return False
            else:
                logger.debug("No changes to pull")
                return True

        except Exception as e:
            logger.error(f"Error pulling changes: {e}")
            return False

    def push_changes(self) -> bool:
        """Push local changes to remote repository"""
        try:
            # Check if there are changes to commit
            result = self.run_git_command(['status', '--porcelain'])
            if not result.stdout.strip():
                logger.debug("No changes to push")
                return True

            logger.info("Pushing local changes...")

            # Add all changes (respecting .gitignore)
            result = self.run_git_command(['add', '.'])
            if result.returncode != 0:
                return False

            # Commit changes
            commit_message = f"Cloud agent sync - {datetime.now().isoformat()}"
            result = self.run_git_command(['commit', '-m', commit_message])
            if result.returncode != 0:
                # No changes to commit
                if "nothing to commit" in result.stdout:
                    return True
                return False

            # Push to remote
            result = self.run_git_command(['push', 'origin', 'main'])
            if result.returncode == 0:
                logger.info("Successfully pushed changes")
                return True
            else:
                logger.error("Failed to push changes")
                return False

        except Exception as e:
            logger.error(f"Error pushing changes: {e}")
            return False

    def sync_vault(self) -> bool:
        """Perform bidirectional sync"""
        try:
            logger.info("Starting vault synchronization...")

            # First, pull any remote changes
            if not self.pull_changes():
                logger.error("Failed to pull remote changes")
                return False

            # Then, push any local changes
            if not self.push_changes():
                logger.error("Failed to push local changes")
                return False

            self.last_sync = datetime.now()
            self.sync_errors = 0
            logger.info("Vault synchronization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Vault sync error: {e}")
            self.sync_errors += 1
            return False

    def check_repo_health(self) -> Dict[str, any]:
        """Check repository health and status"""
        health = {
            'status': 'healthy',
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_errors': self.sync_errors,
            'repo_size': 0,
            'file_count': 0,
            'last_commit': None
        }

        try:
            # Get repository size
            if self.vault_path.exists():
                health['repo_size'] = sum(
                    f.stat().st_size for f in self.vault_path.rglob('*') if f.is_file()
                )
                health['file_count'] = len([f for f in self.vault_path.rglob('*') if f.is_file()])

            # Get last commit info
            result = self.run_git_command(['log', '-1', '--format=%H|%s|%ai'])
            if result.returncode == 0 and result.stdout.strip():
                commit_info = result.stdout.strip().split('|')
                health['last_commit'] = {
                    'hash': commit_info[0][:8],
                    'message': commit_info[1],
                    'date': commit_info[2]
                }

            # Check for sync issues
            if self.sync_errors >= self.max_errors:
                health['status'] = 'degraded'

        except Exception as e:
            logger.error(f"Health check error: {e}")
            health['status'] = 'error'

        return health

    def create_sync_report(self):
        """Create sync status report"""
        health = self.check_repo_health()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        report_content = f"""---
type: sync_report
created_at: {datetime.now().isoformat()}
agent: cloud_sync_daemon
---

# Vault Sync Status Report

## Health Status: {health['status'].upper()}

### Sync Statistics
- **Last Sync**: {health['last_sync'] or 'Never'}
- **Sync Errors**: {health['sync_errors']}/{self.max_errors}
- **Repository Size**: {health['repo_size']:,} bytes
- **File Count**: {health['file_count']:,}

### Last Commit
{f"- **Hash**: {health['last_commit']['hash']}" if health['last_commit'] else "- No commits found"}
{f"- **Message**: {health['last_commit']['message']}" if health['last_commit'] else ""}
{f"- **Date**: {health['last_commit']['date']}" if health['last_commit'] else ""}

### Security Status
- ✅ .gitignore configured with security patterns
- ✅ Sensitive files excluded from sync
- ✅ Git user configured for cloud agent

### Next Sync
Scheduled in {self.sync_interval} seconds

---
*Generated by Vault Sync Daemon*
"""

        # Save report
        reports_dir = self.vault_path / 'Reports' / 'Sync'
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / f'SYNC_REPORT_{timestamp}.md'
        report_file.write_text(report_content)

        logger.info(f"Sync report created: {report_file.name}")

    def run(self):
        """Main daemon loop"""
        logger.info(f"Starting Vault Sync Daemon (interval: {self.sync_interval}s)")

        while True:
            try:
                # Perform sync
                success = self.sync_vault()

                # Create periodic reports (every 10 syncs or on errors)
                if not success or (self.last_sync and
                    (datetime.now() - self.last_sync).total_seconds() > 600):
                    self.create_sync_report()

                # Check if we've exceeded error threshold
                if self.sync_errors >= self.max_errors:
                    logger.error(f"Too many sync errors ({self.sync_errors}). Entering degraded mode.")
                    time.sleep(self.sync_interval * 2)  # Longer wait in degraded mode
                else:
                    time.sleep(self.sync_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down Vault Sync Daemon...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in sync daemon: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function"""
    vault_path = os.getenv('VAULT_PATH', '/home/ubuntu/ai-employee/vault-sync')
    repo_url = os.getenv('VAULT_REPO_URL', 'https://github.com/username/ai-employee-vault.git')
    sync_interval = int(os.getenv('SYNC_INTERVAL', '60'))

    if not repo_url or repo_url == 'https://github.com/username/ai-employee-vault.git':
        logger.error("VAULT_REPO_URL environment variable must be set to your actual repository URL")
        sys.exit(1)

    daemon = VaultSyncDaemon(vault_path, repo_url, sync_interval)
    daemon.run()

if __name__ == "__main__":
    main()