#!/usr/bin/env python3
"""
WhatsApp Broadcast System
Send targeted messages to lead segments with rate limiting
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class BroadcastSystem:
    def __init__(self, lead_crm):
        self.lead_crm = lead_crm
        self.whatsapp_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        self.whatsapp_phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')

        # Rate limiting: WhatsApp allows ~80 messages/second, we'll be conservative
        self.messages_per_minute = 50
        self.delay_between_messages = 60.0 / self.messages_per_minute  # 1.2 seconds

        # Track broadcast history
        self.broadcast_history_path = Path("/tmp/broadcast_history.json")
        self.broadcast_history = self._load_history()

    def _load_history(self) -> Dict:
        """Load broadcast history"""
        try:
            if self.broadcast_history_path.exists():
                with open(self.broadcast_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load broadcast history: {e}")
        return {'broadcasts': []}

    def _save_history(self):
        """Save broadcast history"""
        try:
            self.broadcast_history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.broadcast_history_path, 'w', encoding='utf-8') as f:
                json.dump(self.broadcast_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save broadcast history: {e}")

    def segment_leads(self,
                     min_score: int = None,
                     max_score: int = None,
                     tags: List[str] = None,
                     status: str = None) -> List[Dict]:
        """
        Segment leads based on criteria

        Args:
            min_score: Minimum lead score (0-100)
            max_score: Maximum lead score (0-100)
            tags: List of tags to filter by (any match)
            status: Lead status ('new', 'returning')
        """
        all_leads = list(self.lead_crm.leads.values())
        filtered = []

        for lead in all_leads:
            # Score filter
            if min_score is not None and lead['lead_score'] < min_score:
                continue
            if max_score is not None and lead['lead_score'] > max_score:
                continue

            # Tags filter (any tag matches)
            if tags:
                if not any(tag in lead['tags'] for tag in tags):
                    continue

            # Status filter
            if status and lead['status'] != status:
                continue

            filtered.append(lead)

        return filtered

    def create_broadcast(self,
                        name: str,
                        message: str,
                        segment_criteria: Dict,
                        schedule_time: datetime = None) -> Dict:
        """
        Create a broadcast campaign

        Args:
            name: Campaign name
            message: Message to send
            segment_criteria: Dict with min_score, max_score, tags, status
            schedule_time: When to send (None = immediate)
        """
        # Get target leads
        leads = self.segment_leads(**segment_criteria)

        broadcast = {
            'id': f"broadcast_{int(time.time())}",
            'name': name,
            'message': message,
            'segment_criteria': segment_criteria,
            'target_count': len(leads),
            'target_leads': [{'phone': l['phone'], 'name': l['name']} for l in leads],
            'created_at': datetime.now().isoformat(),
            'schedule_time': schedule_time.isoformat() if schedule_time else None,
            'status': 'scheduled' if schedule_time else 'ready',
            'sent_count': 0,
            'failed_count': 0,
            'delivery_log': []
        }

        self.broadcast_history['broadcasts'].append(broadcast)
        self._save_history()

        return broadcast

    def send_broadcast(self, broadcast_id: str) -> Dict:
        """
        Send a broadcast campaign

        Returns:
            Dict with results: sent_count, failed_count, errors
        """
        # Find broadcast
        broadcast = None
        for b in self.broadcast_history['broadcasts']:
            if b['id'] == broadcast_id:
                broadcast = b
                break

        if not broadcast:
            return {'error': 'Broadcast not found'}

        if broadcast['status'] == 'completed':
            return {'error': 'Broadcast already sent'}

        # Check if scheduled for future
        if broadcast['schedule_time']:
            schedule_time = datetime.fromisoformat(broadcast['schedule_time'])
            if datetime.now() < schedule_time:
                return {'error': f"Broadcast scheduled for {schedule_time}"}

        print(f"[BROADCAST] Starting: {broadcast['name']}")
        print(f"[BROADCAST] Target: {broadcast['target_count']} leads")

        results = {
            'sent_count': 0,
            'failed_count': 0,
            'errors': []
        }

        broadcast['status'] = 'sending'
        broadcast['started_at'] = datetime.now().isoformat()

        # Send to each lead with rate limiting
        for i, lead in enumerate(broadcast['target_leads'], 1):
            phone = lead['phone']
            name = lead['name']

            # Personalize message
            personalized_message = broadcast['message'].replace('{name}', name)

            # Send message
            success = self._send_whatsapp_message(phone, personalized_message)

            # Log result
            log_entry = {
                'phone': phone,
                'name': name,
                'timestamp': datetime.now().isoformat(),
                'success': success
            }
            broadcast['delivery_log'].append(log_entry)

            if success:
                results['sent_count'] += 1
                print(f"[OK] {i}/{broadcast['target_count']}: {name}")
            else:
                results['failed_count'] += 1
                results['errors'].append(f"Failed: {name} ({phone})")
                print(f"[ERROR] {i}/{broadcast['target_count']}: {name}")

            # Rate limiting - wait between messages
            if i < broadcast['target_count']:
                time.sleep(self.delay_between_messages)

        # Update broadcast status
        broadcast['status'] = 'completed'
        broadcast['completed_at'] = datetime.now().isoformat()
        broadcast['sent_count'] = results['sent_count']
        broadcast['failed_count'] = results['failed_count']

        self._save_history()

        print(f"[BROADCAST] Complete: {results['sent_count']} sent, {results['failed_count']} failed")

        return results

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

    def get_broadcast_stats(self) -> Dict:
        """Get broadcast statistics"""
        total_broadcasts = len(self.broadcast_history['broadcasts'])
        completed = len([b for b in self.broadcast_history['broadcasts'] if b['status'] == 'completed'])
        total_sent = sum(b.get('sent_count', 0) for b in self.broadcast_history['broadcasts'])
        total_failed = sum(b.get('failed_count', 0) for b in self.broadcast_history['broadcasts'])

        return {
            'total_broadcasts': total_broadcasts,
            'completed_broadcasts': completed,
            'total_messages_sent': total_sent,
            'total_failed': total_failed
        }

    def list_broadcasts(self, status: str = None) -> List[Dict]:
        """List all broadcasts, optionally filtered by status"""
        broadcasts = self.broadcast_history['broadcasts']

        if status:
            broadcasts = [b for b in broadcasts if b['status'] == status]

        # Return summary (without full delivery logs)
        return [{
            'id': b['id'],
            'name': b['name'],
            'status': b['status'],
            'target_count': b['target_count'],
            'sent_count': b.get('sent_count', 0),
            'failed_count': b.get('failed_count', 0),
            'created_at': b['created_at'],
            'completed_at': b.get('completed_at')
        } for b in broadcasts]


if __name__ == "__main__":
    # Test the broadcast system
    from lead_crm import LeadCRM
    from dotenv import load_dotenv

    load_dotenv()

    # Create test CRM with sample leads
    crm = LeadCRM("/tmp/test_broadcast_crm.json")

    # Add test leads
    crm.add_or_update_lead(
        "923001234567",
        "Hot Lead 1",
        "I need AI automation urgently",
        {'is_urgent': True, 'is_negative': False, 'is_high_value': True, 'priority': 'high'}
    )

    crm.add_or_update_lead(
        "923001234568",
        "Hot Lead 2",
        "Looking for enterprise AI solutions",
        {'is_urgent': False, 'is_negative': False, 'is_high_value': True, 'priority': 'medium'}
    )

    crm.add_or_update_lead(
        "923001234569",
        "Warm Lead",
        "Tell me about your services",
        {'is_urgent': False, 'is_negative': False, 'is_high_value': False, 'priority': 'normal'}
    )

    # Test broadcast system
    broadcast = BroadcastSystem(crm)

    print("="*70)
    print("TESTING BROADCAST SYSTEM")
    print("="*70)

    # Test segmentation
    print("\n[TEST 1] Segment hot leads (score >= 70):")
    hot_leads = broadcast.segment_leads(min_score=70)
    print(f"Found {len(hot_leads)} hot leads")
    for lead in hot_leads:
        print(f"  - {lead['name']} (Score: {lead['lead_score']})")

    # Create broadcast campaign
    print("\n[TEST 2] Create broadcast campaign:")
    campaign = broadcast.create_broadcast(
        name="Hot Leads Promo",
        message="Hi {name}! Special offer on AI automation services. Reply for details! - Nahead",
        segment_criteria={'min_score': 70}
    )
    print(f"Campaign created: {campaign['name']}")
    print(f"Target: {campaign['target_count']} leads")

    # List broadcasts
    print("\n[TEST 3] List all broadcasts:")
    broadcasts = broadcast.list_broadcasts()
    for b in broadcasts:
        print(f"  - {b['name']}: {b['status']} ({b['target_count']} targets)")

    print("\n" + "="*70)
    print("BROADCAST SYSTEM TEST COMPLETE")
    print("="*70)
