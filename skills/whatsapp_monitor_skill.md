# WhatsApp Monitor Agent Skill
# Monitors WhatsApp Web for urgent messages and creates action items

## Skill Description
Monitor WhatsApp Web for messages containing urgent keywords and create action items in Obsidian vault.

## Implementation

```python
# whatsapp_monitor_skill.py
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime

class WhatsAppMonitorSkill:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)
        self.session_path = Path(session_path)

        # Keywords that trigger urgent action
        self.urgent_keywords = [
            'urgent', 'asap', 'emergency', 'help', 'problem',
            'invoice', 'payment', 'due', 'deadline', 'meeting',
            'call me', 'important', 'priority', 'issue'
        ]

    def check_urgent_messages(self):
        """Check WhatsApp Web for urgent messages"""
        urgent_messages = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', timeout=30000)

                # Wait for WhatsApp to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=20000)
                except:
                    print("WhatsApp not loaded or not logged in")
                    browser.close()
                    return urgent_messages

                # Find unread messages
                unread_chats = page.query_selector_all('[aria-label*="unread"]')

                for chat in unread_chats[:5]:  # Limit to 5 most recent
                    try:
                        chat_text = chat.inner_text().lower()

                        # Check for urgent keywords
                        if any(keyword in chat_text for keyword in self.urgent_keywords):
                            # Extract contact name and message preview
                            contact_name = "Unknown Contact"
                            message_preview = chat_text[:100]

                            # Try to get contact name
                            try:
                                name_element = chat.query_selector('[data-testid="conversation-info-header"]')
                                if name_element:
                                    contact_name = name_element.inner_text()
                            except:
                                pass

                            urgent_message = {
                                'contact': contact_name,
                                'preview': message_preview,
                                'timestamp': datetime.now().isoformat(),
                                'keywords_found': [kw for kw in self.urgent_keywords if kw in chat_text]
                            }

                            urgent_messages.append(urgent_message)
                            self.create_whatsapp_action(urgent_message)

                    except Exception as e:
                        print(f"Error processing chat: {e}")
                        continue

                browser.close()

        except Exception as e:
            print(f"Error checking WhatsApp: {e}")

        return urgent_messages

    def create_whatsapp_action(self, message_data):
        """Create action file for urgent WhatsApp message"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            contact_safe = "".join(c for c in message_data['contact'] if c.isalnum() or c in (' ', '-', '_')).strip()

            content = f"""---
type: whatsapp_urgent
contact: {message_data['contact']}
received: {message_data['timestamp']}
priority: high
status: pending
keywords_triggered: {', '.join(message_data['keywords_found'])}
---

## WhatsApp Message Alert
**From:** {message_data['contact']}
**Time:** {message_data['timestamp']}
**Urgency Indicators:** {', '.join(message_data['keywords_found'])}

## Message Preview
{message_data['preview']}

## Suggested Actions
- [ ] Open WhatsApp and read full message
- [ ] Reply immediately if urgent
- [ ] Schedule follow-up if needed
- [ ] Create task if action required
- [ ] Escalate if emergency

## AI Instructions
This message contains urgent keywords. Please prioritize this for immediate attention. Check the full context in WhatsApp and determine appropriate response.
"""

            filepath = self.needs_action / f'WHATSAPP_{contact_safe}_{timestamp}.md'
            filepath.write_text(content, encoding='utf-8')
            print(f"Created urgent WhatsApp action: {filepath}")

        except Exception as e:
            print(f"Error creating WhatsApp action: {e}")

def execute_whatsapp_monitor_skill(vault_path: str = None, session_path: str = None):
    """Execute the WhatsApp monitoring skill"""
    if not vault_path:
        vault_path = os.getenv('AI_EMPLOYEE_VAULT', './AI_Employee_Vault')

    if not session_path:
        session_path = os.getenv('WHATSAPP_SESSION_PATH', './.wwebjs_auth')

    skill = WhatsAppMonitorSkill(vault_path, session_path)
    urgent_messages = skill.check_urgent_messages()

    return {
        "status": "success",
        "urgent_messages_found": len(urgent_messages),
        "messages": urgent_messages,
        "message": f"Found {len(urgent_messages)} urgent WhatsApp messages"
    }

if __name__ == "__main__":
    result = execute_whatsapp_monitor_skill()
    print(json.dumps(result, indent=2))
```

## Skill Configuration

```json
{
  "name": "whatsapp_monitor",
  "description": "Monitor WhatsApp Web for urgent messages and create action items",
  "command": "python whatsapp_monitor_skill.py",
  "parameters": {
    "vault_path": {
      "type": "string",
      "description": "Path to Obsidian vault",
      "default": "./AI_Employee_Vault"
    },
    "session_path": {
      "type": "string",
      "description": "Path to WhatsApp session data",
      "default": "./.wwebjs_auth"
    }
  }
}
```

## Usage in Claude Code

```
/whatsapp_monitor
```

This will scan WhatsApp Web for urgent messages and create action files for immediate attention.