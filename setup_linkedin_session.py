#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Session Setup - Save login session for future use
"""

import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

# Configuration
SESSION_FILE = Path(__file__).parent / ".linkedin_session" / "state.json"
SESSION_FILE.parent.mkdir(exist_ok=True)

LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

def setup_linkedin_session():
    """Setup and save LinkedIn session"""

    print("="*70)
    print("LINKEDIN SESSION SETUP")
    print("="*70)

    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        print("\n[ERROR] LinkedIn credentials not found in .env file")
        print("[INFO] Add these to your .env file:")
        print("  LINKEDIN_EMAIL=your_email@gmail.com")
        print("  LINKEDIN_PASSWORD=your_password")
        return False

    print(f"\n[CONFIG] Email: {LINKEDIN_EMAIL}")
    print(f"[CONFIG] Session file: {SESSION_FILE}")

    with sync_playwright() as p:
        print("\n[STEP 1] Launching browser...")
        browser = p.chromium.launch(headless=False)

        # Check if session exists
        storage_state = None
        if SESSION_FILE.exists():
            print("[INFO] Found existing session, trying to load...")
            try:
                with open(SESSION_FILE, 'r') as f:
                    storage_state = json.load(f)
            except:
                print("[WARN] Could not load session, will create new one")

        # Create context with or without saved session
        if storage_state:
            context = browser.new_context(storage_state=storage_state)
        else:
            context = browser.new_context()

        page = context.new_page()

        print("\n[STEP 2] Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        time.sleep(5)  # Wait longer for page to fully load

        # Check if already logged in by looking at actual URL (not redirect params)
        current_url = page.url
        print(f"[DEBUG] Current URL: {current_url}")

        # Check if we're on the actual feed page (not login page with feed in redirect)
        if current_url.startswith("https://www.linkedin.com/feed") and "login" not in current_url and "uas" not in current_url:
            print("[OK] ✅ Already logged in!")
        else:
            print("[INFO] Not logged in, attempting login...")

            # Go to login page
            page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
            time.sleep(2)

            print("[STEP 3] Filling login form...")
            try:
                page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
                time.sleep(1)
                page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
                time.sleep(1)

                print("[STEP 4] Clicking sign in...")
                page.click('button[type="submit"]')

                print("\n[WAIT] Waiting for login to complete...")
                print("[INFO] If you see CAPTCHA or verification, please complete it")
                print("[INFO] Browser will wait for 60 seconds...")

                # Wait longer for login to complete
                time.sleep(15)

                # Check if login successful
                current_url = page.url
                print(f"[DEBUG] Current URL: {current_url}")

                if current_url.startswith("https://www.linkedin.com/feed"):
                    print("[OK] ✅ Login successful!")
                elif "checkpoint" in current_url:
                    print("\n[WAIT] ⚠️ LinkedIn security checkpoint detected")
                    print("[ACTION] Please complete the verification in the browser")
                    print("[INFO] Waiting for you to complete verification...")
                    print("[INFO] Script will automatically detect when verification is done")

                    # Poll for checkpoint completion (check every 3 seconds for up to 3 minutes)
                    max_attempts = 60
                    for attempt in range(max_attempts):
                        time.sleep(3)
                        current_url = page.url
                        print(f"[CHECK {attempt+1}/{max_attempts}] Waiting for verification...")

                        if current_url.startswith("https://www.linkedin.com/feed"):
                            print("[OK] ✅ Verification complete!")
                            break
                        elif "checkpoint" not in current_url:
                            print("[INFO] Checkpoint passed, navigating to feed...")
                            page.goto("https://www.linkedin.com/feed/")
                            time.sleep(3)
                            break
                    else:
                        print("[WARN] Timeout waiting for verification")
                        print("[INFO] Trying to navigate to feed anyway...")
                        page.goto("https://www.linkedin.com/feed/")
                        time.sleep(3)
                elif "login" in current_url or "uas" in current_url:
                    print("\n[WAIT] ⚠️ Still on login page")
                    print("[ACTION] Please complete login manually in the browser")
                    print("[INFO] Waiting for you to complete login...")
                    print("[INFO] Script will automatically detect when you're logged in")

                    # Poll for successful login (check every 3 seconds for up to 2 minutes)
                    max_attempts = 40
                    for attempt in range(max_attempts):
                        time.sleep(3)
                        current_url = page.url
                        print(f"[CHECK {attempt+1}/{max_attempts}] Current URL: {current_url[:60]}...")

                        if current_url.startswith("https://www.linkedin.com/feed"):
                            print("[OK] ✅ Login detected!")
                            break
                        elif "checkpoint" in current_url:
                            print("[INFO] Checkpoint detected, waiting for completion...")
                    else:
                        print("[WARN] Timeout waiting for login")
                        print("[INFO] Trying to navigate to feed anyway...")
                        page.goto("https://www.linkedin.com/feed/")
                        time.sleep(3)
                else:
                    print("[WARN] Unexpected page, waiting for manual completion...")
                    print("[ACTION] Please navigate to LinkedIn feed manually")
                    print("[INFO] Waiting 60 seconds...")

                    # Poll for feed page
                    for i in range(20):
                        time.sleep(3)
                        current_url = page.url
                        if "feed" in current_url:
                            print("[OK] Feed page detected!")
                            break

            except Exception as e:
                print(f"[ERROR] Login failed: {e}")
                browser.close()
                return False

        # Save session
        print("\n[STEP 5] Saving session...")
        try:
            storage_state = context.storage_state()
            with open(SESSION_FILE, 'w') as f:
                json.dump(storage_state, f, indent=2)
            print(f"[OK] ✅ Session saved to: {SESSION_FILE}")
        except Exception as e:
            print(f"[ERROR] Could not save session: {e}")

        # Take screenshot
        print("\n[STEP 6] Taking screenshot...")
        screenshot_path = "linkedin_logged_in.png"
        page.screenshot(path=screenshot_path)
        print(f"[OK] Screenshot saved: {screenshot_path}")

        # Show current page info
        print("\n[INFO] Current page:")
        print(f"  URL: {page.url}")
        print(f"  Title: {page.title()}")

        print("\n[SUCCESS] ✅ Session setup complete!")
        print("\n[INFO] Browser will stay open for 10 seconds...")
        print("[ACTION] You can verify you're logged in")
        time.sleep(10)

        browser.close()

        print("\n" + "="*70)
        print("SESSION SAVED SUCCESSFULLY")
        print("="*70)
        print("\n[NEXT] You can now use linkedin_playwright_poster.py")
        print("[INFO] The session will be reused automatically")

        return True

if __name__ == "__main__":
    success = setup_linkedin_session()

    if success:
        print("\n✅ Setup complete! Session is ready for posting.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
