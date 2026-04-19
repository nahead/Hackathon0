#!/usr/bin/env python3
"""
Lead CRM System
Tracks all WhatsApp leads with complete history and scoring
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class LeadCRM:
    def __init__(self, storage_path: str = "/tmp/leads_crm.json"):
        self.storage_path = Path(storage_path)
        self.leads: Dict[str, Dict] = {}
        self.load_leads()

    def load_leads(self):
        """Load leads from storage"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.leads = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load leads: {e}")
            self.leads = {}

    def save_leads(self):
        """Save leads to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.leads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save leads: {e}")

    def add_or_update_lead(self, phone: str, name: str, message: str,
                          sentiment: Dict = None, response: str = None):
        """Add new lead or update existing lead"""

        if phone not in self.leads:
            # New lead
            self.leads[phone] = {
                'name': name,
                'phone': phone,
                'first_contact': datetime.now().isoformat(),
                'last_contact': datetime.now().isoformat(),
                'total_messages': 1,
                'status': 'new',
                'lead_score': 50,  # Default score
                'messages': [],
                'sentiment_history': [],
                'tags': [],
                'notes': ''
            }
        else:
            # Update existing lead
            self.leads[phone]['last_contact'] = datetime.now().isoformat()
            self.leads[phone]['total_messages'] += 1
            self.leads[phone]['status'] = 'returning'

        # Add message to history
        message_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message[:200],  # Limit length
            'response': response[:200] if response else None,
            'sentiment': sentiment
        }
        self.leads[phone]['messages'].append(message_entry)

        # Keep only last 10 messages
        if len(self.leads[phone]['messages']) > 10:
            self.leads[phone]['messages'] = self.leads[phone]['messages'][-10:]

        # Update lead score based on sentiment
        if sentiment:
            self._update_lead_score(phone, sentiment)

        # Auto-tag based on content
        self._auto_tag_lead(phone, message)

        self.save_leads()

    def _update_lead_score(self, phone: str, sentiment: Dict):
        """Update lead score based on sentiment and behavior"""
        lead = self.leads[phone]
        score = lead['lead_score']

        # Increase score for high-value indicators
        if sentiment.get('is_high_value'):
            score += 20

        # Increase score for urgent messages (shows intent)
        if sentiment.get('is_urgent'):
            score += 15

        # Decrease score for negative sentiment
        if sentiment.get('is_negative'):
            score -= 10

        # Increase score for returning customers
        if lead['total_messages'] > 3:
            score += 10

        # Cap score between 0-100
        lead['lead_score'] = max(0, min(100, score))

    def _auto_tag_lead(self, phone: str, message: str):
        """Automatically tag leads based on message content"""
        message_lower = message.lower()
        lead = self.leads[phone]

        # Service tags
        if any(word in message_lower for word in ['ai', 'automation', 'chatbot', 'bot']):
            if 'ai_automation' not in lead['tags']:
                lead['tags'].append('ai_automation')

        if any(word in message_lower for word in ['website', 'web', 'site']):
            if 'web_development' not in lead['tags']:
                lead['tags'].append('web_development')

        if any(word in message_lower for word in ['app', 'mobile', 'android', 'ios']):
            if 'app_development' not in lead['tags']:
                lead['tags'].append('app_development')

        if any(word in message_lower for word in ['cloud', 'deploy', 'server', 'hosting']):
            if 'cloud_services' not in lead['tags']:
                lead['tags'].append('cloud_services')

        # Budget indicators
        if any(word in message_lower for word in ['enterprise', 'company', 'business', 'team']):
            if 'high_budget' not in lead['tags']:
                lead['tags'].append('high_budget')

        # Urgency tags
        if any(word in message_lower for word in ['urgent', 'asap', 'immediately', 'quick']):
            if 'urgent' not in lead['tags']:
                lead['tags'].append('urgent')

    def get_lead(self, phone: str) -> Optional[Dict]:
        """Get lead details"""
        return self.leads.get(phone)

    def get_hot_leads(self, min_score: int = 70) -> List[Dict]:
        """Get hot leads (high score)"""
        hot_leads = []
        for phone, lead in self.leads.items():
            if lead['lead_score'] >= min_score:
                hot_leads.append(lead)

        # Sort by score descending
        hot_leads.sort(key=lambda x: x['lead_score'], reverse=True)
        return hot_leads

    def get_leads_needing_followup(self, hours: int = 24) -> List[Dict]:
        """Get leads that haven't been contacted in X hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        needs_followup = []

        for phone, lead in self.leads.items():
            last_contact = datetime.fromisoformat(lead['last_contact'])

            # Only follow up with leads that showed interest (score > 40)
            if last_contact < cutoff and lead['lead_score'] > 40:
                needs_followup.append(lead)

        # Sort by lead score descending
        needs_followup.sort(key=lambda x: x['lead_score'], reverse=True)
        return needs_followup

    def get_stats(self) -> Dict:
        """Get CRM statistics"""
        total_leads = len(self.leads)
        hot_leads = len(self.get_hot_leads(70))
        warm_leads = len([l for l in self.leads.values() if 40 <= l['lead_score'] < 70])
        cold_leads = len([l for l in self.leads.values() if l['lead_score'] < 40])

        return {
            'total_leads': total_leads,
            'hot_leads': hot_leads,
            'warm_leads': warm_leads,
            'cold_leads': cold_leads,
            'needs_followup': len(self.get_leads_needing_followup(24))
        }

    def export_to_csv(self, output_path: str):
        """Export leads to CSV for easy viewing"""
        import csv

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Phone', 'First Contact', 'Last Contact',
                           'Total Messages', 'Lead Score', 'Status', 'Tags', 'Notes'])

            for phone, lead in self.leads.items():
                writer.writerow([
                    lead['name'],
                    lead['phone'],
                    lead['first_contact'],
                    lead['last_contact'],
                    lead['total_messages'],
                    lead['lead_score'],
                    lead['status'],
                    ', '.join(lead['tags']),
                    lead['notes']
                ])

if __name__ == "__main__":
    # Test the CRM system
    crm = LeadCRM("/tmp/test_crm.json")

    # Add test leads
    crm.add_or_update_lead(
        "923122955972",
        "Test User",
        "I need enterprise AI automation for my company of 50 people",
        {'is_urgent': False, 'is_negative': False, 'is_high_value': True, 'priority': 'medium'}
    )

    crm.add_or_update_lead(
        "923122955972",
        "Test User",
        "What's the pricing? Need it ASAP",
        {'is_urgent': True, 'is_negative': False, 'is_high_value': False, 'priority': 'high'}
    )

    # Get lead details
    lead = crm.get_lead("923122955972")
    print("Lead Details:")
    print(f"Name: {lead['name']}")
    print(f"Lead Score: {lead['lead_score']}")
    print(f"Tags: {lead['tags']}")
    print(f"Total Messages: {lead['total_messages']}")

    # Get stats
    print("\nCRM Stats:")
    stats = crm.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")

    # Export to CSV
    crm.export_to_csv("/tmp/leads_export.csv")
    print("\nExported to CSV: /tmp/leads_export.csv")
