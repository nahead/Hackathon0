#!/usr/bin/env python3
"""
Cloud Gmail Watcher - Platinum Tier
Monitors Gmail for new emails and creates draft responses (cloud agent)
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-employee/logs/cloud-gmail-watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudGmailWatcher')

class CloudGmailWatcher:
    """Cloud Gmail Watcher - Draft-only mode for Platinum Tier"""

    def __init__(self, vault_path: str, credentials_path: str):
        self.vault_path = Path(vault_path)
        self.credentials_path = credentials_path
        self.scopes = ['https://www.googleapis.com/auth/gmail.readonly']

        # Cloud-specific folders
        self.cloud_drafts = self.vault_path / 'Cloud_Drafts'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.processed_emails = self.vault_path / 'Processed_Emails'

        # Ensure directories exist
        self.cloud_drafts.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)
        self.processed_emails.mkdir(exist_ok=True)

        # Track processed email IDs
        self.processed_ids_file = self.vault_path / '.cloud_processed_emails.json'
        self.processed_ids = self.load_processed_ids()

        # Initialize Gmail service
        self.service = self.authenticate_gmail()

        logger.info("Cloud Gmail Watcher initialized")

    def load_processed_ids(self) -> set:
        """Load previously processed email IDs"""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_ids', []))
            except Exception as e:
                logger.warning(f"Could not load processed IDs: {e}")
        return set()

    def save_processed_ids(self):
        """Save processed email IDs"""
        try:
            with open(self.processed_ids_file, 'w') as f:
                json.dump({
                    'processed_ids': list(self.processed_ids),
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save processed IDs: {e}")

    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        token_path = Path(self.credentials_path).parent / 'cloud_token.json'

        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def check_for_new_emails(self):
        """Check for new important emails"""
        try:
            # Query for unread important emails from last 24 hours
            query = 'is:unread is:important newer_than:1d'

            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_emails = []

            for message in messages:
                email_id = message['id']
                if email_id not in self.processed_ids:
                    new_emails.append(email_id)

            logger.info(f"Found {len(new_emails)} new emails to process")
            return new_emails

        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []

    def process_email(self, email_id: str):
        """Process a single email and create draft response"""
        try:
            # Get email details
            message = self.service.users().messages().get(
                userId='me', id=email_id, format='full'
            ).execute()

            # Extract headers
            headers = {}
            for header in message['payload'].get('headers', []):
                headers[header['name'].lower()] = header['value']

            # Extract body (simplified)
            body = self.extract_email_body(message['payload'])

            # Create email metadata
            email_data = {
                'id': email_id,
                'from': headers.get('from', 'Unknown'),
                'to': headers.get('to', 'Unknown'),
                'subject': headers.get('subject', 'No Subject'),
                'date': headers.get('date', 'Unknown'),
                'body': body[:1000],  # Limit body length
                'thread_id': message.get('threadId'),
                'labels': message.get('labelIds', [])
            }

            # Create draft response
            self.create_email_draft(email_data)

            # Mark as processed
            self.processed_ids.add(email_id)

            # Save email for reference
            self.save_email_reference(email_data)

            logger.info(f"Processed email: {email_data['subject'][:50]}...")

        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")

    def extract_email_body(self, payload):
        """Extract email body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body

    def create_email_draft(self, email_data: dict):
        """Create draft email response"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_file = self.cloud_drafts / f'EMAIL_DRAFT_{timestamp}_{email_data["id"][:8]}.md'

        # Determine response type based on content
        response_type = self.classify_email(email_data)
        draft_response = self.generate_draft_response(email_data, response_type)

        draft_content = f"""---
type: email_draft
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
email_id: {email_data['id']}
thread_id: {email_data['thread_id']}
response_type: {response_type}
status: draft
requires_approval: true
---

## Email Draft Response

**To**: {email_data['from']}
**Subject**: Re: {email_data['subject']}
**Response Type**: {response_type}

### Draft Response:
{draft_response}

### Original Email:
**From**: {email_data['from']}
**Subject**: {email_data['subject']}
**Date**: {email_data['date']}

**Body**:
{email_data['body']}

### Actions Required:
- [ ] Review draft response
- [ ] Modify if needed
- [ ] Approve for sending
- [ ] Move to /Approved when ready

**Note**: This draft was created by Cloud Agent. Local agent will handle actual sending.
"""

        draft_file.write_text(draft_content, encoding='utf-8')

        # Create approval request
        self.create_approval_request(email_data, draft_response)

        logger.info(f"Email draft created: {draft_file.name}")

    def classify_email(self, email_data: dict) -> str:
        """Classify email type for appropriate response"""
        subject = email_data['subject'].lower()
        body = email_data['body'].lower()

        # Simple classification logic
        if any(word in subject + body for word in ['invoice', 'payment', 'bill']):
            return 'financial'
        elif any(word in subject + body for word in ['meeting', 'schedule', 'appointment']):
            return 'scheduling'
        elif any(word in subject + body for word in ['urgent', 'asap', 'emergency']):
            return 'urgent'
        elif any(word in subject + body for word in ['quote', 'proposal', 'pricing']):
            return 'business_inquiry'
        else:
            return 'general'

    def generate_draft_response(self, email_data: dict, response_type: str) -> str:
        """Generate appropriate draft response based on email type"""
        responses = {
            'financial': f"""Thank you for your email regarding financial matters.

I have received your message about {email_data['subject']} and will review the details carefully. I will respond with the requested information within 24 hours.

If this is urgent, please don't hesitate to call directly.

Best regards,
AI Employee (Draft Response)""",

            'scheduling': f"""Thank you for reaching out about scheduling.

I have received your request regarding {email_data['subject']}. I will check my calendar and respond with available times within a few hours.

Looking forward to connecting soon.

Best regards,
AI Employee (Draft Response)""",

            'urgent': f"""Thank you for your urgent message.

I have received your email marked as urgent regarding {email_data['subject']}. This has been prioritized and I will respond as soon as possible.

If this requires immediate attention, please call directly.

Best regards,
AI Employee (Draft Response)""",

            'business_inquiry': f"""Thank you for your business inquiry.

I have received your request regarding {email_data['subject']}. I will prepare the requested information and respond within 24 hours.

I appreciate your interest and look forward to working together.

Best regards,
AI Employee (Draft Response)""",

            'general': f"""Thank you for your email.

I have received your message regarding {email_data['subject']} and will respond shortly.

Best regards,
AI Employee (Draft Response)"""
        }

        return responses.get(response_type, responses['general'])

    def create_approval_request(self, email_data: dict, draft_response: str):
        """Create approval request for email sending"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        approval_file = self.pending_approval / f'EMAIL_APPROVAL_{timestamp}_{email_data["id"][:8]}.md'

        approval_content = f"""---
type: approval_request
action: send_email
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
email_id: {email_data['id']}
status: pending
expires_at: {(datetime.now() + timedelta(hours=24)).isoformat()}
---

## Email Send Approval Request

**Action**: Send Email Response
**To**: {email_data['from']}
**Subject**: Re: {email_data['subject']}

### Draft Response:
{draft_response}

### Original Email Context:
- **From**: {email_data['from']}
- **Subject**: {email_data['subject']}
- **Date**: {email_data['date']}

### To Approve:
Move this file to /Approved folder

### To Reject:
Move this file to /Rejected folder

**Note**: Local agent will execute the actual email sending upon approval.
"""

        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"Email approval request created: {approval_file.name}")

    def save_email_reference(self, email_data: dict):
        """Save email reference for audit trail"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ref_file = self.processed_emails / f'EMAIL_REF_{timestamp}_{email_data["id"][:8]}.json'

        with open(ref_file, 'w') as f:
            json.dump(email_data, f, indent=2)

    def run(self):
        """Main run loop"""
        logger.info("Starting Cloud Gmail Watcher...")

        while True:
            try:
                # Check for new emails
                new_email_ids = self.check_for_new_emails()

                # Process each new email
                for email_id in new_email_ids:
                    self.process_email(email_id)

                # Save processed IDs
                if new_email_ids:
                    self.save_processed_ids()

                # Wait before next check
                time.sleep(300)  # Check every 5 minutes

            except KeyboardInterrupt:
                logger.info("Shutting down Cloud Gmail Watcher...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function"""
    vault_path = os.getenv('VAULT_PATH', '/home/ubuntu/ai-employee/vault-sync')
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', '/home/ubuntu/ai-employee/config/credentials.json')

    if not Path(vault_path).exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    if not Path(credentials_path).exists():
        logger.error(f"Gmail credentials not found: {credentials_path}")
        sys.exit(1)

    watcher = CloudGmailWatcher(vault_path, credentials_path)
    watcher.run()

if __name__ == "__main__":
    main()