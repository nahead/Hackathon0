#!/usr/bin/env python3
"""
Email Integration System
Export leads and send targeted email campaigns
"""

import os
import csv
import json
import smtplib
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional

class EmailIntegration:
    def __init__(self, lead_crm):
        self.lead_crm = lead_crm
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))

        # Track email campaigns
        self.campaign_history_path = Path("/tmp/email_campaigns.json")
        self.campaign_history = self._load_history()

    def _load_history(self) -> Dict:
        """Load campaign history"""
        try:
            if self.campaign_history_path.exists():
                with open(self.campaign_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load campaign history: {e}")
        return {'campaigns': []}

    def _save_history(self):
        """Save campaign history"""
        try:
            self.campaign_history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.campaign_history_path, 'w', encoding='utf-8') as f:
                json.dump(self.campaign_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save campaign history: {e}")

    def export_leads_csv(self, output_path: str, segment_criteria: Dict = None) -> int:
        """
        Export leads to CSV file

        Args:
            output_path: Path to save CSV file
            segment_criteria: Optional filters (min_score, max_score, tags, status)

        Returns:
            Number of leads exported
        """
        # Get all leads or filtered leads
        if segment_criteria:
            from broadcast_system import BroadcastSystem
            broadcast = BroadcastSystem(self.lead_crm)
            leads = broadcast.segment_leads(**segment_criteria)
        else:
            leads = list(self.lead_crm.leads.values())

        # Export to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Name', 'Phone', 'Email', 'First Contact', 'Last Contact',
                'Total Messages', 'Lead Score', 'Status', 'Tags', 'Notes'
            ])

            for lead in leads:
                writer.writerow([
                    lead['name'],
                    lead['phone'],
                    lead.get('email', ''),  # Email might not be available
                    lead['first_contact'],
                    lead['last_contact'],
                    lead['total_messages'],
                    lead['lead_score'],
                    lead['status'],
                    ', '.join(lead['tags']),
                    lead.get('notes', '')
                ])

        print(f"[OK] Exported {len(leads)} leads to {output_path}")
        return len(leads)

    def export_leads_json(self, output_path: str, segment_criteria: Dict = None) -> int:
        """Export leads to JSON file"""
        # Get all leads or filtered leads
        if segment_criteria:
            from broadcast_system import BroadcastSystem
            broadcast = BroadcastSystem(self.lead_crm)
            leads = broadcast.segment_leads(**segment_criteria)
        else:
            leads = list(self.lead_crm.leads.values())

        # Export to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        print(f"[OK] Exported {len(leads)} leads to {output_path}")
        return len(leads)

    def send_email_campaign(self,
                           subject: str,
                           body: str,
                           segment_criteria: Dict,
                           campaign_name: str = "Untitled Campaign") -> Dict:
        """
        Send email campaign to segmented leads

        Note: This requires leads to have email addresses
        """
        if not self.smtp_user or not self.smtp_pass:
            return {'error': 'SMTP credentials not configured'}

        # Get target leads
        from broadcast_system import BroadcastSystem
        broadcast = BroadcastSystem(self.lead_crm)
        leads = broadcast.segment_leads(**segment_criteria)

        # Filter leads with email addresses
        leads_with_email = [l for l in leads if l.get('email')]

        if not leads_with_email:
            return {'error': 'No leads with email addresses found'}

        results = {
            'campaign_name': campaign_name,
            'total_targets': len(leads),
            'with_email': len(leads_with_email),
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        campaign = {
            'id': f"email_campaign_{int(datetime.now().timestamp())}",
            'name': campaign_name,
            'subject': subject,
            'created_at': datetime.now().isoformat(),
            'target_count': len(leads_with_email),
            'sent_count': 0,
            'failed_count': 0
        }

        print(f"[EMAIL CAMPAIGN] Starting: {campaign_name}")
        print(f"[EMAIL CAMPAIGN] Target: {len(leads_with_email)} leads with email")

        # Send emails
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)

            for lead in leads_with_email:
                try:
                    # Personalize email
                    personalized_body = body.replace('{name}', lead['name'])

                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = self.smtp_user
                    msg['To'] = lead['email']
                    msg['Subject'] = subject
                    msg.attach(MIMEText(personalized_body, 'plain'))

                    # Send
                    server.send_message(msg)
                    results['sent'] += 1
                    print(f"[OK] Email sent to {lead['name']} ({lead['email']})")

                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"{lead['name']}: {str(e)}")
                    print(f"[ERROR] Failed to send to {lead['name']}: {e}")

            server.quit()

        except Exception as e:
            return {'error': f'SMTP connection failed: {str(e)}'}

        # Save campaign history
        campaign['sent_count'] = results['sent']
        campaign['failed_count'] = results['failed']
        campaign['completed_at'] = datetime.now().isoformat()
        self.campaign_history['campaigns'].append(campaign)
        self._save_history()

        print(f"[EMAIL CAMPAIGN] Complete: {results['sent']} sent, {results['failed']} failed")

        return results

    def get_mailchimp_format(self, segment_criteria: Dict = None) -> List[Dict]:
        """
        Export leads in Mailchimp-compatible format

        Returns list of dicts with: Email Address, First Name, Last Name, Tags
        """
        # Get leads
        if segment_criteria:
            from broadcast_system import BroadcastSystem
            broadcast = BroadcastSystem(self.lead_crm)
            leads = broadcast.segment_leads(**segment_criteria)
        else:
            leads = list(self.lead_crm.leads.values())

        # Format for Mailchimp
        mailchimp_data = []
        for lead in leads:
            if lead.get('email'):
                name_parts = lead['name'].split(' ', 1)
                mailchimp_data.append({
                    'Email Address': lead['email'],
                    'First Name': name_parts[0],
                    'Last Name': name_parts[1] if len(name_parts) > 1 else '',
                    'Tags': ', '.join(lead['tags']),
                    'Lead Score': lead['lead_score'],
                    'Phone': lead['phone']
                })

        return mailchimp_data

    def get_campaign_stats(self) -> Dict:
        """Get email campaign statistics"""
        total_campaigns = len(self.campaign_history['campaigns'])
        total_sent = sum(c.get('sent_count', 0) for c in self.campaign_history['campaigns'])
        total_failed = sum(c.get('failed_count', 0) for c in self.campaign_history['campaigns'])

        return {
            'total_campaigns': total_campaigns,
            'total_emails_sent': total_sent,
            'total_failed': total_failed
        }


if __name__ == "__main__":
    # Test email integration
    from lead_crm import LeadCRM
    from dotenv import load_dotenv

    load_dotenv()

    print("="*70)
    print("TESTING EMAIL INTEGRATION")
    print("="*70)

    # Create test CRM
    crm = LeadCRM("/tmp/test_email_crm.json")

    # Add test leads with emails
    crm.add_or_update_lead(
        "923001234567",
        "Test User 1",
        "I need AI automation",
        {'is_urgent': False, 'is_negative': False, 'is_high_value': True, 'priority': 'medium'}
    )
    crm.leads["923001234567"]['email'] = "test1@example.com"

    crm.add_or_update_lead(
        "923001234568",
        "Test User 2",
        "Looking for web development",
        {'is_urgent': False, 'is_negative': False, 'is_high_value': False, 'priority': 'normal'}
    )
    crm.leads["923001234568"]['email'] = "test2@example.com"

    crm.save_leads()

    # Test email integration
    email_integration = EmailIntegration(crm)

    # Test CSV export
    print("\n[TEST 1] Export leads to CSV:")
    count = email_integration.export_leads_csv("/tmp/leads_export.csv")
    print(f"Exported {count} leads")

    # Test JSON export
    print("\n[TEST 2] Export leads to JSON:")
    count = email_integration.export_leads_json("/tmp/leads_export.json")
    print(f"Exported {count} leads")

    # Test Mailchimp format
    print("\n[TEST 3] Get Mailchimp format:")
    mailchimp_data = email_integration.get_mailchimp_format()
    print(f"Formatted {len(mailchimp_data)} leads for Mailchimp")
    for lead in mailchimp_data:
        print(f"  - {lead['Email Address']}: {lead['First Name']} {lead['Last Name']}")

    print("\n" + "="*70)
    print("EMAIL INTEGRATION TEST COMPLETE")
    print("="*70)
