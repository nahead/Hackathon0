#!/usr/bin/env python3
"""
Email Response Sender - Processes approved email responses
Monitors /Done folder and sends approved email responses
"""

import smtplib
import os
import time
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re

class EmailResponseSender:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.archive_path = self.vault_path / "Archive"

        # Create directories
        self.archive_path.mkdir(parents=True, exist_ok=True)

        # Load email configuration
        from dotenv import load_dotenv
        load_dotenv()

        self.smtp_server = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email = os.getenv('SMTP_USER')
        self.password = os.getenv('SMTP_PASS')
        self.sender_name = os.getenv('DEFAULT_SENDER_NAME', 'AI Employee')

        if not self.email or not self.password:
            print("[ERROR] SMTP credentials not found in .env file!")
            exit(1)

    def send_email(self, to_email, subject, body, original_subject=None):
        """Send email response"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.email}>"
            msg['To'] = to_email

            # Handle reply subject
            if original_subject and not original_subject.startswith('Re:'):
                msg['Subject'] = f"Re: {original_subject}"
            else:
                msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)

            text = msg.as_string()
            server.sendmail(self.email, to_email, text)
            server.quit()

            print(f"[SUCCESS] Email sent to: {to_email}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to send email: {e}")
            return False

    def parse_approval_file(self, file_path):
        """Parse approval file and extract email details"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata
            sender_match = re.search(r'sender:\s*(.+)', content)
            subject_match = re.search(r'subject:\s*(.+)', content)

            # Extract proposed response
            response_match = re.search(r'## Proposed Response:\s*```\s*(.+?)\s*```', content, re.DOTALL)

            if sender_match and subject_match and response_match:
                # Extract email from sender (remove name if present)
                sender = sender_match.group(1).strip()
                email_match = re.search(r'<(.+?)>', sender)
                if email_match:
                    sender_email = email_match.group(1)
                else:
                    sender_email = sender.split()[-1]  # Take last word as email

                return {
                    'sender_email': sender_email,
                    'original_subject': subject_match.group(1).strip(),
                    'response_body': response_match.group(1).strip()
                }

            return None

        except Exception as e:
            print(f"[ERROR] Error parsing file {file_path}: {e}")
            return None

    def process_approved_responses(self):
        """Process all approved email responses in /Done folder"""
        # Look for email response approval files
        approval_files = list(self.done_path.glob('email_response_*.md'))

        if not approval_files:
            return

        print(f"[FOUND] Found {len(approval_files)} approved email responses")

        for file_path in approval_files:
            print(f"[PROCESS] Processing: {file_path.name}")

            # Parse approval file
            email_data = self.parse_approval_file(file_path)

            if email_data:
                # Send email response
                success = self.send_email(
                    email_data['sender_email'],
                    email_data['original_subject'],
                    email_data['response_body'],
                    email_data['original_subject']
                )

                if success:
                    # Move to archive
                    archive_file = self.archive_path / f"sent_{file_path.name}"
                    file_path.rename(archive_file)
                    print(f"[SUCCESS] Response sent and archived: {archive_file.name}")
                else:
                    print(f"[ERROR] Failed to send response for: {file_path.name}")
            else:
                print(f"[ERROR] Could not parse approval file: {file_path.name}")

    def start_monitoring(self):
        """Start monitoring /Done folder for approved responses"""
        print("[EMAIL] Starting Email Response Sender...")
        print(f"[MONITOR] Monitoring: {self.done_path}")
        print(f"[SMTP] SMTP Server: {self.smtp_server}:{self.smtp_port}")
        print(f"[FROM] From: {self.sender_name} <{self.email}>")
        print("Press Ctrl+C to stop")

        while True:
            try:
                self.process_approved_responses()

                # Wait 10 seconds before next check
                time.sleep(10)

            except KeyboardInterrupt:
                print("\n🛑 Stopping Email Response Sender...")
                break
            except Exception as e:
                print(f"[ERROR] Error in monitoring loop: {e}")
                time.sleep(30)

def main():
    vault_path = "AI_Employee_Vault"

    print("[EMAIL] Email Response Sender Starting...")
    print("=" * 50)

    sender = EmailResponseSender(vault_path)
    sender.start_monitoring()

if __name__ == "__main__":
    main()