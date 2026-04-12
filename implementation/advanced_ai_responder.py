#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced AI WhatsApp Responder with Claude API
Fully intelligent, context-aware, natural responses
"""

import os
import json
import requests
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('AdvancedAIResponder')

# Claude API Configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# Business Context - Customize this for your business
BUSINESS_CONTEXT = """
You are an AI assistant for a business automation company.

Our Services:
- WhatsApp AI Auto-Responder (24/7 intelligent message handling)
- LinkedIn Automation (Auto-posting, engagement)
- Email Management (Smart inbox, auto-responses)
- Business Process Automation
- AI Employee Solutions

Pricing:
- Starter Plan: $99/month (Basic automation)
- Professional Plan: $299/month (Full automation suite)
- Enterprise Plan: Custom pricing (Dedicated support)

Business Hours: Monday-Friday, 9 AM - 6 PM (PKT)
Response Time: Within 2 hours during business hours

Tone: Professional, friendly, helpful, and efficient
Language: Respond in the same language the customer uses (English, Urdu, or mixed)
"""


class AdvancedAIResponder:
    """Advanced AI-powered response generator using Claude API"""

    def __init__(self):
        self.api_key = ANTHROPIC_API_KEY
        self.conversation_history = {}  # Track conversations per user
        self.history_file = Path(__file__).parent / ".conversation_history.json"
        self._load_history()

    def _load_history(self):
        """Load conversation history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
            except:
                pass

    def _save_history(self):
        """Save conversation history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _get_conversation_context(self, phone_number):
        """Get recent conversation history for context"""
        if phone_number not in self.conversation_history:
            return []

        # Return last 5 messages for context
        return self.conversation_history[phone_number][-5:]

    def _add_to_history(self, phone_number, role, content):
        """Add message to conversation history"""
        if phone_number not in self.conversation_history:
            self.conversation_history[phone_number] = []

        self.conversation_history[phone_number].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 20 messages per user
        if len(self.conversation_history[phone_number]) > 20:
            self.conversation_history[phone_number] = self.conversation_history[phone_number][-20:]

        self._save_history()

    def generate_advanced_response(self, message_text, sender_name, phone_number, classification):
        """
        Generate advanced AI response using Claude API

        Args:
            message_text: The customer's message
            sender_name: Customer's name
            phone_number: Customer's phone number
            classification: 'routine' or 'serious'

        Returns:
            Intelligent, context-aware response
        """

        # If no API key, fallback to enhanced rule-based
        if not self.api_key:
            logger.warning("[AI] No Claude API key - using enhanced fallback")
            return self._enhanced_fallback_response(message_text, sender_name, classification)

        try:
            # Get conversation context
            context = self._get_conversation_context(phone_number)

            # Build conversation history for Claude
            messages = []
            for msg in context:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message_text
            })

            # Build system prompt
            system_prompt = f"""{BUSINESS_CONTEXT}

Customer Name: {sender_name}
Message Classification: {classification.upper()}

Instructions:
1. Respond naturally and professionally
2. Use the customer's name when appropriate
3. Provide specific, helpful information
4. If asked about services, explain clearly with pricing
5. If asked about availability, mention business hours
6. Keep responses concise (2-4 sentences max)
7. Always end with a helpful question or next step
8. Match the language style of the customer (formal/informal, English/Urdu)

Remember: You are representing a professional business automation company. Be helpful, efficient, and build trust."""

            # Call Claude API
            logger.info(f"[AI] Calling Claude API for intelligent response...")

            headers = {
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }

            payload = {
                'model': CLAUDE_MODEL,
                'max_tokens': 300,
                'temperature': 0.7,
                'system': system_prompt,
                'messages': messages
            }

            response = requests.post(
                CLAUDE_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result['content'][0]['text']

                logger.info(f"[AI] ✅ Claude generated response: {ai_response[:100]}...")

                # Add to conversation history
                self._add_to_history(phone_number, 'user', message_text)
                self._add_to_history(phone_number, 'assistant', ai_response)

                return ai_response

            else:
                logger.error(f"[AI] Claude API error: {response.status_code} - {response.text}")
                return self._enhanced_fallback_response(message_text, sender_name, classification)

        except Exception as e:
            logger.error(f"[AI] Exception: {e}")
            return self._enhanced_fallback_response(message_text, sender_name, classification)

    def _enhanced_fallback_response(self, message_text, sender_name, classification):
        """Enhanced rule-based fallback when Claude API unavailable"""
        message_lower = message_text.lower()

        # Services inquiry
        if any(word in message_lower for word in ['service', 'services', 'provide', 'offer', 'do', 'what']):
            return f"Hi {sender_name}! We specialize in AI-powered business automation:\n\n✅ WhatsApp Auto-Responder (24/7)\n✅ LinkedIn Automation\n✅ Email Management\n✅ Complete AI Employee Solutions\n\nStarting at $99/month. Which service interests you most?"

        # Pricing inquiry
        if any(word in message_lower for word in ['price', 'cost', 'rate', 'fee', 'charge', 'pricing', 'plan']):
            return f"Hi {sender_name}! Our pricing:\n\n💼 Starter: $99/month\n🚀 Professional: $299/month\n🏢 Enterprise: Custom pricing\n\nAll plans include 24/7 support. Would you like details on a specific plan?"

        # Greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'salam', 'assalam']):
            return f"Hello {sender_name}! 👋 Welcome to our AI Business Automation service. We help businesses automate WhatsApp, LinkedIn, and Email with intelligent AI. How can I assist you today?"

        # Thanks
        if any(word in message_lower for word in ['thanks', 'thank', 'شکریہ', 'shukriya']):
            return f"You're very welcome, {sender_name}! 😊 Feel free to reach out anytime if you need help. We're here 24/7!"

        # How it works
        if any(word in message_lower for word in ['how', 'work', 'kaise', 'process']):
            return f"Hi {sender_name}! Here's how it works:\n\n1️⃣ We integrate with your WhatsApp/LinkedIn/Email\n2️⃣ AI learns your business context\n3️⃣ Automatically handles routine messages\n4️⃣ You approve important responses\n\nSetup takes just 15 minutes! Want to get started?"

        # Availability/timing
        if any(word in message_lower for word in ['when', 'time', 'available', 'hours', 'kab']):
            return f"Hi {sender_name}! Our AI works 24/7 non-stop! 🤖\n\nFor human support:\n📅 Monday-Friday, 9 AM - 6 PM (PKT)\n⚡ Response time: Within 2 hours\n\nWhat would you like to know?"

        # Demo/trial
        if any(word in message_lower for word in ['demo', 'trial', 'test', 'try', 'show']):
            return f"Hi {sender_name}! We offer a FREE 7-day trial! 🎉\n\nYou'll get:\n✅ Full access to all features\n✅ Personal onboarding session\n✅ 24/7 support\n\nNo credit card required. Ready to start?"

        # Contact/support
        if any(word in message_lower for word in ['contact', 'support', 'help', 'talk', 'speak']):
            return f"Hi {sender_name}! I'm here to help! 💬\n\nYou can:\n📱 Continue chatting here (I respond instantly)\n📧 Email: support@yourbusiness.com\n📞 Call: +92-312-2955972\n\nWhat specific help do you need?"

        # Default intelligent response
        return f"Hi {sender_name}! Thank you for your message. I'm your AI assistant, and I'm here to help with:\n\n🤖 Business automation questions\n💰 Pricing and plans\n🚀 Getting started\n\nWhat would you like to know more about?"


# Singleton instance
_advanced_responder = None

def get_advanced_responder():
    """Get singleton instance of advanced responder"""
    global _advanced_responder
    if _advanced_responder is None:
        _advanced_responder = AdvancedAIResponder()
    return _advanced_responder
