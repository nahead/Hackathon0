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

def get_email_content(email_message):
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

def test_gmail_connection():
    """Test Gmail IMAP connection and create action files for detected emails"""
    print("[TEST] Testing Gmail Connection...")

    # Get credentials from environment
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("[ERROR] ERROR: SMTP_USER and SMTP_PASS environment variables not set")
        print("\nSet them with:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASS='your-app-password'")
        return False, []

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

        detected_emails = []

        if len(email_ids) > 0:
            print("\n[INBOX] Recent unread emails:")
            # Process first 5 unread emails
            for email_id in email_ids[:5]:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                subject = msg.get('Subject', 'No Subject')
                sender = msg.get('From', 'Unknown')
                date = msg.get('Date', 'Unknown')
                content = get_email_content(msg)

                print(f"\n  From: {sender}")
                print(f"  Subject: {subject}")
                print(f"  Date: {date}")

                # Store email data for action file creation
                detected_emails.append({
                    'sender': sender,
                    'subject': subject,
                    'date': date,
                    'content': content,
                    'email_id': email_id.decode() if isinstance(email_id, bytes) else email_id
                })

        mail.close()
        mail.logout()

        print("\n[OK] Email detection test PASSED")
        return True, detected_emails

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False, []

def create_action_files(detected_emails):
    """Create action files for detected emails in Needs_Action folder"""
    if not detected_emails:
        print("\n[INFO] No emails to process")
        return []

    print(f"\n[TEST] Creating Action Files for {len(detected_emails)} email(s)...")

    vault_path = Path("AI_Employee_Vault/Needs_Action")
    vault_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    for email_data in detected_emails:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_DETECTED_{timestamp}.md"
        filepath = vault_path / filename

        content = f"""---
type: email_action
sender: {email_data['sender']}
subject: {email_data['subject']}
received: {datetime.now().isoformat()}
status: needs_action
priority: normal
email_id: {email_data['email_id']}
---

## Email Details
A new email has been detected and needs processing.

**From:** {email_data['sender']}
**Subject:** {email_data['subject']}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Content:**
```
{email_data['content']}
```

## Next Steps
1. System will analyze this email
2. Generate appropriate response
3. Create approval file in Pending_Approval/
4. Wait for human approval
5. Send response via SMTP

## Workflow
Needs_Action -> Processing -> Pending_Approval -> Approved -> Done
"""

        filepath.write_text(content, encoding='utf-8')
        created_files.append(filename)
        print(f"[OK] Created: {filename}")

    print(f"\n[INFO] Created {len(created_files)} action file(s) in Needs_Action/")
    return created_files

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL DETECTION TEST")
    print("=" * 60)

    # Test Gmail connection and detect emails
    success, detected_emails = test_gmail_connection()

    if success:
        # Create action files for detected emails
        created_files = create_action_files(detected_emails)

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
