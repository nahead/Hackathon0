#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Playwright Poster - Optimized & Efficient
Best practices implementation with proper error handling
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
APPROVED_FOLDER = VAULT_PATH / "Approved"
DONE_FOLDER = VAULT_PATH / "Done"
SESSION_FILE = Path(__file__).parent / ".linkedin_session" / "state.json"

LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

class LinkedInPoster:
    """Optimized LinkedIn Poster with Playwright"""

    def __init__(self, headless=True, timeout=30000):
        self.headless = headless
        self.timeout = timeout
        self.session_file = SESSION_FILE
        self.session_file.parent.mkdir(exist_ok=True)

    def post_to_linkedin(self, content, max_retries=2):
        """Post content to LinkedIn with retry logic"""

        for attempt in range(max_retries):
            try:
                print(f"\n[ATTEMPT {attempt + 1}/{max_retries}] Starting post attempt...")

                with sync_playwright() as p:
                    # Launch browser
                    browser = p.chromium.launch(
                        headless=self.headless,
                        args=['--disable-blink-features=AutomationControlled']
                    )

                    # Load session if exists
                    storage_state = None
                    if self.session_file.exists():
                        with open(self.session_file, 'r') as f:
                            storage_state = json.load(f)

                    # Create context
                    context = browser.new_context(
                        storage_state=storage_state,
                        viewport={'width': 1280, 'height': 720}
                    )

                    page = context.new_page()
                    page.set_default_timeout(self.timeout)

                    # Navigate to LinkedIn feed
                    print("[STEP 1] Navigating to LinkedIn feed...")
                    page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")

                    # Check if logged in
                    if "login" in page.url or "uas" in page.url:
                        print("[ERROR] Not logged in - session expired")
                        browser.close()
                        return False

                    print("[OK] Logged in successfully")

                    # Save/update session
                    storage_state = context.storage_state()
                    with open(self.session_file, 'w') as f:
                        json.dump(storage_state, f, indent=2)

                    # Wait for page to be fully loaded
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)

                    # Click "Start a post" button
                    print("[STEP 2] Clicking 'Start a post'...")

                    # Use the most reliable selector
                    start_post_clicked = False

                    # Try clicking the share box
                    try:
                        page.click('button:has-text("Start a post")', timeout=5000)
                        start_post_clicked = True
                        print("[OK] Clicked 'Start a post' button")
                    except:
                        try:
                            page.click('div:has-text("Start a post")', timeout=5000)
                            start_post_clicked = True
                            print("[OK] Clicked 'Start a post' div")
                        except:
                            print("[ERROR] Could not find 'Start a post' button")
                            page.screenshot(path=f"error_no_button_{attempt}.png")
                            browser.close()
                            continue

                    # Wait for modal to open
                    print("[STEP 3] Waiting for post modal...")
                    time.sleep(3)

                    # Find and fill the editor
                    print("[STEP 4] Typing content...")

                    editor_filled = False

                    # Try to find the editor
                    try:
                        # Wait for editor to be visible
                        page.wait_for_selector('div[contenteditable="true"]', timeout=5000)

                        # Click to focus
                        page.click('div[contenteditable="true"]')
                        time.sleep(0.5)

                        # Type content
                        page.keyboard.type(content, delay=50)
                        editor_filled = True
                        print("[OK] Content typed successfully")

                    except Exception as e:
                        print(f"[ERROR] Could not type content: {e}")
                        page.screenshot(path=f"error_no_editor_{attempt}.png")
                        browser.close()
                        continue

                    # Wait a bit for content to be processed
                    time.sleep(2)

                    # Click Post button
                    print("[STEP 5] Clicking 'Post' button...")

                    post_clicked = False

                    try:
                        # Find and click the Post button
                        page.click('button:has-text("Post")', timeout=5000)
                        post_clicked = True
                        print("[OK] Clicked 'Post' button")
                    except:
                        try:
                            # Alternative selector
                            page.click('button[type="submit"]', timeout=5000)
                            post_clicked = True
                            print("[OK] Clicked submit button")
                        except Exception as e:
                            print(f"[ERROR] Could not click Post button: {e}")
                            page.screenshot(path=f"error_no_post_button_{attempt}.png")
                            browser.close()
                            continue

                    # Wait for post to be published
                    print("[STEP 6] Waiting for post to publish...")
                    time.sleep(5)

                    # Take success screenshot
                    page.screenshot(path="linkedin_post_success.png")
                    print("[OK] Post published successfully!")

                    browser.close()
                    return True

            except PlaywrightTimeout as e:
                print(f"[ERROR] Timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"[RETRY] Retrying in 3 seconds...")
                    time.sleep(3)
                continue

            except Exception as e:
                print(f"[ERROR] Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"[RETRY] Retrying in 3 seconds...")
                    time.sleep(3)
                continue

        print(f"[FAILED] All {max_retries} attempts failed")
        return False

    def process_approved_posts(self):
        """Process all approved LinkedIn posts"""

        if not APPROVED_FOLDER.exists():
            print(f"[ERROR] Approved folder not found: {APPROVED_FOLDER}")
            return

        # Find LinkedIn posts
        linkedin_posts = list(APPROVED_FOLDER.glob("LINKEDIN_POST_*.md"))

        if not linkedin_posts:
            print("[INFO] No approved LinkedIn posts found")
            return

        print(f"\n[FOUND] {len(linkedin_posts)} approved post(s)")

        success_count = 0
        fail_count = 0

        for post_file in linkedin_posts:
            print(f"\n{'='*70}")
            print(f"[POST] Processing: {post_file.name}")
            print('='*70)

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

                print(f"\n[CONTENT] Preview:")
                print(f"{post_text[:200]}...")

                # Post to LinkedIn
                success = self.post_to_linkedin(post_text)

                if success:
                    # Move to Done folder
                    DONE_FOLDER.mkdir(exist_ok=True)
                    done_path = DONE_FOLDER / post_file.name
                    post_file.rename(done_path)
                    print(f"\n[SUCCESS] ✅ Posted and moved to Done: {post_file.name}")
                    success_count += 1
                else:
                    print(f"\n[FAILED] ❌ Could not post: {post_file.name}")
                    fail_count += 1

            except Exception as e:
                print(f"[ERROR] Error processing {post_file.name}: {e}")
                fail_count += 1

        # Summary
        print(f"\n{'='*70}")
        print("SUMMARY")
        print('='*70)
        print(f"✅ Successfully posted: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📊 Total processed: {success_count + fail_count}")

def main():
    """Main entry point"""
    print("="*70)
    print("LINKEDIN PLAYWRIGHT POSTER - OPTIMIZED")
    print("="*70)

    # Check for headless mode
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'

    print(f"\n[CONFIG] Headless mode: {headless}")
    print(f"[CONFIG] Vault path: {VAULT_PATH}")
    print(f"[CONFIG] Session file: {SESSION_FILE}")

    # Check session
    if not SESSION_FILE.exists():
        print("\n[WARN] No saved session found")
        print("[INFO] Run: python linkedin_manual_session.py")
        print("[INFO] to create a session first")
        return

    # Create poster instance
    poster = LinkedInPoster(headless=headless, timeout=30000)

    # Process approved posts
    poster.process_approved_posts()

    print("\n" + "="*70)
    print("[DONE] LinkedIn posting complete")
    print("="*70)

if __name__ == "__main__":
    main()
