#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Cloud API Integration
Official Meta WhatsApp Business API implementation
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
NEEDS_ACTION_FOLDER = VAULT_PATH / "Needs_Action"
APPROVED_FOLDER = VAULT_PATH / "Approved"
DONE_FOLDER = VAULT_PATH / "Done"

# WhatsApp Cloud API credentials
WHATSAPP_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_BUSINESS_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
WHATSAPP_API_VERSION = 'v18.0'

# Whitelist - Only these numbers can receive messages
ALLOWED_NUMBERS = os.getenv('WHATSAPP_ALLOWED_NUMBERS', '').split(',')
ALLOWED_NUMBERS = [num.strip() for num in ALLOWED_NUMBERS if num.strip()]

class WhatsAppCloudAPI:
    """WhatsApp Cloud API client"""

    def __init__(self):
        self.token = WHATSAPP_TOKEN
        self.phone_id = WHATSAPP_PHONE_ID
        self.api_url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{self.phone_id}/messages"

        # Ensure folders exist
        NEEDS_ACTION_FOLDER.mkdir(parents=True, exist_ok=True)
        APPROVED_FOLDER.mkdir(parents=True, exist_ok=True)
        DONE_FOLDER.mkdir(parents=True, exist_ok=True)

    def check_credentials(self):
        """Check if API credentials are configured"""
        if not self.token or self.token == 'your_access_token_here':
            print("[ERROR] WHATSAPP_ACCESS_TOKEN not configured")
            return False

        if not self.phone_id or self.phone_id == 'your_phone_number_id':
            print("[ERROR] WHATSAPP_PHONE_NUMBER_ID not configured")
            return False

        return True

    def send_message(self, to_number, message_text):
        """
        Send WhatsApp message using Cloud API

        Args:
            to_number: Recipient phone number (with country code, no +)
            message_text: Message content

        Returns:
            bool: Success status
        """
        # Whitelist check - Safety feature
        if ALLOWED_NUMBERS and to_number not in ALLOWED_NUMBERS:
            print(f"[BLOCKED] ❌ Number {to_number} not in whitelist")
            print(f"[INFO] Allowed numbers: {', '.join(ALLOWED_NUMBERS)}")
            print(f"[INFO] Add to .env: WHATSAPP_ALLOWED_NUMBERS={to_number},...")
            return False

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to_number,
            'type': 'text',
            'text': {
                'preview_url': False,
                'body': message_text
            }
        }

        try:
            print(f"[API] Sending message to {to_number}...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                print(f"[OK] ✅ Message sent successfully! ID: {message_id}")
                return True
            else:
                print(f"[ERROR] ❌ Failed to send message: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Exception while sending message: {e}")
            return False

    def handle_incoming_message(self, webhook_data):
        """
        Process incoming webhook message from WhatsApp

        Args:
            webhook_data: Webhook payload from Meta
        """
        try:
            # Extract message data
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})

            messages = value.get('messages', [])
            if not messages:
                print("[INFO] No messages in webhook")
                return

            for message in messages:
                # Extract message details
                from_number = message.get('from', '')
                message_id = message.get('id', '')
                timestamp = message.get('timestamp', '')
                message_type = message.get('type', 'text')

                # Get message content
                if message_type == 'text':
                    content = message.get('text', {}).get('body', '')
                else:
                    content = f"[{message_type.upper()} message]"

                # Get contact info
                contacts = value.get('contacts', [{}])
                contact_name = contacts[0].get('profile', {}).get('name', 'Unknown') if contacts else 'Unknown'

                print(f"\n[NEW MESSAGE] From: {contact_name} ({from_number})")
                print(f"[CONTENT] {content[:100]}...")

                # Create action file
                self.create_action_file({
                    'id': message_id,
                    'from': from_number,
                    'name': contact_name,
                    'content': content,
                    'timestamp': datetime.fromtimestamp(int(timestamp)),
                    'type': message_type
                })

        except Exception as e:
            print(f"[ERROR] Failed to process webhook: {e}")

    def create_action_file(self, message_data):
        """Create action file for incoming message"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WHATSAPP_MESSAGE_{timestamp}.md"
        filepath = NEEDS_ACTION_FOLDER / filename

        content = f"""---
type: whatsapp_message
from: {message_data['name']}
phone: {message_data['from']}
message_id: {message_data['id']}
received: {message_data['timestamp'].isoformat()}
priority: normal
requires_response: true
message_type: {message_data['type']}
---

## WhatsApp Message from {message_data['name']}

**Phone:** {message_data['from']}
**Time:** {message_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
**Type:** {message_data['type']}

### Message Content:
```
{message_data['content']}
```

### Action Required:
- Review message content
- Draft appropriate response
- Get approval before sending
- Send via WhatsApp Cloud API

### Response Guidelines:
- Be professional and courteous
- Address all questions/concerns
- Keep response concise
- Follow company communication policy

### To Respond:
1. Create response in Approved/ folder
2. Name file: WHATSAPP_RESPONSE_{timestamp}.md
3. Include phone number and message content
4. System will auto-send via API
"""

        try:
            filepath.write_text(content, encoding='utf-8')
            print(f"[OK] ✅ Created action file: {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to create action file: {e}")

    def process_approved_responses(self):
        """Process approved WhatsApp responses and send them"""
        if not APPROVED_FOLDER.exists():
            return

        # Find WhatsApp response files
        response_files = list(APPROVED_FOLDER.glob("WHATSAPP_RESPONSE_*.md"))

        if not response_files:
            return

        print(f"\n[FOUND] {len(response_files)} approved response(s)")

        for response_file in response_files:
            try:
                # Read response file
                content = response_file.read_text(encoding='utf-8')

                # Extract phone number and message
                phone = None
                message = None

                # Parse frontmatter
                lines = content.split('\n')
                in_frontmatter = False
                message_lines = []

                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue

                    if in_frontmatter:
                        if line.startswith('phone:'):
                            phone = line.split(':', 1)[1].strip()
                    else:
                        if line.strip() and not line.startswith('#'):
                            message_lines.append(line)

                message = '\n'.join(message_lines).strip()

                if not phone or not message:
                    print(f"[WARN] Missing phone or message in: {response_file.name}")
                    continue

                print(f"\n[PROCESSING] {response_file.name}")
                print(f"[TO] {phone}")
                print(f"[MESSAGE] {message[:100]}...")

                # Send message
                success = self.send_message(phone, message)

                if success:
                    # Move to Done
                    done_file = DONE_FOLDER / response_file.name
                    response_file.rename(done_file)
                    print(f"[SUCCESS] ✅ Sent and moved to Done")
                else:
                    print(f"[FAILED] ❌ Could not send message")

            except Exception as e:
                print(f"[ERROR] Error processing {response_file.name}: {e}")

def main():
    """Main entry point"""
    print("="*70)
    print("WHATSAPP CLOUD API - OFFICIAL INTEGRATION")
    print("="*70)

    # Create API client
    api = WhatsAppCloudAPI()

    # Check credentials
    print("\n[STEP 1] Checking credentials...")
    if not api.check_credentials():
        print("\n[ERROR] WhatsApp Cloud API credentials not configured")
        print("\n[SETUP] To configure:")
        print("  1. Go to: https://developers.facebook.com/")
        print("  2. Create/select your app")
        print("  3. Add WhatsApp product")
        print("  4. Get credentials and add to .env:")
        print("     WHATSAPP_ACCESS_TOKEN=your_token")
        print("     WHATSAPP_PHONE_NUMBER_ID=your_phone_id")
        print("\n[GUIDE] See: WHATSAPP_CLOUD_API_SETUP.md")
        return

    print("[OK] ✅ Credentials configured")

    # Process approved responses
    print("\n[STEP 2] Processing approved responses...")
    api.process_approved_responses()

    print("\n" + "="*70)
    print("[DONE] WhatsApp Cloud API processing complete")
    print("="*70)

if __name__ == "__main__":
    main()
