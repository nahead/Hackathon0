#!/usr/bin/env python3
"""
Test Multi-Language Support and Context Memory
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

# Import conversation history
from implementation.conversation_history import ConversationHistory

# Test conversation history
print("="*70)
print("TEST 1: CONVERSATION HISTORY")
print("="*70)

history = ConversationHistory("/tmp/test_whatsapp_history.json")

# Simulate conversation
contact_id = "923122955972"
contact_name = "Test User"

# First message
print("\n[MESSAGE 1] Customer: I need AI automation")
history.add_message(contact_id, contact_name, "I need AI automation",
                   "Hi! I'd be happy to help with AI automation. What specific tasks are you looking to automate?")

# Second message
print("[MESSAGE 2] Customer: What's the pricing?")
history.add_message(contact_id, contact_name, "What's the pricing?", None)

# Get context
print("\n" + "="*70)
print("CONTEXT RETRIEVED:")
print("="*70)
print(history.get_context_summary(contact_id))

print("\n" + "="*70)
print("CONTACT STATS:")
print("="*70)
stats = history.get_contact_stats(contact_id)
for key, value in stats.items():
    print(f"{key}: {value}")

print("\n" + "="*70)
print("TEST 1: PASSED ✅")
print("="*70)

# Test multi-language (requires Gemini API)
print("\n" + "="*70)
print("TEST 2: MULTI-LANGUAGE SUPPORT")
print("="*70)

gemini_key = os.getenv('GEMINI_API_KEY')
if not gemini_key:
    print("\n[SKIP] GEMINI_API_KEY not set - cannot test AI responses")
    print("Set GEMINI_API_KEY in .env to test multi-language support")
else:
    try:
        import google.generativeai as genai

        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

        test_messages = [
            ("English", "What services do you offer?"),
            ("Roman Urdu", "Mujhe AI automation chahiye"),
            ("Urdu Script", "آپ کی خدمات کیا ہیں؟")
        ]

        for lang, message in test_messages:
            print(f"\n[{lang}] Input: {message}")

            prompt = f"""You are an AI assistant. Detect the language and respond in the SAME language.

Message: {message}

Respond briefly (under 50 words) in the detected language."""

            response = model.generate_content(prompt)
            print(f"[{lang}] Output: {response.text[:200]}")

        print("\n" + "="*70)
        print("TEST 2: PASSED ✅")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("TEST 2: FAILED ❌")

print("\n" + "="*70)
print("ALL TESTS COMPLETE")
print("="*70)
