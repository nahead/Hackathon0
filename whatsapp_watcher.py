#!/usr/bin/env python3
"""
WhatsApp Watcher - Silver Tier Requirement
Monitors WhatsApp for new messages and creates action files
"""

import os
import time
from pathlib import Path
from datetime import datetime

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
NEEDS_ACTION_FOLDER = VAULT_PATH / "Needs_Action"

class WhatsAppWatcher:
    """Monitor WhatsApp for new messages"""

    def __init__(self, check_interval=60):
        self.vault_path = VAULT_PATH
        self.needs_action = NEEDS_ACTION_FOLDER
        self.needs_action.mkdir(exist_ok=True)
        self.check_interval = check_interval
        self.processed_messages = set()

    def check_whatsapp_messages(self):
        """
        Check for new WhatsApp messages

        Note: This is a placeholder implementation.
        In production, this would:
        1. Use WhatsApp Web automation (Playwright/Selenium)
        2. Or use WhatsApp Business API
        3. Or monitor WhatsApp database files (if accessible)

        For Silver Tier demo, this creates sample action files
        """
        print(f"[WHATSAPP] Checking for new messages...")

        # In production, this would check actual WhatsApp messages
        # For now, return empty list (no new messages)
        return []

    def create_action_file(self, message):
        """Create action file for WhatsApp message"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"WHATSAPP_MESSAGE_{timestamp}.md"
        filepath = self.needs_action / filename

        # Extract message details
        sender = message.get('sender', 'Unknown')
        content = message.get('content', '')
        phone = message.get('phone', '')
        priority = message.get('priority', 'normal')

        # Create frontmatter
        frontmatter = f"""---
type: whatsapp_message
from: {sender}
phone: {phone}
received: {datetime.now().isoformat()}
priority: {priority}
requires_response: true
---

## WhatsApp Message from {sender}

**Phone:** {phone}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### Message Content:
{content}

### Action Required:
- Review message content
- Draft appropriate response
- Get approval before sending
- Send via WhatsApp

### Response Guidelines:
- Be professional and courteous
- Address all questions/concerns
- Keep response concise
- Follow company communication policy
"""

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)

        print(f"[OK] Created action file: {filename}")
        return filepath

    def run_once(self):
        """Run one check cycle"""
        try:
            messages = self.check_whatsapp_messages()

            if messages:
                print(f"[WHATSAPP] Found {len(messages)} new message(s)")
                for message in messages:
                    msg_id = message.get('id', '')
                    if msg_id not in self.processed_messages:
                        self.create_action_file(message)
                        self.processed_messages.add(msg_id)
            else:
                print(f"[WHATSAPP] No new messages")

        except Exception as e:
            print(f"[ERROR] WhatsApp check failed: {e}")

    def run_continuous(self):
        """Run continuous monitoring"""
        print(f"[WHATSAPP] Starting continuous monitoring (interval: {self.check_interval}s)")

        while True:
            try:
                self.run_once()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                print("\n[STOP] WhatsApp watcher stopped by user")
                break
            except Exception as e:
                print(f"[ERROR] Watcher error: {e}")
                time.sleep(self.check_interval)

def main():
    """Main entry point"""
    print("="*70)
    print("WHATSAPP WATCHER - SILVER TIER")
    print("="*70)

    # Get check interval from environment
    check_interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', '60'))

    print(f"\n[CONFIG] Check interval: {check_interval} seconds")
    print(f"[CONFIG] Vault path: {VAULT_PATH}")
    print(f"[CONFIG] Needs Action folder: {NEEDS_ACTION_FOLDER}")

    # Create watcher instance
    watcher = WhatsAppWatcher(check_interval=check_interval)

    # Check if running in continuous mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        watcher.run_continuous()
    else:
        # Single check
        watcher.run_once()

    print("\n" + "="*70)
    print("[DONE] WhatsApp watcher complete")
    print("="*70)

if __name__ == "__main__":
    main()
