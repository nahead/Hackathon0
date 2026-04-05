#!/usr/bin/env python3
"""
Email Workflow Orchestrator - Complete Automation
Automates: Needs_Action → Draft → Pending_Approval → Approved → Send Email

Flow:
1. Monitors Needs_Action for email files
2. Drafts response using Claude Code
3. Moves to Pending_Approval
4. Monitors Approved folder
5. Sends email when approved
"""

import os
import time
import json
import smtplib
import logging
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import subprocess
import re

# Load environment variables
load_dotenv()

class EmailWorkflowOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.done = self.vault_path / "Done"
        self.logs = self.vault_path / "Logs"

        # Create directories
        for path in [self.needs_action, self.pending_approval, self.approved, self.done, self.logs]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs / 'email_workflow.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Email configuration
        self.smtp_user = os.getenv('SMTP_USER', 'naheadj@gmail.com')
        self.smtp_pass = os.getenv('SMTP_PASS')

        if not self.smtp_pass:
            self.logger.error("SMTP_PASS not found in .env file!")
            raise ValueError("Please set SMTP_PASS in .env file")

        self.logger.info("[OK] Email Workflow Orchestrator initialized")
        self.logger.info(f"[EMAIL] {self.smtp_user}")
        self.logger.info(f"[VAULT] {self.vault_path}")

    def run(self):
        """Main orchestrator loop"""
        self.logger.info("[START] Starting Email Workflow Orchestrator...")
        self.logger.info("[MONITOR] Monitoring folders:")
        self.logger.info(f"   - Needs_Action: {self.needs_action}")
        self.logger.info(f"   - Approved: {self.approved}")

        while True:
            try:
                # Step 1: Process Needs_Action → Draft → Pending_Approval
                self.process_needs_action()

                # Step 2: Process Approved → Send Email → Done
                self.process_approved()

                # Wait before next check
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                self.logger.info("[STOP] Orchestrator stopped by user")
                break
            except Exception as e:
                self.logger.error(f"[ERROR] Error in orchestrator loop: {e}")
                time.sleep(60)  # Wait longer on error

    def process_needs_action(self):
        """Process emails in Needs_Action folder"""
        email_files = list(self.needs_action.glob("EMAIL_*.md"))

        if not email_files:
            return

        self.logger.info(f"[FOUND] Found {len(email_files)} emails in Needs_Action")

        for email_file in email_files:
            try:
                self.logger.info(f"[PROCESS] Processing: {email_file.name}")

                # Read email content
                email_data = self.parse_email_file(email_file)

                if not email_data:
                    self.logger.warning(f"[WARNING] Could not parse: {email_file.name}")
                    continue

                # Draft response using Claude Code
                draft = self.draft_response(email_data)

                if draft:
                    # Create approval request
                    approval_file = self.create_approval_request(email_data, draft)

                    # Move original to Done
                    done_file = self.done / email_file.name
                    email_file.rename(done_file)

                    self.logger.info(f"[OK] Draft created: {approval_file.name}")
                    self.logger.info(f"[MOVED] Moved to Done: {email_file.name}")
                else:
                    self.logger.warning(f"[WARNING] Could not draft response for: {email_file.name}")

            except Exception as e:
                self.logger.error(f"[ERROR] Error processing {email_file.name}: {e}")

    def parse_email_file(self, file_path: Path) -> dict:
        """Parse email file and extract metadata"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata from frontmatter
            email_data = {
                'file_name': file_path.name,
                'from': '',
                'subject': '',
                'content': '',
                'received': ''
            }

            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2]

                    # Extract fields
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            if key in email_data:
                                email_data[key] = value

                    email_data['content'] = body.strip()

            return email_data if email_data['from'] else None

        except Exception as e:
            self.logger.error(f"Error parsing email file: {e}")
            return None

    def draft_response(self, email_data: dict) -> str:
        """Draft response using Claude Code or simple template"""
        try:
            # For now, use a simple template
            # In production, you would call Claude Code API here

            sender = email_data['from']
            subject = email_data['subject']
            content = email_data['content']

            # Simple intelligent response based on content
            draft = self.generate_smart_response(sender, subject, content)

            return draft

        except Exception as e:
            self.logger.error(f"Error drafting response: {e}")
            return None

    def generate_smart_response(self, sender: str, subject: str, content: str) -> str:
        """Generate contextual response based on email content"""
        content_lower = content.lower()

        # Detect intent and generate appropriate response
        if any(word in content_lower for word in ['invoice', 'payment', 'bill']):
            return f"""Dear {self.extract_name(sender)},

Thank you for your email regarding {subject}.

I have received your inquiry about the invoice. I will review the details and get back to you within 24 hours with the requested information.

If you need immediate assistance, please feel free to call me directly.

Best regards,
{self.smtp_user.split('@')[0].title()}"""

        elif any(word in content_lower for word in ['meeting', 'schedule', 'appointment']):
            return f"""Dear {self.extract_name(sender)},

Thank you for reaching out regarding {subject}.

I would be happy to schedule a meeting with you. Please let me know your preferred date and time, and I will do my best to accommodate.

Alternatively, you can check my calendar and book a slot directly: [Calendar Link]

Looking forward to connecting with you.

Best regards,
{self.smtp_user.split('@')[0].title()}"""

        elif any(word in content_lower for word in ['question', 'inquiry', 'ask', 'help']):
            return f"""Dear {self.extract_name(sender)},

Thank you for your email regarding {subject}.

I appreciate you reaching out. I will review your inquiry and provide you with a detailed response within 24 hours.

If this is urgent, please don't hesitate to follow up.

Best regards,
{self.smtp_user.split('@')[0].title()}"""

        else:
            # Generic professional response
            return f"""Dear {self.extract_name(sender)},

Thank you for your email regarding {subject}.

I have received your message and will review it carefully. I will get back to you with a detailed response within 24-48 hours.

If you need immediate assistance, please feel free to reach out directly.

Best regards,
{self.smtp_user.split('@')[0].title()}"""

    def extract_name(self, email_address: str) -> str:
        """Extract name from email address"""
        # Try to extract name from "Name <email@domain.com>" format
        match = re.match(r'([^<]+)<', email_address)
        if match:
            return match.group(1).strip()

        # Otherwise use email username
        username = email_address.split('@')[0]
        return username.replace('.', ' ').replace('_', ' ').title()

    def create_approval_request(self, email_data: dict, draft: str) -> Path:
        """Create approval request file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_RESPONSE_{timestamp}.md"
        filepath = self.pending_approval / filename

        content = f"""---
type: approval_request
action: send_email
priority: high
created: {datetime.now().isoformat()}
status: pending
original_email: {email_data['file_name']}
---

# Email Response Approval Required

## Original Email
**From:** {email_data['from']}
**Subject:** {email_data['subject']}
**Received:** {email_data['received']}

**Content:**
{email_data['content'][:500]}...

---

## Drafted Response

**To:** {email_data['from']}
**Subject:** Re: {email_data['subject']}

**Message:**
{draft}

---

## Action Required
**HUMAN APPROVAL REQUIRED**

To approve and send this email:
1. Review the drafted response above
2. Edit if needed
3. Move this file to the **Approved** folder

To reject:
- Move this file to the **Rejected** folder

---

## Metadata
```json
{{
    "to": "{email_data['from']}",
    "subject": "Re: {email_data['subject']}",
    "original_file": "{email_data['file_name']}"
}}
```
"""

        filepath.write_text(content, encoding='utf-8')
        return filepath

    def process_approved(self):
        """Process approved emails and send them"""
        approved_files = list(self.approved.glob("EMAIL_RESPONSE_*.md"))

        if not approved_files:
            return

        self.logger.info(f"[APPROVED] Found {len(approved_files)} approved emails")

        for approved_file in approved_files:
            try:
                self.logger.info(f"[SENDING] Sending: {approved_file.name}")

                # Parse approval file
                approval_data = self.parse_approval_file(approved_file)

                if not approval_data:
                    self.logger.warning(f"[WARNING] Could not parse: {approved_file.name}")
                    continue

                # Send email
                success = self.send_email(
                    to=approval_data['to'],
                    subject=approval_data['subject'],
                    body=approval_data['body']
                )

                if success:
                    # Move to Done
                    done_file = self.done / approved_file.name
                    approved_file.rename(done_file)

                    self.logger.info(f"[OK] Email sent successfully to {approval_data['to']}")
                    self.logger.info(f"[MOVED] Moved to Done: {approved_file.name}")
                else:
                    self.logger.error(f"[ERROR] Failed to send email: {approved_file.name}")

            except Exception as e:
                self.logger.error(f"[ERROR] Error processing approved email {approved_file.name}: {e}")

    def parse_approval_file(self, file_path: Path) -> dict:
        """Parse approval file and extract email details"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata JSON
            json_match = re.search(r'```json\s*(\{[^`]+\})\s*```', content, re.DOTALL)
            if json_match:
                metadata = json.loads(json_match.group(1))
            else:
                metadata = {}

            # Extract drafted message
            message_match = re.search(r'\*\*Message:\*\*\s*(.+?)(?=\n---|\n##|$)', content, re.DOTALL)
            body = message_match.group(1).strip() if message_match else ""

            return {
                'to': metadata.get('to', ''),
                'subject': metadata.get('subject', ''),
                'body': body
            }

        except Exception as e:
            self.logger.error(f"Error parsing approval file: {e}")
            return None

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = to
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Connect to Gmail SMTP
            self.logger.info(f"[SMTP] Connecting to Gmail SMTP...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)

            # Send email
            text = msg.as_string()
            server.sendmail(self.smtp_user, to, text)
            server.quit()

            self.logger.info(f"[OK] Email sent successfully to {to}")
            return True

        except Exception as e:
            self.logger.error(f"[ERROR] Error sending email: {e}")
            return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("EMAIL WORKFLOW ORCHESTRATOR")
    print("=" * 60)
    print()
    print("This system automates:")
    print("1. Needs_Action -> Draft Response -> Pending_Approval")
    print("2. Approved -> Send Email -> Done")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Initialize orchestrator
    vault_path = "AI_Employee_Vault"
    orchestrator = EmailWorkflowOrchestrator(vault_path)

    # Run
    orchestrator.run()


if __name__ == "__main__":
    main()
