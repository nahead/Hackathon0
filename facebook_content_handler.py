#!/usr/bin/env python3
"""
Facebook Content Handler - UPDATED SELECTORS (2026)
Fixed for current Facebook interface
"""

import os
import time
import re
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

class FacebookContentHandler:
    def __init__(self, vault_path, session_path="facebook_session"):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.archive_path = self.vault_path / "Archive"
        self.session_path = Path(session_path)

        # Create directories
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Updated Facebook selectors (2026) - More comprehensive
        self.post_selectors = [
            # 2026 Updated selectors
            'div[role="textbox"][data-lexical-editor="true"]',
            'div[contenteditable="true"][role="textbox"]',
            '[data-testid="status-attachment-mentions-input"]',
            '[data-testid="post-composer-text-input"]',
            'div[aria-label*="What\'s on your mind"]',
            'div[placeholder*="What\'s on your mind"]',
            '[aria-label*="Create a post"]',
            'div[data-testid*="composer"]',
            'div[role="textbox"][aria-multiline="true"]',
            '.notranslate._1mf',
            '.notranslate._5rpu',
            # Generic fallbacks
            'div[contenteditable="true"]',
            'textarea[placeholder*="mind"]',
            'div[role="textbox"]'
        ]

        self.post_button_selectors = [
            # 2026 Updated post buttons
            '[data-testid="react-composer-post-button"]',
            'div[aria-label="Post"][role="button"]',
            'div[role="button"]:has-text("Post")',
            '[data-testid="composer-save-button"]',
            'button:has-text("Post")',
            '[aria-label*="Share post"]',
            'div[role="button"][tabindex="0"]:has-text("Post")',
            # Generic fallbacks
            'button:has-text("Post")',
            'div:has-text("Post")[role="button"]'
        ]

    def find_element_with_fallbacks(self, page, selectors, element_name, timeout=20000):
        """Try multiple selectors with longer timeout"""
        print(f"SEARCHING: Looking for {element_name}...")

        for i, selector in enumerate(selectors):
            try:
                print(f"TRYING: Selector {i+1}/{len(selectors)}: {selector}")
                element = page.wait_for_selector(selector, timeout=timeout//len(selectors))
                if element and element.is_visible():
                    print(f"SUCCESS: Found {element_name} with selector: {selector}")
                    return element, selector
            except Exception as e:
                print(f"FAILED: Selector {selector} - {str(e)[:100]}")
                continue

        # If all fail, let user inspect manually
        print(f"\n❌ Could not find {element_name} with any selector")
        print("🔍 MANUAL INSPECTION NEEDED:")
        print("1. Right-click on 'What's on your mind' box")
        print("2. Select 'Inspect Element'")
        print("3. Look for data-testid, aria-label, or class attributes")
        print("4. Share the selector with me")

        input("Press Enter to continue (or Ctrl+C to stop)...")
        raise Exception(f"Could not find {element_name} with any selector")

    def post_to_facebook_browser(self, content):
        """Post content to Facebook using browser automation"""
        try:
            with sync_playwright() as p:
                print("STARTING: Facebook posting process (UPDATED VERSION)...")

                # Launch browser with Facebook session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Keep visible for debugging
                    viewport={"width": 1280, "height": 720},
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.set_default_timeout(30000)

                # Navigate to Facebook
                print("NAVIGATING: Going to Facebook...")
                try:
                    page.goto("https://www.facebook.com/", wait_until="networkidle", timeout=30000)
                except:
                    page.goto("https://www.facebook.com/")
                    time.sleep(5)

                # Verify login
                print("VERIFYING: Checking Facebook login...")
                login_verified = self.verify_facebook_login(page)

                if not login_verified:
                    print("ERROR: Facebook login required. Please log in manually.")
                    print("TIP: The browser will stay open - log in and press Enter")
                    input("Press Enter after logging in...")

                # Wait longer for page load
                print("WAITING: For Facebook page to fully load...")
                time.sleep(5)

                # Try to scroll to ensure composer is visible
                print("SCROLLING: To ensure composer is visible...")
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(2)

                # Find post composer with updated selectors
                print("STEP 1: Finding post composer...")
                try:
                    composer_element, composer_selector = self.find_element_with_fallbacks(
                        page, self.post_selectors, "post composer"
                    )
                except Exception as e:
                    print(f"ERROR: {e}")
                    print("\n🔧 TROUBLESHOOTING:")
                    print("Facebook interface may have changed. Please:")
                    print("1. Look at the browser window")
                    print("2. Find the 'What's on your mind?' box")
                    print("3. Right-click → Inspect Element")
                    print("4. Share the HTML attributes with me")
                    browser.close()
                    return False

                # Click and enter content
                print("TYPING: Content into composer...")
                composer_element.click()
                time.sleep(2)

                # Clear and type content
                page.keyboard.press("Control+a")
                time.sleep(0.5)

                # Try different input methods
                try:
                    composer_element.fill(content)
                except:
                    # Fallback: type character by character
                    page.keyboard.type(content)

                time.sleep(3)

                # Find and click post button
                print("STEP 2: Finding post button...")
                try:
                    post_element, post_selector = self.find_element_with_fallbacks(
                        page, self.post_button_selectors, "post button"
                    )
                except Exception as e:
                    print(f"ERROR: {e}")
                    print("\n🔧 TROUBLESHOOTING:")
                    print("Post button not found. Please:")
                    print("1. Look for the 'Post' button in browser")
                    print("2. Right-click → Inspect Element")
                    print("3. Share the button's HTML attributes")
                    browser.close()
                    return False

                print("POSTING: Clicking post button...")
                post_element.click()

                # Wait for post to be published
                print("WAITING: For post to be published...")
                time.sleep(8)

                print("SUCCESS: Facebook post completed")
                browser.close()
                return True

        except Exception as e:
            print(f"ERROR: Facebook posting failed: {e}")
            try:
                browser.close()
            except:
                pass
            return False

    def verify_facebook_login(self, page):
        """Verify Facebook login status with updated selectors"""
        login_indicators = [
            '[data-testid="blue_bar_profile_link"]',
            '[aria-label="Account"]',
            '[data-testid="left_nav_menu_item"]',
            'div[role="banner"]',
            '[data-testid="nav-search-input"]',
            '.x1n2onr6',  # Updated Facebook class
            '[aria-label*="Facebook"]'
        ]

        for selector in login_indicators:
            try:
                element = page.wait_for_selector(selector, timeout=3000)
                if element and element.is_visible():
                    print("SUCCESS: Facebook login verified")
                    return True
            except:
                continue

        # Check if on login page
        try:
            login_form = page.query_selector('#email')
            if login_form:
                print("WARNING: Facebook login required")
                return False
        except:
            pass

        return False

    def parse_facebook_approval_file(self, file_path):
        """Parse Facebook approval file and extract content"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract proposed content
            content_match = re.search(r'## Proposed Content\s*(.+?)(?=##|\n---|\Z)', content, re.DOTALL)

            if content_match:
                facebook_content = content_match.group(1).strip()
                return {
                    'content': facebook_content
                }

            return None

        except Exception as e:
            print(f"ERROR: Error parsing Facebook approval file {file_path}: {e}")
            return None

    def process_approved_facebook_posts(self):
        """Process all approved Facebook posts in /Done folder"""
        # Look for Facebook post approval files
        facebook_files = list(self.done_path.glob('FACEBOOK_POST_*.md'))

        if not facebook_files:
            return

        print(f"FOUND: {len(facebook_files)} approved Facebook posts")

        for file_path in facebook_files:
            print(f"PROCESSING: {file_path.name}")

            # Parse approval file
            post_data = self.parse_facebook_approval_file(file_path)

            if post_data:
                # Use browser method with updated selectors
                print("ATTEMPTING: Browser automation method (UPDATED)...")
                success = self.post_to_facebook_browser(post_data['content'])

                if success:
                    # Move to archive
                    archive_file = self.archive_path / f"posted_{file_path.name}"
                    file_path.rename(archive_file)
                    print(f"SUCCESS: Facebook post published and archived: {archive_file.name}")

                    # Log analytics
                    self.log_facebook_analytics(post_data['content'])
                else:
                    print(f"ERROR: Failed to post Facebook content for: {file_path.name}")
            else:
                print(f"ERROR: Could not parse Facebook approval file: {file_path.name}")

    def log_facebook_analytics(self, content):
        """Log Facebook post for analytics tracking"""
        analytics_file = self.vault_path / "Facebook_Analytics" / f"{datetime.now().strftime('%Y-%m')}.json"
        analytics_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "status": "posted",
            "platform": "facebook",
            "engagement": "pending_tracking"
        }

        # Load existing analytics
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = []

        analytics.append(log_entry)

        # Save updated analytics
        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)

        print(f"ANALYTICS: Facebook analytics logged: {analytics_file}")

    def start_monitoring(self):
        """Start monitoring /Done folder for approved Facebook posts"""
        print("STARTING: Facebook Content Handler (UPDATED SELECTORS)...")
        print(f"MONITORING: {self.done_path}")
        print(f"SESSION: {self.session_path}")
        print("Press Ctrl+C to stop")

        while True:
            try:
                self.process_approved_facebook_posts()

                # Wait 30 seconds before next check
                time.sleep(30)

            except KeyboardInterrupt:
                print("\n🛑 Stopping Facebook Content Handler...")
                break
            except Exception as e:
                print(f"ERROR: Error in monitoring loop: {e}")
                time.sleep(60)

def main():
    vault_path = "AI_Employee_Vault"

    print("Facebook Content Handler (UPDATED SELECTORS) Starting...")
    print("=" * 60)

    handler = FacebookContentHandler(vault_path)
    handler.start_monitoring()

if __name__ == "__main__":
    main()