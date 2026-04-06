# Email Monitoring Agent Skill
# Converts our email watcher functionality into a proper Claude Agent Skill

## Skill Description
Monitor Gmail for important emails and create action items in Obsidian vault.

## Usage
This skill monitors Gmail for unread important emails and creates markdown files in the /Needs_Action folder for Claude to process.

## Implementation

```python
# email_monitor_skill.py
import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

class EmailMonitorSkill:
    def __init__(self, vault_path: str, credentials_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(exist_ok=True)

        # Initialize Gmail API
        self.creds = Credentials.from_authorized_user_file(credentials_path)
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()

    def check_important_emails(self):
        """Check for unread important emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important'
            ).execute()

            messages = results.get('messages', [])
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            for message in new_messages:
                self.create_email_action(message)
                self.processed_ids.add(message['id'])

            return len(new_messages)

        except Exception as e:
            print(f"Error checking emails: {e}")
            return 0

    def create_email_action(self, message):
        """Create action file for email"""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            content = f"""---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
message_id: {message['id']}
---

## Email Content
{msg.get('snippet', '')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Add to calendar if meeting request
- [ ] Create task if action required

## AI Instructions
Please analyze this email and determine the appropriate response. If it requires a reply, draft one for approval. If it's informational, summarize and archive.
"""

            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content, encoding='utf-8')
            print(f"Created action file: {filepath}")

        except Exception as e:
            print(f"Error creating email action: {e}")

# Skill execution function for Claude Code
def execute_email_monitor_skill(vault_path: str = None, credentials_path: str = None):
    """Execute the email monitoring skill"""
    if not vault_path:
        vault_path = os.getenv('AI_EMPLOYEE_VAULT', './AI_Employee_Vault')

    if not credentials_path:
        credentials_path = os.getenv('GMAIL_CREDENTIALS', './credentials.json')

    skill = EmailMonitorSkill(vault_path, credentials_path)
    new_emails = skill.check_important_emails()

    return {
        "status": "success",
        "new_emails_found": new_emails,
        "message": f"Processed {new_emails} new important emails"
    }

if __name__ == "__main__":
    result = execute_email_monitor_skill()
    print(json.dumps(result, indent=2))
```

## Skill Configuration

Add this to your Claude Code skills configuration:

```json
{
  "name": "email_monitor",
  "description": "Monitor Gmail for important emails and create action items",
  "command": "python email_monitor_skill.py",
  "parameters": {
    "vault_path": {
      "type": "string",
      "description": "Path to Obsidian vault",
      "default": "./AI_Employee_Vault"
    },
    "credentials_path": {
      "type": "string",
      "description": "Path to Gmail credentials file",
      "default": "./credentials.json"
    }
  }
}
```

## Usage in Claude Code

```
/email_monitor
```

This will check for new important emails and create action files for processing.