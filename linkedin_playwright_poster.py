#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Playwright Poster - Silver Tier Requirement
Posts to LinkedIn using Playwright with session management
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
APPROVED_FOLDER = VAULT_PATH / "Approved"
DONE_FOLDER = VAULT_PATH / "Done"
SESSION_FILE = Path(__file__).parent / ".linkedin_session" / "state.json"

# LinkedIn credentials from environment
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

class LinkedInPlaywrightPoster:
    """Post to LinkedIn using Playwright with session management"""

    def __init__(self, headless=True):
        self.headless = headless
        self.session_file = SESSION_FILE
        self.session_file.parent.mkdir(exist_ok=True)

    def load_session(self, context):
        """Load saved browser session"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    storage_state = json.load(f)
                print(f"[SESSION] Loaded saved session from {self.session_file}")
                return storage_state
            except Exception as e:
                print(f"[WARN] Could not load session: {e}")
        return None

    def save_session(self, context):
        """Save browser session for reuse"""
        try:
            storage_state = context.storage_state()
            with open(self.session_file, 'w') as f:
                json.dump(storage_state, f, indent=2)
            print(f"[SESSION] Saved session to {self.session_file}")
        except Exception as e:
            print(f"[ERROR] Could not save session: {e}")

    def login_to_linkedin(self, page):
        """Login to LinkedIn if not already logged in"""
        print("[LOGIN] Checking LinkedIn login status...")

        # Navigate to LinkedIn
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        time.sleep(2)

        # Check if already logged in
        if "feed" in page.url:
            print("[LOGIN] Already logged in!")
            return True

        # Need to login
        print("[LOGIN] Not logged in, attempting login...")

        if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
            print("[ERROR] LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables required")
            return False

        # Go to login page
        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        time.sleep(1)

        # Fill login form
        page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)

        # Click sign in
        page.click('button[type="submit"]')
        time.sleep(3)

        # Check if login successful
        if "feed" in page.url or "checkpoint" in page.url:
            print("[LOGIN] Login successful!")
            return True
        else:
            print("[ERROR] Login failed")
            return False

    def post_to_linkedin(self, content):
        """Post content to LinkedIn"""
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.headless)

            # Create context with saved session if available
            storage_state = None
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    storage_state = json.load(f)

            context = browser.new_context(storage_state=storage_state) if storage_state else browser.new_context()
            page = context.new_page()

            try:
                # Login if needed
                if not self.login_to_linkedin(page):
                    return False

                # Save session after successful login
                self.save_session(context)

                # Navigate to feed
                page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
                time.sleep(2)

                # Click "Start a post" button
                print("[POST] Looking for 'Start a post' button...")
                try:
                    # Take screenshot for debugging
                    page.screenshot(path="linkedin_feed.png")
                    print("[DEBUG] Screenshot saved: linkedin_feed.png")

                    # Try multiple selectors with more variations
                    selectors = [
                        # New LinkedIn UI selectors
                        'button.share-box-feed-entry__trigger',
                        'button[class*="share-box"]',
                        'div.share-box-feed-entry__trigger',
                        # Text-based selectors
                        'button:has-text("Start a post")',
                        'div:has-text("Start a post")',
                        # Aria label selectors
                        'button[aria-label*="Start a post"]',
                        '[aria-label*="Start a post"]',
                        # Class-based selectors
                        '.artdeco-button.share-box-feed-entry__trigger',
                        'button.artdeco-button--secondary',
                        # Generic fallback
                        'button:has-text("Share")',
                    ]

                    clicked = False
                    for i, selector in enumerate(selectors):
                        try:
                            print(f"[TRY {i+1}/{len(selectors)}] Trying selector: {selector[:50]}...")
                            page.click(selector, timeout=2000)
                            clicked = True
                            print(f"[OK] Button clicked with selector: {selector[:50]}")
                            break
                        except Exception as e:
                            continue

                    if not clicked:
                        print("[ERROR] Could not find 'Start a post' button")
                        print("[INFO] Check linkedin_feed.png to see the page")
                        return False

                    time.sleep(3)

                except Exception as e:
                    print(f"[ERROR] Could not click 'Start a post': {e}")
                    return False

                # Type content in the post editor
                print("[POST] Typing content...")
                try:
                    # Wait for modal to fully open
                    time.sleep(3)

                    # Take screenshot of modal
                    page.screenshot(path="linkedin_modal.png")
                    print("[DEBUG] Modal screenshot saved: linkedin_modal.png")

                    # Try multiple selectors for the editor
                    editor_selectors = [
                        'div[role="textbox"][contenteditable="true"]',
                        'div.ql-editor[contenteditable="true"]',
                        'div[contenteditable="true"]',
                        'div[data-placeholder*="share"]',
                        'div.share-creation-state__text-editor',
                        '.ql-editor.ql-blank',
                        'div[aria-label*="share"]',
                    ]

                    typed = False
                    for i, selector in enumerate(editor_selectors):
                        try:
                            print(f"[TRY {i+1}/{len(editor_selectors)}] Trying editor selector: {selector[:50]}...")

                            # Try to click first to focus
                            page.click(selector, timeout=2000)
                            time.sleep(0.5)

                            # Then type
                            page.fill(selector, content, timeout=2000)
                            typed = True
                            print(f"[OK] Content typed with selector: {selector[:50]}")
                            break
                        except Exception as e:
                            continue

                    if not typed:
                        print("[ERROR] Could not find post editor")
                        print("[INFO] Check linkedin_modal.png to see the modal")
                        return False

                    time.sleep(2)

                except Exception as e:
                    print(f"[ERROR] Could not type content: {e}")
                    return False

                # Click Post button
                print("[POST] Clicking 'Post' button...")
                try:
                    post_selectors = [
                        'button[aria-label*="Post"]',
                        'button:has-text("Post")',
                        '.share-actions__primary-action'
                    ]

                    posted = False
                    for selector in post_selectors:
                        try:
                            page.click(selector, timeout=3000)
                            posted = True
                            break
                        except:
                            continue

                    if not posted:
                        print("[ERROR] Could not find 'Post' button")
                        return False

                    time.sleep(3)

                except Exception as e:
                    print(f"[ERROR] Could not click 'Post' button: {e}")
                    return False

                print("[OK] Post published successfully!")
                return True

            except Exception as e:
                print(f"[ERROR] Posting failed: {e}")
                return False

            finally:
                browser.close()

    def process_approved_posts(self):
        """Process all approved LinkedIn posts"""
        if not APPROVED_FOLDER.exists():
            print(f"[ERROR] Approved folder not found: {APPROVED_FOLDER}")
            return

        # Find LinkedIn post files
        linkedin_posts = list(APPROVED_FOLDER.glob("LINKEDIN_POST_*.md"))

        if not linkedin_posts:
            print("[INFO] No approved LinkedIn posts found")
            return

        print(f"[INBOX] Found {len(linkedin_posts)} approved LinkedIn post(s)")

        for post_file in linkedin_posts:
            print(f"\n[POST] Processing: {post_file.name}")

            try:
                # Read post content
                content = post_file.read_text(encoding='utf-8')

                # Extract content (skip frontmatter)
                lines = content.split('\n')
                post_content = []
                in_frontmatter = False

                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if not in_frontmatter and line.strip():
                        post_content.append(line)

                post_text = '\n'.join(post_content).strip()

                if not post_text:
                    print(f"[WARN] Empty post content, skipping")
                    continue

                print(f"[CONTENT] {post_text[:100]}...")

                # Post to LinkedIn
                success = self.post_to_linkedin(post_text)

                if success:
                    # Move to Done folder
                    DONE_FOLDER.mkdir(exist_ok=True)
                    done_path = DONE_FOLDER / post_file.name
                    post_file.rename(done_path)
                    print(f"[OK] Moved to Done: {post_file.name}")
                else:
                    print(f"[ERROR] Failed to post: {post_file.name}")

            except Exception as e:
                print(f"[ERROR] Error processing {post_file.name}: {e}")

        print(f"\n[OK] Processed {len(linkedin_posts)} post(s)")

def main():
    """Main entry point"""
    print("="*70)
    print("LINKEDIN PLAYWRIGHT POSTER - SILVER TIER")
    print("="*70)

    # Check for headless mode
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'

    print(f"\n[CONFIG] Headless mode: {headless}")
    print(f"[CONFIG] Vault path: {VAULT_PATH}")
    print(f"[CONFIG] Session file: {SESSION_FILE}")

    # Create poster instance
    poster = LinkedInPlaywrightPoster(headless=headless)

    # Process approved posts
    poster.process_approved_posts()

    print("\n" + "="*70)
    print("[DONE] LinkedIn posting complete")
    print("="*70)

if __name__ == "__main__":
    main()
