#!/usr/bin/env python3
"""
Conversation History Manager
Tracks WhatsApp conversation history for context-aware responses
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ConversationHistory:
    def __init__(self, storage_path: str = "/tmp/conversation_history.json"):
        self.storage_path = Path(storage_path)
        self.history: Dict[str, List[Dict]] = {}
        self.load_history()

    def load_history(self):
        """Load conversation history from file"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
            self.history = {}

    def save_history(self):
        """Save conversation history to file"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def add_message(self, contact_id: str, contact_name: str, message: str, response: str = None):
        """Add a message to conversation history"""
        if contact_id not in self.history:
            self.history[contact_id] = []

        entry = {
            'timestamp': datetime.now().isoformat(),
            'contact_name': contact_name,
            'message': message,
            'response': response
        }

        self.history[contact_id].append(entry)

        # Keep only last 10 messages per contact
        if len(self.history[contact_id]) > 10:
            self.history[contact_id] = self.history[contact_id][-10:]

        self.save_history()

    def get_history(self, contact_id: str, limit: int = 5) -> List[Dict]:
        """Get conversation history for a contact"""
        if contact_id not in self.history:
            return []

        # Return last N messages
        return self.history[contact_id][-limit:]

    def get_context_summary(self, contact_id: str) -> str:
        """Get a formatted summary of conversation history"""
        history = self.get_history(contact_id, limit=3)

        if not history:
            return "No previous conversation history."

        summary = "PREVIOUS CONVERSATION HISTORY:\n"
        for i, entry in enumerate(history, 1):
            timestamp = datetime.fromisoformat(entry['timestamp'])
            time_ago = self._time_ago(timestamp)

            summary += f"\n{i}. {time_ago}:\n"
            summary += f"   Customer: {entry['message'][:100]}\n"
            if entry.get('response'):
                summary += f"   You: {entry['response'][:100]}\n"

        return summary

    def _time_ago(self, timestamp: datetime) -> str:
        """Convert timestamp to human-readable time ago"""
        now = datetime.now()
        diff = now - timestamp

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"
        else:
            return timestamp.strftime("%Y-%m-%d")

    def get_contact_stats(self, contact_id: str) -> Dict:
        """Get statistics for a contact"""
        history = self.history.get(contact_id, [])

        if not history:
            return {
                'total_messages': 0,
                'first_contact': None,
                'last_contact': None,
                'status': 'new'
            }

        first_msg = history[0]
        last_msg = history[-1]

        return {
            'total_messages': len(history),
            'first_contact': first_msg['timestamp'],
            'last_contact': last_msg['timestamp'],
            'status': 'returning' if len(history) > 1 else 'new'
        }

    def cleanup_old_conversations(self, days: int = 30):
        """Remove conversations older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)

        for contact_id in list(self.history.keys()):
            # Filter out old messages
            self.history[contact_id] = [
                msg for msg in self.history[contact_id]
                if datetime.fromisoformat(msg['timestamp']) > cutoff
            ]

            # Remove contact if no messages left
            if not self.history[contact_id]:
                del self.history[contact_id]

        self.save_history()

if __name__ == "__main__":
    # Test the conversation history manager
    history = ConversationHistory("/tmp/test_history.json")

    # Add some test conversations
    history.add_message(
        "923122955972",
        "Test User",
        "Hi, I need AI automation",
        "Hi! I'd be happy to help with AI automation. What specific tasks are you looking to automate?"
    )

    history.add_message(
        "923122955972",
        "Test User",
        "What's the pricing?",
        None
    )

    # Get context summary
    print(history.get_context_summary("923122955972"))
    print("\nContact Stats:")
    print(history.get_contact_stats("923122955972"))
