#!/usr/bin/env python3
"""
Simple Gmail Watcher using App Password
No OAuth complexity - direct IMAP access
"""

import imaplib
import email
import time
import os
from pathlib import Path
from datetime import datetime
import json

class SimpleGmailWatcher:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"

        # Create directories if they don't exist
        for path in [self.inbox_path, self.needs_action_path, self.done_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Gmail credentials from environment
        self.email = os.getenv('SMTP_USER', 'naheadj@gmail.com')
        self.password = os.getenv('SMTP_PASS')

        if not self.password:
            print("ERROR: Gmail App Password not found!")
            print("Please set SMTP_PASS environment variable")
            print("Or create .env file with:")
            print("SMTP_USER=naheadj@gmail.com")
            print("SMTP_PASS=your-16-char-app-password")
            exit(1)

    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email, self.password)
            print(f"SUCCESS: Connected to Gmail: {self.email}")
            return mail
        except Exception as e:
            print(f"ERROR: Gmail connection failed: {e}")
            return None

    def check_new_emails(self, mail):
        """Check for new emails"""
        try:
            # Select inbox
            mail.select('inbox')

            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')

            if status == 'OK':
                email_ids = messages[0].split()
                print(f"FOUND: Found {len(email_ids)} new emails")

                for email_id in email_ids:
                    self.process_email(mail, email_id)

        except Exception as e:
            print(f"ERROR: Error checking emails: {e}")

    def process_email(self, mail, email_id):
        """Process individual email"""
        try:
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if status == 'OK':
                # Parse email
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Extract email details
                subject = email_message['Subject']
                sender = email_message['From']
                date = email_message['Date']

                # Get email content
                content = self.get_email_content(email_message)

                print(f"[EMAIL] Processing: {subject} from {sender}")

                # Create approval file
                self.create_approval_file(subject, sender, content, email_id)

        except Exception as e:
            print(f"ERROR: Error processing email {email_id}: {e}")

    def get_email_content(self, email_message):
        """Extract email content"""
        content = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    content = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            content = email_message.get_payload(decode=True).decode('utf-8')

        return content

    def create_approval_file(self, subject, sender, content, email_id):
        """Create approval file for human review"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_TEST_{timestamp}.md"
        filepath = self.needs_action_path / filename

        # Analyze email type and suggest response
        response_type = self.analyze_email_type(subject, content)
        suggested_response = self.generate_response(response_type, subject, content)

        approval_content = f"""---
type: email_response_approval
email_id: {email_id.decode()}
sender: {sender}
subject: {subject}
timestamp: {datetime.now().isoformat()}
response_type: {response_type}
---

# Email Response Approval Required

## Original Email:
**From:** {sender}
**Subject:** {subject}
**Content:**
```
{content[:500]}...
```

## Suggested Response Type: {response_type}

## Proposed Response:
```
{suggested_response}
```

## Actions Required:
- [ ] Review email content and proposed response
- [ ] Edit response if needed
- [ ] Move this file to /Done folder to approve sending
- [ ] Or move to /Archive to skip response

## Instructions:
1. Review the proposed response above
2. Edit if necessary
3. Move file to AI_Employee_Vault/Done/ to approve
4. System will automatically send the response
"""

        # Write approval file
        filepath.write_text(approval_content, encoding='utf-8')
        print(f"SUCCESS: Approval file created: {filename}")

    def analyze_email_type(self, subject, content):
        """Simple email type analysis"""
        subject_lower = subject.lower()
        content_lower = content.lower()

        if any(word in subject_lower for word in ['invoice', 'payment', 'bill']):
            return "invoice_request"
        elif any(word in subject_lower for word in ['quote', 'proposal', 'consultation']):
            return "business_inquiry"
        elif any(word in subject_lower for word in ['support', 'help', 'issue', 'problem']):
            return "support_request"
        elif any(word in content_lower for word in ['meeting', 'schedule', 'appointment']):
            return "meeting_request"
        else:
            return "general_inquiry"

    def generate_response(self, response_type, subject, content):
        """Generate appropriate response based on email type"""
        responses = {
            "invoice_request": """Thank you for your email regarding the invoice request.

I have received your request and will process the invoice within 24 hours. You will receive the invoice via email with detailed payment instructions.

If you have any questions, please don't hesitate to contact me.

Best regards,
AI Employee System""",

            "business_inquiry": """Thank you for your interest in our services.

I have received your inquiry and will review the details carefully. I will provide you with a detailed proposal within 48 hours.

In the meantime, if you have any additional questions or requirements, please feel free to share them.

Best regards,
AI Employee System""",

            "support_request": """Thank you for contacting our support team.

I have received your support request and understand the urgency of your issue. I will investigate this matter immediately and provide you with a solution within 4 hours.

I will keep you updated on the progress and ensure your issue is resolved promptly.

Best regards,
AI Employee Support""",

            "meeting_request": """Thank you for your meeting request.

I have received your request to schedule a meeting. I will check the availability and send you a calendar invitation with available time slots within 24 hours.

Please let me know if you have any preferred dates or times.

Best regards,
AI Employee System""",

            "general_inquiry": """Thank you for your email.

I have received your message and will review it carefully. I will respond with the appropriate information within 24 hours.

If this is urgent, please don't hesitate to call or send a follow-up email.

Best regards,
AI Employee System"""
        }

        return responses.get(response_type, responses["general_inquiry"])

    def start_monitoring(self):
        """Start continuous email monitoring"""
        print("STARTING: Starting Gmail monitoring...")
        print(f"VAULT: Vault path: {self.vault_path}")
        print(f"MONITORING: {self.email}")
        print("Press Ctrl+C to stop")

        while True:
            try:
                # Connect to Gmail
                mail = self.connect_to_gmail()
                if mail:
                    # Check for new emails
                    self.check_new_emails(mail)
                    # Close connection
                    mail.close()
                    mail.logout()

                # Wait 30 seconds before next check
                print("[WAIT] Waiting 30 seconds...")
                time.sleep(30)

            except KeyboardInterrupt:
                print("\n[STOP] Stopping Gmail watcher...")
                break
            except Exception as e:
                print(f"ERROR: Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    vault_path = "AI_Employee_Vault"

    print("Simple Gmail Watcher Starting...")
    print("=" * 50)

    watcher = SimpleGmailWatcher(vault_path)
    watcher.start_monitoring()

if __name__ == "__main__":
    main()