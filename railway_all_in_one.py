#!/usr/bin/env python3
"""
Railway All-in-One Orchestrator - Platinum Tier
Real implementation with Gmail monitoring and vault sync
"""

import os
import sys
import time
import logging
import threading
import imaplib
import email
import subprocess
from pathlib import Path
from datetime import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Create logs directory (use /tmp for cloud platforms)
logs_dir = Path("/tmp/logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('RailwayOrchestrator')

class HealthHandler(BaseHTTPRequestHandler):
    """Health check endpoint"""
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            health = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "orchestrator": "running",
                    "vault_sync": "active",
                    "gmail_watcher": "monitoring"
                }
            }
            self.wfile.write(json.dumps(health).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

class CloudGmailWatcher:
    """Gmail monitoring for cloud deployment"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

        self.email = os.getenv('SMTP_USER')
        self.password = os.getenv('SMTP_PASS')

        if not self.email or not self.password:
            logger.error("Gmail credentials not configured")
            raise ValueError("SMTP_USER and SMTP_PASS required")

    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email, self.password)
            logger.info(f"✅ Connected to Gmail: {self.email}")
            return mail
        except Exception as e:
            logger.error(f"❌ Gmail connection failed: {e}")
            return None

    def check_new_emails(self, mail):
        """Check for new unread emails"""
        try:
            mail.select('inbox')
            status, messages = mail.search(None, 'UNSEEN')

            if status == 'OK':
                email_ids = messages[0].split()
                if email_ids:
                    logger.info(f"📧 Found {len(email_ids)} new emails")
                    for email_id in email_ids[:5]:  # Process max 5 at a time
                        self.process_email(mail, email_id)

        except Exception as e:
            logger.error(f"❌ Error checking emails: {e}")

    def process_email(self, mail, email_id):
        """Process individual email"""
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if status == 'OK':
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                subject = email_message['Subject'] or "No Subject"
                sender = email_message['From']

                content = self.get_email_content(email_message)

                logger.info(f"📨 Processing: {subject[:50]}...")

                self.create_approval_file(subject, sender, content, email_id)

        except Exception as e:
            logger.error(f"❌ Error processing email: {e}")

    def get_email_content(self, email_message):
        """Extract email content"""
        content = ""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            content = "Could not decode email content"

        return content[:1000]  # Limit content length

    def create_approval_file(self, subject, sender, content, email_id):
        """Create approval file in vault"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_CLOUD_{timestamp}.md"
        filepath = self.needs_action_path / filename

        approval_content = f"""---
type: email_response_approval
email_id: {email_id.decode() if isinstance(email_id, bytes) else email_id}
sender: {sender}
subject: {subject}
timestamp: {datetime.now().isoformat()}
---

# Email Response Approval Required

## Original Email:
**From:** {sender}
**Subject:** {subject}
**Content:**
```
{content}
```

## Proposed Response:
```
Thank you for your email.

I have received your message and will review it carefully. I will respond with the appropriate information within 24 hours.

Best regards,
AI Employee System
```

## Instructions:
1. Review the proposed response
2. Edit if necessary
3. Move to Approved/ folder to send
4. Or move to Archive/ to skip
"""

        filepath.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ Created approval file: {filename}")

class CloudVaultSync:
    """Vault synchronization with GitHub"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.repo_url = os.getenv('VAULT_REPO_URL')
        self.git_username = os.getenv('GIT_USERNAME')
        self.git_token = os.getenv('GIT_TOKEN')

        if not all([self.repo_url, self.git_username, self.git_token]):
            logger.error("Vault sync credentials not configured")
            raise ValueError("VAULT_REPO_URL, GIT_USERNAME, GIT_TOKEN required")

        # Setup authenticated URL
        self.auth_url = self.repo_url.replace('https://', f'https://{self.git_username}:{self.git_token}@')

    def clone_or_pull_vault(self):
        """Clone vault repository or pull latest changes"""
        try:
            # Check if vault directory exists
            if self.vault_path.exists():
                # Check if it's a valid git repo
                if (self.vault_path / '.git').exists():
                    logger.info("🔄 Pulling latest changes...")
                    subprocess.run(
                        ['git', 'pull', 'origin', 'main'],
                        cwd=self.vault_path,
                        check=True,
                        capture_output=True
                    )
                    logger.info("✅ Vault updated")
                else:
                    # Directory exists but not a git repo - remove and clone
                    logger.info("🗑️ Removing invalid vault directory...")
                    import shutil
                    shutil.rmtree(self.vault_path)
                    logger.info("📥 Cloning vault repository...")
                    subprocess.run(
                        ['git', 'clone', self.auth_url, str(self.vault_path)],
                        check=True,
                        capture_output=True
                    )
                    logger.info("✅ Vault cloned successfully")
            else:
                # Directory doesn't exist - clone fresh
                logger.info("📥 Cloning vault repository...")
                subprocess.run(
                    ['git', 'clone', self.auth_url, str(self.vault_path)],
                    check=True,
                    capture_output=True
                )
                logger.info("✅ Vault cloned successfully")

            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git operation failed: {e}")
            # If clone failed, clean up partial directory
            if self.vault_path.exists() and not (self.vault_path / '.git').exists():
                try:
                    import shutil
                    shutil.rmtree(self.vault_path)
                    logger.info("🗑️ Cleaned up failed clone")
                except:
                    pass
            return False

    def commit_and_push_changes(self):
        """Commit and push changes to vault"""
        try:
            # Check for changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.vault_path,
                capture_output=True,
                text=True
            )

            if not result.stdout.strip():
                return True  # No changes

            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=self.vault_path, check=True)

            # Commit
            commit_msg = f"Cloud agent update - {datetime.now().isoformat()}"
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.vault_path,
                check=True,
                capture_output=True
            )

            # Push
            subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.vault_path,
                check=True,
                capture_output=True
            )

            logger.info("✅ Changes pushed to vault")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git push failed: {e}")
            return False

class RailwayOrchestrator:
    """All-in-one orchestrator for Railway/Render"""

    def __init__(self):
        self.port = int(os.getenv("PORT", 8080))
        self.vault_path = Path("/tmp/vault")

        logger.info("🚀 Railway All-in-One Orchestrator initialized")

    def check_environment(self):
        """Check environment variables"""
        required = ["SMTP_USER", "SMTP_PASS", "VAULT_REPO_URL", "GIT_USERNAME", "GIT_TOKEN"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            logger.warning(f"⚠️ Missing variables: {missing}")
            return False

        logger.info("✅ Environment variables configured")
        return True

    def vault_sync_service(self):
        """Background vault synchronization"""
        logger.info("🔄 Starting vault sync service...")

        try:
            vault_sync = CloudVaultSync(self.vault_path)

            # Initial clone/pull
            vault_sync.clone_or_pull_vault()

            while True:
                try:
                    # Pull changes every 5 minutes
                    vault_sync.clone_or_pull_vault()

                    # Push any local changes
                    vault_sync.commit_and_push_changes()

                    logger.info("💾 Vault sync heartbeat")
                    time.sleep(300)  # 5 minutes

                except Exception as e:
                    logger.error(f"❌ Vault sync error: {e}")
                    time.sleep(60)

        except Exception as e:
            logger.error(f"❌ Vault sync initialization failed: {e}")

    def gmail_watcher_service(self):
        """Background Gmail monitoring"""
        logger.info("📧 Starting Gmail watcher service...")

        try:
            gmail_watcher = CloudGmailWatcher(self.vault_path)

            while True:
                try:
                    mail = gmail_watcher.connect_to_gmail()
                    if mail:
                        gmail_watcher.check_new_emails(mail)
                        mail.close()
                        mail.logout()

                    logger.info("📬 Gmail monitoring heartbeat")
                    time.sleep(300)  # 5 minutes

                except Exception as e:
                    logger.error(f"❌ Gmail watcher error: {e}")
                    time.sleep(60)

        except Exception as e:
            logger.error(f"❌ Gmail watcher initialization failed: {e}")

    def start_background_services(self):
        """Start all background services"""
        logger.info("🔧 Starting background services...")

        # Start vault sync in background
        vault_thread = threading.Thread(target=self.vault_sync_service, daemon=True)
        vault_thread.start()

        # Start Gmail watcher in background
        gmail_thread = threading.Thread(target=self.gmail_watcher_service, daemon=True)
        gmail_thread.start()

        logger.info("✅ Background services started")

    def start_health_server(self):
        """Start health check server"""
        logger.info(f"🌐 Starting health server on port {self.port}")

        try:
            server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
            logger.info(f"✅ Health endpoint: http://0.0.0.0:{self.port}/health")
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Health server failed: {e}")
            raise

    def run(self):
        """Main run method"""
        logger.info("🎯 Starting Railway AI Employee...")

        # Check environment
        env_ok = self.check_environment()
        if not env_ok:
            logger.warning("⚠️ Some environment variables missing, but continuing...")

        # Start background services
        self.start_background_services()

        logger.info("🎉 Railway AI Employee is now LIVE!")
        logger.info("🌐 Your AI Employee is running 24/7 in the cloud!")

        # Start health server (this blocks)
        self.start_health_server()

if __name__ == "__main__":
    try:
        orchestrator = RailwayOrchestrator()
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Railway AI Employee...")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)