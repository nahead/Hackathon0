#!/usr/bin/env python3
"""
Test Email Detection - Gmail IMAP
Tests if Gmail monitoring is working and can detect new emails
"""

import os
import imaplib
import email
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_gmail_connection():
    """Test Gmail IMAP connection"""
    print("[TEST] Testing Gmail Connection...")

    # Get credentials from environment
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("[ERROR] ERROR: SMTP_USER and SMTP_PASS environment variables not set")
        print("\nSet them with:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASS='your-app-password'")
        return False

    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(smtp_user, smtp_pass)
        print(f"[OK] Connected to Gmail as: {smtp_user}")

        # Select inbox
        mail.select('inbox')
        print("[OK] Inbox selected")

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        print(f"\n[EMAIL] Found {len(email_ids)} unread emails")

        if len(email_ids) > 0:
            print("\n[INBOX] Recent unread emails:")
            # Show first 5 unread emails
            for email_id in email_ids[:5]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                subject = msg.get('Subject', 'No Subject')
                sender = msg.get('From', 'Unknown')
                date = msg.get('Date', 'Unknown')

                print(f"\n  From: {sender}")
                print(f"  Subject: {subject}")
                print(f"  Date: {date}")

        mail.close()
        mail.logout()

        print("\n[OK] Email detection test PASSED")
        return True

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

def test_create_action_file():
    """Test creating action file in Needs_Action (proper workflow)"""
    print("\n[TEST] Testing Action File Creation in Needs_Action...")

    vault_path = Path("AI_Employee_Vault/Needs_Action")
    vault_path.mkdir(parents=True, exist_ok=True)

    # Create action file (not approval file)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"EMAIL_DETECTED_{timestamp}.md"
    filepath = vault_path / filename

    content = f"""---
type: email_action
sender: detected-email@example.com
subject: New Email Detected
received: {datetime.now().isoformat()}
status: needs_action
priority: normal
---

## Email Details
A new email has been detected and needs processing.

**From:** detected-email@example.com
**Subject:** New Email Detected
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Next Steps
1. System will analyze this email
2. Generate appropriate response
3. Create approval file in Pending_Approval/
4. Wait for human approval
5. Send response via SMTP

## Workflow
Needs_Action → Processing → Pending_Approval → Approved → Done
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"[OK] Created action file: {filename}")
    print(f"   Location: {filepath}")
    print(f"\n[INFO] This file should be processed by the system")
    print(f"   System will create approval file in Pending_Approval/")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL DETECTION TEST")
    print("=" * 60)

    # Test Gmail connection
    if test_gmail_connection():
        # Test action file creation (proper workflow)
        test_create_action_file()

        print("\n" + "=" * 60)
        print("[OK] ALL TESTS PASSED")
        print("=" * 60)
        print("\n[INFO] Workflow:")
        print("  1. Email detected -> Needs_Action/")
        print("  2. System processes -> generates response")
        print("  3. Creates approval file -> Pending_Approval/")
        print("  4. Human approves -> Approved/")
        print("  5. System sends email -> Done/")
    else:
        print("\n" + "=" * 60)
        print("[ERROR] TESTS FAILED")
        print("=" * 60)
