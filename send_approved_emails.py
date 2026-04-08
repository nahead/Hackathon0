#!/usr/bin/env python3
"""
Send Approved Emails
Reads approved email responses from Approved/ folder and sends them via SMTP
"""

import os
import re
import smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_email_details(content):
    """Extract email details from approval file"""
    details = {}

    # Extract from frontmatter
    frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                details[key.strip()] = value.strip()

    # Extract proposed response
    response_match = re.search(r'## Proposed Response[:\s]*```\s*(.+?)\s*```', content, re.DOTALL)
    if response_match:
        details['response'] = response_match.group(1).strip()
    else:
        details['response'] = None

    return details

def send_email_smtp(to_email, subject, body):
    """Send email via SMTP"""
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("[ERROR] SMTP credentials not configured")
        return False

    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Try SSL first (port 465)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[OK] Email sent via SMTP (SSL port 465)")
        return True
    except Exception as e:
        print(f"[WARN] SSL port 465 failed: {e}")

    # Try TLS (port 587) as fallback
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"[OK] Email sent via SMTP (TLS port 587)")
        return True
    except Exception as e:
        print(f"[ERROR] TLS port 587 also failed: {e}")
        return False

def process_approved_emails():
    """Process and send approved emails"""
    print("[TEST] Processing Approved Emails...")

    approved_path = Path("AI_Employee_Vault/Approved")
    done_path = Path("AI_Employee_Vault/Done")

    if not approved_path.exists():
        print("[INFO] No Approved folder found")
        return 0

    # Find approved email response files
    approved_files = list(approved_path.glob("EMAIL_RESPONSE_*.md"))

    if not approved_files:
        print("[INFO] No approved emails found")
        print("\nTo approve an email:")
        print("1. Run: python process_needs_action.py")
        print("2. Check AI_Employee_Vault/Pending_Approval/")
        print("3. Move approved file to AI_Employee_Vault/Approved/")
        return 0

    print(f"[INBOX] Found {len(approved_files)} approved email(s)")

    sent_count = 0
    for approved_file in approved_files:
        print(f"\n[PROCESS] Processing: {approved_file.name}")

        try:
            # Read approval file
            content = approved_file.read_text(encoding='utf-8')

            # Extract email details
            details = extract_email_details(content)

            if not details.get('sender') or not details.get('subject') or not details.get('response'):
                print(f"[ERROR] Could not parse email details from {approved_file.name}")
                continue

            # Extract email address from sender
            sender = details['sender']
            email_match = re.search(r'<(.+?)>', sender)
            if email_match:
                to_email = email_match.group(1)
            else:
                to_email = sender

            # Create reply subject
            original_subject = details['subject']
            if original_subject.startswith('Re:'):
                reply_subject = original_subject
            else:
                reply_subject = f"Re: {original_subject}"

            response_body = details['response']

            print(f"[SEND] Sending to: {to_email}")
            print(f"[SEND] Subject: {reply_subject}")

            # Send email
            success = send_email_smtp(to_email, reply_subject, response_body)

            if success:
                # Move to Done folder
                done_path.mkdir(parents=True, exist_ok=True)
                done_file = done_path / approved_file.name
                approved_file.rename(done_file)
                print(f"[OK] Moved to Done: {approved_file.name}")
                sent_count += 1
            else:
                print(f"[ERROR] Failed to send email from {approved_file.name}")

        except Exception as e:
            print(f"[ERROR] Error processing {approved_file.name}: {e}")

    return sent_count

if __name__ == "__main__":
    print("=" * 60)
    print("SEND APPROVED EMAILS")
    print("=" * 60)

    sent = process_approved_emails()

    print("\n" + "=" * 60)
    if sent > 0:
        print(f"[OK] SENT {sent} EMAIL(S)")
        print("=" * 60)
        print("\n[INFO] Completed emails moved to Done/")
    else:
        print("[INFO] NO EMAILS TO SEND")
        print("=" * 60)
        print("\n[INFO] Workflow:")
        print("  1. Run: python test_email_detection.py")
        print("  2. Run: python process_needs_action.py")
        print("  3. Move file from Pending_Approval/ to Approved/")
        print("  4. Run: python send_approved_emails.py")
