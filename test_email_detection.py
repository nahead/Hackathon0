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
    print("🔍 Testing Gmail Connection...")

    # Get credentials from environment
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("❌ ERROR: SMTP_USER and SMTP_PASS environment variables not set")
        print("\nSet them with:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASS='your-app-password'")
        return False

    try:
        # Connect to Gmail
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(smtp_user, smtp_pass)
        print(f"✅ Connected to Gmail as: {smtp_user}")

        # Select inbox
        mail.select('inbox')
        print("✅ Inbox selected")

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        print(f"\n📧 Found {len(email_ids)} unread emails")

        if len(email_ids) > 0:
            print("\n📬 Recent unread emails:")
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

        print("\n✅ Email detection test PASSED")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_create_approval_file():
    """Test creating approval file in vault"""
    print("\n🔍 Testing Approval File Creation...")

    vault_path = Path("AI_Employee_Vault/Pending_Approval")
    vault_path.mkdir(parents=True, exist_ok=True)

    # Create test approval file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"EMAIL_TEST_{timestamp}.md"
    filepath = vault_path / filename

    content = f"""---
type: email_approval
sender: test@example.com
subject: Test Email
received: {datetime.now().isoformat()}
status: pending
---

## Email Body
This is a test email for approval workflow.

## Proposed Response
Thank you for your email. This is an automated test response.

## To Approve
Move this file to AI_Employee_Vault/Approved/ folder.

## To Reject
Move this file to AI_Employee_Vault/Rejected/ folder or delete it.
"""

    filepath.write_text(content, encoding='utf-8')
    print(f"✅ Created approval file: {filename}")
    print(f"   Location: {filepath}")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL DETECTION TEST")
    print("=" * 60)

    # Test Gmail connection
    if test_gmail_connection():
        # Test approval file creation
        test_create_approval_file()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ TESTS FAILED")
        print("=" * 60)
