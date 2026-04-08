#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Manual Session Setup
Opens browser, you login manually, then saves session
"""

import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Set UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

SESSION_FILE = Path(__file__).parent / ".linkedin_session" / "state.json"
SESSION_FILE.parent.mkdir(exist_ok=True)

print("="*70)
print("LINKEDIN MANUAL SESSION SETUP")
print("="*70)

print("\n[INFO] This script will:")
print("  1. Open LinkedIn in browser")
print("  2. Wait for you to login manually")
print("  3. Save your session for future use")
print("  4. Keep browser open for 2 minutes")

print("\n[ACTION] Press Ctrl+C when you're done to save and exit")
print("[ACTION] Or wait 2 minutes and it will auto-save")

with sync_playwright() as p:
    print("\n[STEP 1] Launching browser...")
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("[STEP 2] Opening LinkedIn...")
    page.goto("https://www.linkedin.com/login")

    print("\n" + "="*70)
    print("PLEASE LOGIN TO LINKEDIN IN THE BROWSER")
    print("="*70)
    print("\n[WAIT] Waiting 2 minutes for you to login...")
    print("[INFO] After login, navigate to your feed")
    print("[INFO] Browser will stay open for 2 minutes")
    print("[INFO] Press Ctrl+C anytime to save and exit")

    try:
        # Wait 2 minutes
        for i in range(120):
            time.sleep(1)
            if i % 10 == 0:
                print(f"[WAIT] {120-i} seconds remaining...")
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user, saving session...")

    # Save session
    print("\n[STEP 3] Saving session...")
    try:
        storage_state = context.storage_state()
        with open(SESSION_FILE, 'w') as f:
            json.dump(storage_state, f, indent=2)
        print(f"[OK] ✅ Session saved to: {SESSION_FILE}")

        # Take screenshot
        page.screenshot(path="linkedin_session_saved.png")
        print("[OK] Screenshot saved: linkedin_session_saved.png")

        print("\n" + "="*70)
        print("SESSION SAVED SUCCESSFULLY!")
        print("="*70)
        print("\n[NEXT] You can now use: python linkedin_playwright_poster.py")

    except Exception as e:
        print(f"[ERROR] Could not save session: {e}")

    print("\n[INFO] Closing browser in 5 seconds...")
    time.sleep(5)
    browser.close()

print("\n✅ Done!")
