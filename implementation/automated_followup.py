#!/usr/bin/env python3
"""
Automated Follow-up System
Intelligently follows up with leads based on CRM data
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class AutomatedFollowup:
    def __init__(self, lead_crm, gemini_api_key: str = None):
        self.lead_crm = lead_crm
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY', '')
        self.whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')

        # Track follow-up attempts to avoid spam
        self.followup_history = {}

    def check_and_send_followups(self, hours_since_contact: int = 48) -> Dict:
        """Check for leads needing follow-up and send messages"""
        results = {
            'checked': 0,
            'sent': 0,
            'skipped': 0,
            'errors': 0,
            'leads_contacted': []
        }

        # Get leads needing follow-up
        leads = self.lead_crm.get_leads_needing_followup(hours=hours_since_contact)
        results['checked'] = len(leads)

        if not leads:
            print(f"[OK] No leads need follow-up (checked {hours_since_contact}h window)")
            return results

        print(f"[FOLLOWUP] Found {len(leads)} leads needing follow-up")

        for lead in leads:
            phone = lead['phone']
            name = lead['name']

            # Check if we already followed up recently (avoid spam)
            if self._recently_followed_up(phone, hours=24):
                print(f"[SKIP] Skipping {name} - already followed up in last 24h")
                results['skipped'] += 1
                continue

            # Generate personalized follow-up message
            message = self._generate_followup_message(lead)

            if not message:
                print(f"[WARNING] Could not generate message for {name}")
                results['errors'] += 1
                continue

            # Send WhatsApp message
            success = self._send_whatsapp_message(phone, message)

            if success:
                print(f"[OK] Follow-up sent to {name} ({phone})")
                self._record_followup(phone)
                results['sent'] += 1
                results['leads_contacted'].append({
                    'name': name,
                    'phone': phone,
                    'lead_score': lead['lead_score']
                })
            else:
                print(f"[ERROR] Failed to send follow-up to {name}")
                results['errors'] += 1

        return results

    def _generate_followup_message(self, lead: Dict) -> Optional[str]:
        """Generate personalized follow-up message using AI"""
        try:
            if not self.gemini_api_key:
                # Fallback message if no AI available
                return self._get_fallback_message(lead)

            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

            # Build context from lead data
            lead_context = f"""
Lead Information:
- Name: {lead['name']}
- Lead Score: {lead['lead_score']}/100 ({"Hot" if lead['lead_score'] >= 70 else "Warm" if lead['lead_score'] >= 40 else "Cold"})
- Total Messages: {lead['total_messages']}
- Tags: {', '.join(lead['tags']) if lead['tags'] else 'None'}
- Last Contact: {lead['last_contact']}
- Status: {lead['status']}

Recent Conversation:
"""
            # Add last 2 messages for context
            for msg in lead['messages'][-2:]:
                lead_context += f"Customer: {msg['message'][:100]}\n"
                if msg.get('response'):
                    lead_context += f"You: {msg['response'][:100]}\n"

            prompt = f"""{lead_context}

Generate a friendly, professional follow-up message for WhatsApp.

REQUIREMENTS:
- Keep it under 200 characters
- Be warm and helpful, not pushy
- Reference their previous interest if relevant
- Ask if they need any help or have questions
- Use casual, conversational tone
- If they showed interest in specific services (from tags), mention that
- Sign off as "Nahead"

Generate ONLY the message text, nothing else."""

            response = model.generate_content(prompt)

            if response and response.text:
                return response.text.strip()
            else:
                return self._get_fallback_message(lead)

        except Exception as e:
            print(f"[WARNING] AI generation failed: {e}")
            return self._get_fallback_message(lead)

    def _get_fallback_message(self, lead: Dict) -> str:
        """Get fallback message when AI is unavailable"""
        name = lead['name']

        # Customize based on lead score
        if lead['lead_score'] >= 70:
            # Hot lead - more direct
            return f"Hi {name}! 👋 Just checking in - do you have any questions about our AI automation services? Happy to help! - Nahead"
        elif lead['lead_score'] >= 40:
            # Warm lead - friendly
            return f"Hi {name}! Hope you're doing well. Let me know if you'd like to discuss your project further. I'm here to help! - Nahead"
        else:
            # Cold lead - gentle
            return f"Hi {name}! Just wanted to reach out and see if you need any assistance with AI or development services. Feel free to ask! - Nahead"

    def _send_whatsapp_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message"""
        try:
            if not self.whatsapp_token or not self.whatsapp_phone_id:
                print("[WARNING] WhatsApp credentials not configured")
                return False

            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': to_number,
                'type': 'text',
                'text': {
                    'preview_url': False,
                    'body': message
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 200

        except Exception as e:
            print(f"[ERROR] WhatsApp send error: {e}")
            return False

    def _recently_followed_up(self, phone: str, hours: int = 24) -> bool:
        """Check if we followed up with this lead recently"""
        if phone not in self.followup_history:
            return False

        last_followup = datetime.fromisoformat(self.followup_history[phone])
        hours_since = (datetime.now() - last_followup).total_seconds() / 3600

        return hours_since < hours

    def _record_followup(self, phone: str):
        """Record that we followed up with this lead"""
        self.followup_history[phone] = datetime.now().isoformat()

if __name__ == "__main__":
    # Test the follow-up system
    from lead_crm import LeadCRM
    from dotenv import load_dotenv

    load_dotenv()

    # Create test CRM with sample data
    crm = LeadCRM("/tmp/test_followup_crm.json")

    # Add a test lead that needs follow-up
    from datetime import timedelta
    old_time = (datetime.now() - timedelta(hours=50)).isoformat()

    crm.leads["923122955972"] = {
        'name': 'Test User',
        'phone': '923122955972',
        'first_contact': old_time,
        'last_contact': old_time,
        'total_messages': 2,
        'status': 'returning',
        'lead_score': 75,
        'messages': [
            {
                'timestamp': old_time,
                'message': 'I need AI automation for my business',
                'response': 'Great! I can help with that.',
                'sentiment': {'is_urgent': False, 'is_negative': False, 'is_high_value': True}
            }
        ],
        'sentiment_history': [],
        'tags': ['ai_automation', 'high_budget'],
        'notes': ''
    }
    crm.save_leads()

    # Test follow-up system
    followup = AutomatedFollowup(crm)

    print("="*70)
    print("TESTING AUTOMATED FOLLOW-UP SYSTEM")
    print("="*70)

    results = followup.check_and_send_followups(hours_since_contact=48)

    print("\n" + "="*70)
    print("FOLLOW-UP RESULTS:")
    print("="*70)
    print(f"Leads Checked: {results['checked']}")
    print(f"Messages Sent: {results['sent']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Errors: {results['errors']}")

    if results['leads_contacted']:
        print("\nLeads Contacted:")
        for lead in results['leads_contacted']:
            print(f"  - {lead['name']} (Score: {lead['lead_score']})")
