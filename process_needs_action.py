#!/usr/bin/env python3
"""
Process Needs_Action Files
Reads action files from Needs_Action/ and creates approval files in Pending_Approval/
"""

import os
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_email_data(content):
    """Extract email data from action file"""
    data = {}

    # Extract frontmatter
    frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()

    # Extract email content
    content_match = re.search(r'\*\*Content:\*\*\n```\n(.*?)\n```', content, re.DOTALL)
    if content_match:
        data['email_content'] = content_match.group(1).strip()
    else:
        data['email_content'] = "No content available"

    return data

def generate_response(email_data):
    """Generate appropriate response based on email content"""
    subject = email_data.get('subject', '').lower()
    sender = email_data.get('sender', 'Unknown')
    content = email_data.get('email_content', '').lower()

    # Simple response generation based on keywords
    if 'urgent' in subject or 'urgent' in content:
        if 'payment' in subject or 'payment' in content:
            response = f"""Thank you for your email regarding the urgent payment matter.

I have received your message and understand the urgency. I will review the payment details and get back to you within 2 hours with a resolution.

If you need immediate assistance, please feel free to call our support line.

Best regards,
AI Employee System"""
        else:
            response = f"""Thank you for your urgent message.

I have received your email and will prioritize this matter. I will respond with the necessary information within 2 hours.

Best regards,
AI Employee System"""

    elif 'meeting' in subject or 'meeting' in content:
        response = f"""Thank you for your email.

I have received your meeting request. I will check the calendar and get back to you with available time slots within 24 hours.

Best regards,
AI Employee System"""

    elif 'question' in subject or 'inquiry' in subject or '?' in content:
        response = f"""Thank you for your inquiry.

I have received your question and will provide you with a detailed response within 24 hours.

Best regards,
AI Employee System"""

    else:
        # Default response
        response = f"""Thank you for your email.

I have received your message and will review it carefully. I will respond with the appropriate information within 24 hours.

Best regards,
AI Employee System"""

    return response

def process_action_file(filepath):
    """Process a single action file"""
    print(f"\n[PROCESS] Processing: {filepath.name}")

    try:
        # Read action file
        content = filepath.read_text(encoding='utf-8')

        # Extract email data
        email_data = extract_email_data(content)

        if not email_data:
            print(f"[ERROR] Could not extract email data from {filepath.name}")
            return False

        print(f"[INFO] From: {email_data.get('sender', 'Unknown')}")
        print(f"[INFO] Subject: {email_data.get('subject', 'No Subject')}")

        # Generate response
        response = generate_response(email_data)

        # Create approval file
        pending_approval_path = Path("AI_Employee_Vault/Pending_Approval")
        pending_approval_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_filename = f"EMAIL_RESPONSE_{timestamp}.md"
        approval_filepath = pending_approval_path / approval_filename

        approval_content = f"""---
type: email_response_approval
sender: {email_data.get('sender', 'Unknown')}
subject: {email_data.get('subject', 'No Subject')}
email_id: {email_data.get('email_id', 'unknown')}
created: {datetime.now().isoformat()}
status: pending_approval
---

## Original Email

**From:** {email_data.get('sender', 'Unknown')}
**Subject:** {email_data.get('subject', 'No Subject')}
**Received:** {email_data.get('received', 'Unknown')}

**Content:**
```
{email_data.get('email_content', 'No content available')}
```

## Proposed Response

```
{response}
```

## Instructions

1. **To Approve:** Move this file to `AI_Employee_Vault/Approved/`
2. **To Edit:** Modify the response above and keep in Pending_Approval/
3. **To Reject:** Move this file to `AI_Employee_Vault/Rejected/` or delete it

## Workflow
Needs_Action -> Processing -> **Pending_Approval** -> Approved -> Done
"""

        approval_filepath.write_text(approval_content, encoding='utf-8')
        print(f"[OK] Created approval file: {approval_filename}")

        # Move processed action file to Processing folder
        processing_path = Path("AI_Employee_Vault/Processing")
        processing_path.mkdir(parents=True, exist_ok=True)

        processed_filepath = processing_path / filepath.name
        filepath.rename(processed_filepath)
        print(f"[OK] Moved to Processing: {filepath.name}")

        return True

    except Exception as e:
        print(f"[ERROR] Error processing {filepath.name}: {e}")
        return False

def process_needs_action():
    """Process all files in Needs_Action folder"""
    print("[TEST] Processing Needs_Action Files...")

    needs_action_path = Path("AI_Employee_Vault/Needs_Action")

    if not needs_action_path.exists():
        print("[INFO] No Needs_Action folder found")
        return 0

    # Find all action files
    action_files = list(needs_action_path.glob("EMAIL_DETECTED_*.md"))

    if not action_files:
        print("[INFO] No action files found in Needs_Action/")
        return 0

    print(f"[INBOX] Found {len(action_files)} action file(s)")

    processed_count = 0
    for action_file in action_files:
        if process_action_file(action_file):
            processed_count += 1

    return processed_count

if __name__ == "__main__":
    print("=" * 60)
    print("PROCESS NEEDS_ACTION FILES")
    print("=" * 60)

    processed = process_needs_action()

    print("\n" + "=" * 60)
    if processed > 0:
        print(f"[OK] PROCESSED {processed} FILE(S)")
        print("=" * 60)
        print("\n[INFO] Next Steps:")
        print("  1. Check AI_Employee_Vault/Pending_Approval/")
        print("  2. Review the proposed responses")
        print("  3. Move approved files to Approved/")
        print("  4. Run test_email_sender.py to send approved responses")
    else:
        print("[INFO] NO FILES TO PROCESS")
        print("=" * 60)
        print("\n[INFO] Run test_email_detection.py first to detect emails")
