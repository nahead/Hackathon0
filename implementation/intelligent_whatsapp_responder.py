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
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Import advanced AI responder
try:
    from advanced_ai_responder import get_advanced_responder
    ADVANCED_AI_AVAILABLE = True
except ImportError:
    ADVANCED_AI_AVAILABLE = False

# Set UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Setup logging
logger = logging.getLogger('WhatsAppResponder')
logger.setLevel(logging.INFO)

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

    def generate_intelligent_response(self, message_text, sender_name, phone_number, classification):
        """
        Generate intelligent response based on message content

        Uses Advanced AI (Claude API) if available, otherwise enhanced fallback
        """
        # Try advanced AI responder first
        if ADVANCED_AI_AVAILABLE:
            try:
                logger.info(f"[AI] Using Advanced AI Responder...")
                advanced_responder = get_advanced_responder()
                response = advanced_responder.generate_advanced_response(
                    message_text,
                    sender_name,
                    phone_number,
                    classification
                )
                return response
            except Exception as e:
                logger.error(f"[AI] Advanced AI failed: {e}, using fallback")

        # Fallback to enhanced rule-based responses
        message_lower = message_text.lower()

        # Services inquiry
        if any(word in message_lower for word in ['service', 'services', 'provide', 'offer', 'do', 'what']):
            return f"Hi {sender_name}! We specialize in AI-powered business automation:\n\n✅ WhatsApp Auto-Responder (24/7)\n✅ LinkedIn Automation\n✅ Email Management\n✅ Complete AI Employee Solutions\n\nStarting at $99/month. Which service interests you most?"

        # Pricing inquiry
        if any(word in message_lower for word in ['price', 'cost', 'rate', 'fee', 'charge', 'pricing', 'plan']):
            return f"Hi {sender_name}! Our pricing:\n\n💼 Starter: $99/month\n🚀 Professional: $299/month\n🏢 Enterprise: Custom pricing\n\nAll plans include 24/7 support. Would you like details on a specific plan?"

        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'salam', 'assalam']):
            return f"Hello {sender_name}! 👋 Welcome to our AI Business Automation service. We help businesses automate WhatsApp, LinkedIn, and Email with intelligent AI. How can I assist you today?"

        # Thanks responses
        if any(word in message_lower for word in ['thanks', 'thank you', 'شکریہ', 'shukriya']):
            return f"You're very welcome, {sender_name}! 😊 Feel free to reach out anytime if you need help. We're here 24/7!"

        # How it works
        if any(word in message_lower for word in ['how', 'work', 'kaise', 'process']):
            return f"Hi {sender_name}! Here's how it works:\n\n1️⃣ We integrate with your WhatsApp/LinkedIn/Email\n2️⃣ AI learns your business context\n3️⃣ Automatically handles routine messages\n4️⃣ You approve important responses\n\nSetup takes just 15 minutes! Want to get started?"

        # Status/Update queries
        if any(word in message_lower for word in ['status', 'update', 'progress']):
            return f"Hi {sender_name}, I'll check the status and get back to you shortly. Thank you for your patience!"

        # Timing/Schedule queries
        if any(word in message_lower for word in ['when', 'timing', 'schedule', 'time', 'available', 'hours', 'kab']):
            return f"Hi {sender_name}! Our AI works 24/7 non-stop! 🤖\n\nFor human support:\n📅 Monday-Friday, 9 AM - 6 PM (PKT)\n⚡ Response time: Within 2 hours\n\nWhat would you like to know?"

        # Demo/trial
        if any(word in message_lower for word in ['demo', 'trial', 'test', 'try', 'show']):
            return f"Hi {sender_name}! We offer a FREE 7-day trial! 🎉\n\nYou'll get:\n✅ Full access to all features\n✅ Personal onboarding session\n✅ 24/7 support\n\nNo credit card required. Ready to start?"

        # Default intelligent response
        return f"Hi {sender_name}! Thank you for your message. I'm your AI assistant, and I'm here to help with:\n\n🤖 Business automation questions\n💰 Pricing and plans\n🚀 Getting started\n\nWhat would you like to know more about?"

    def send_whatsapp_message(self, to_number, message_text):
        """Send WhatsApp message via Cloud API"""
        logger.info(f"[API] Attempting to send to {to_number}")
        logger.info(f"[TOKEN] Length: {len(self.token)}, Phone ID: {self.phone_id}")

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
            logger.info(f"[API] Sending request to WhatsApp API...")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            logger.info(f"[API] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"[SENT] ✅ Message sent to {to_number} (ID: {message_id})")
                print(f"[SENT] ✅ Message sent to {to_number} (ID: {message_id})")
                return True
            else:
                logger.error(f"[ERROR] Failed to send: {response.status_code} - {response.text}")
                print(f"[ERROR] Failed to send: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Exception: {e}")
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
            logger.info(f"[SKIP] Message already processed: {message_id}")
            return

        logger.info(f"\n{'='*70}")
        logger.info(f"[NEW MESSAGE] From: {message_data['name']} ({message_data['from']})")
        logger.info(f"[CONTENT] {message_data['content'][:100]}...")

        print(f"\n{'='*70}")
        print(f"[NEW MESSAGE] From: {message_data['name']} ({message_data['from']})")
        print(f"[CONTENT] {message_data['content'][:100]}...")

        # Classify message
        classification = self.classify_message(message_data['content'])
        logger.info(f"[CLASSIFICATION] {classification.upper()}")
        print(f"[CLASSIFICATION] {classification.upper()}")

        if classification == 'serious':
            # Create approval request
            logger.info(f"[ACTION] Creating approval request...")
            print(f"[ACTION] Creating approval request...")
            self.create_approval_request(message_data)

        else:
            # Generate and send intelligent response
            logger.info(f"[ACTION] Generating intelligent response...")
            print(f"[ACTION] Generating intelligent response...")
            response = self.generate_intelligent_response(
                message_data['content'],
                message_data['name'],
                message_data['from'],
                classification
            )

            logger.info(f"[RESPONSE] {response[:100]}...")
            print(f"[RESPONSE] {response[:100]}...")

            # Send response
            success = self.send_whatsapp_message(
                message_data['from'],
                response
            )

            if success:
                logger.info(f"[SUCCESS] ✅ Auto-responded to {message_data['name']}")
                print(f"[SUCCESS] ✅ Auto-responded to {message_data['name']}")
            else:
                logger.error(f"[FAILED] ❌ Could not send response")
                print(f"[FAILED] ❌ Could not send response")

        # Mark as processed
        self.processed_messages.add(message_id)
        self._save_state()
        logger.info(f"{'='*70}\n")
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
