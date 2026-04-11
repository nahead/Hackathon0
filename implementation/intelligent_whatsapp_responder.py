#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intelligent WhatsApp Auto-Responder
Monitors messages every 15 seconds, generates intelligent responses,
auto-sends routine replies, creates approval for serious messages
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
DONE = VAULT_PATH / "Done"

# WhatsApp API
WHATSAPP_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_API_VERSION = 'v18.0'
CHECK_INTERVAL = 15  # seconds

# Ensure folders exist
for folder in [NEEDS_ACTION, PENDING_APPROVAL, APPROVED, DONE]:
    folder.mkdir(parents=True, exist_ok=True)

# Keywords for serious messages (require approval)
SERIOUS_KEYWORDS = [
    'urgent', 'emergency', 'complaint', 'refund', 'cancel', 'legal',
    'lawsuit', 'problem', 'issue', 'angry', 'disappointed', 'unhappy',
    'payment issue', 'not working', 'broken', 'failed', 'error',
    'contract', 'agreement', 'negotiate', 'discount', 'price change'
]

# Keywords for routine messages (auto-respond)
ROUTINE_KEYWORDS = [
    'hello', 'hi', 'thanks', 'thank you', 'ok', 'okay', 'yes', 'no',
    'status', 'update', 'when', 'how', 'what', 'where', 'info',
    'information', 'details', 'price', 'cost', 'timing', 'schedule'
]


class IntelligentWhatsAppResponder:
    """Intelligent auto-responder for WhatsApp messages"""

    def __init__(self):
        self.token = WHATSAPP_TOKEN
        self.phone_id = WHATSAPP_PHONE_ID
        self.api_url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{self.phone_id}/messages"
        self.processed_messages = set()

        # Load processed messages from file
        self.state_file = Path(__file__).parent / ".whatsapp_processed.json"
        self._load_state()

    def _load_state(self):
        """Load processed message IDs from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.processed_messages = set(data.get('processed', []))
            except:
                pass

    def _save_state(self):
        """Save processed message IDs to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'processed': list(self.processed_messages)}, f)
        except:
            pass

    def classify_message(self, message_text):
        """
        Classify message as routine or serious

        Returns:
            'routine' - Auto-respond
            'serious' - Require approval
        """
        message_lower = message_text.lower()

        # Check for serious keywords
        for keyword in SERIOUS_KEYWORDS:
            if keyword in message_lower:
                return 'serious'

        # Check message length (long messages might be serious)
        if len(message_text) > 500:
            return 'serious'

        # Check for multiple question marks (indicates urgency)
        if message_text.count('?') > 2:
            return 'serious'

        # Check for all caps (indicates anger/urgency)
        if message_text.isupper() and len(message_text) > 20:
            return 'serious'

        # Default to routine
        return 'routine'

    def generate_intelligent_response(self, message_text, sender_name, classification):
        """
        Generate intelligent response based on message content

        Uses simple rule-based generation (in production, use Claude API)
        """
        message_lower = message_text.lower()

        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'salam']):
            return f"Hello {sender_name}! Thank you for contacting us. How can I help you today?"

        # Thanks responses
        if any(word in message_lower for word in ['thanks', 'thank you', 'شکریہ']):
            return f"You're welcome, {sender_name}! Feel free to reach out if you need anything else."

        # Status/Update queries
        if any(word in message_lower for word in ['status', 'update', 'progress']):
            return f"Hi {sender_name}, I'll check the status and get back to you shortly. Thank you for your patience!"

        # Pricing queries
        if any(word in message_lower for word in ['price', 'cost', 'rate', 'fee', 'charge']):
            return f"Hi {sender_name}, thank you for your interest! Our pricing depends on your specific requirements. Could you please share more details about what you're looking for?"

        # Information requests
        if any(word in message_lower for word in ['info', 'information', 'details', 'tell me']):
            return f"Hi {sender_name}, I'd be happy to provide more information. What specific details would you like to know?"

        # Timing/Schedule queries
        if any(word in message_lower for word in ['when', 'timing', 'schedule', 'time']):
            return f"Hi {sender_name}, our business hours are Monday-Friday, 9 AM - 6 PM. We'll respond to your inquiry as soon as possible!"

        # Default intelligent response
        return f"Hi {sender_name}, thank you for your message. I've received your inquiry and will get back to you shortly with a detailed response. Is there anything specific I can help you with right away?"

    def send_whatsapp_message(self, to_number, message_text):
        """Send WhatsApp message via Cloud API"""
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
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                print(f"[SENT] ✅ Message sent to {to_number} (ID: {message_id})")
                return True
            else:
                print(f"[ERROR] Failed to send: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            return False

    def create_approval_request(self, message_data):
        """Create approval request for serious messages"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WHATSAPP_APPROVAL_{message_data['from']}_{timestamp}.md"
        filepath = PENDING_APPROVAL / filename

        content = f"""---
type: whatsapp_approval
from: {message_data['name']}
phone: {message_data['from']}
message_id: {message_data['id']}
received: {message_data['timestamp'].isoformat()}
priority: high
classification: serious
---

## ⚠️ Serious WhatsApp Message - Approval Required

**From:** {message_data['name']}
**Phone:** {message_data['from']}
**Time:** {message_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
**Classification:** SERIOUS - Requires human review

### Original Message:
```
{message_data['content']}
```

### Why This Needs Approval:
This message was classified as serious because it contains:
- Urgent/complaint keywords
- Complex inquiry requiring careful response
- Potential business-critical content

### Action Required:
1. Review the message carefully
2. Draft appropriate response
3. Create response file in /Approved folder:
   - Filename: WHATSAPP_RESPONSE_{timestamp}.md
   - Include phone number in frontmatter
   - System will auto-send once approved

### Response Guidelines:
- Be professional and empathetic
- Address all concerns raised
- Provide clear next steps
- Maintain company tone and policies

---
**Auto-generated by Intelligent WhatsApp Responder**
"""

        try:
            filepath.write_text(content, encoding='utf-8')
            print(f"[APPROVAL] ⚠️ Created approval request: {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create approval: {e}")
            return False

    def process_message(self, message_data):
        """Process incoming message - classify and respond"""
        message_id = message_data['id']

        # Skip if already processed
        if message_id in self.processed_messages:
            return

        print(f"\n{'='*70}")
        print(f"[NEW MESSAGE] From: {message_data['name']} ({message_data['from']})")
        print(f"[CONTENT] {message_data['content'][:100]}...")

        # Classify message
        classification = self.classify_message(message_data['content'])
        print(f"[CLASSIFICATION] {classification.upper()}")

        if classification == 'serious':
            # Create approval request
            print(f"[ACTION] Creating approval request...")
            self.create_approval_request(message_data)

        else:
            # Generate and send intelligent response
            print(f"[ACTION] Generating intelligent response...")
            response = self.generate_intelligent_response(
                message_data['content'],
                message_data['name'],
                classification
            )

            print(f"[RESPONSE] {response[:100]}...")

            # Send response
            success = self.send_whatsapp_message(
                message_data['from'],
                response
            )

            if success:
                print(f"[SUCCESS] ✅ Auto-responded to {message_data['name']}")
            else:
                print(f"[FAILED] ❌ Could not send response")

        # Mark as processed
        self.processed_messages.add(message_id)
        self._save_state()
        print(f"{'='*70}\n")

    def check_messages(self):
        """
        Check for new WhatsApp messages

        Note: This is a placeholder. In production, you would:
        1. Use WhatsApp webhook to receive messages in real-time
        2. Or poll WhatsApp Business API for new messages

        For now, this monitors the Needs_Action folder for test messages
        """
        # Check Needs_Action folder for incoming messages
        message_files = list(NEEDS_ACTION.glob("WHATSAPP_MESSAGE_*.md"))

        for message_file in message_files:
            try:
                content = message_file.read_text(encoding='utf-8')

                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        metadata = {}
                        for line in parts[1].split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()

                        message_data = {
                            'id': metadata.get('message_id', message_file.stem),
                            'from': metadata.get('phone', 'unknown'),
                            'name': metadata.get('from', 'Unknown'),
                            'content': parts[2].strip(),
                            'timestamp': datetime.now()
                        }

                        # Process message
                        self.process_message(message_data)

                        # Move to Done
                        done_file = DONE / message_file.name
                        message_file.rename(done_file)

            except Exception as e:
                print(f"[ERROR] Failed to process {message_file.name}: {e}")

    def run_continuous(self):
        """Run continuous monitoring every 15 seconds"""
        print("="*70)
        print("INTELLIGENT WHATSAPP AUTO-RESPONDER")
        print("="*70)
        print(f"[CONFIG] Check interval: {CHECK_INTERVAL} seconds")
        print(f"[CONFIG] Auto-respond: Routine messages")
        print(f"[CONFIG] Require approval: Serious messages")
        print(f"[STATUS] Monitoring started...\n")

        while True:
            try:
                self.check_messages()
                time.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                print("\n[STOP] Monitoring stopped by user")
                break

            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(CHECK_INTERVAL)


def main():
    """Main entry point"""
    responder = IntelligentWhatsAppResponder()

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        responder.run_continuous()
    else:
        # Single check
        responder.check_messages()


if __name__ == "__main__":
    main()
