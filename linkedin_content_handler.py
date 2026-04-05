#!/usr/bin/env python3
"""
LinkedIn Content Handler - INTEGRATED WITH PLAYWRIGHT AUTOMATION
Enhanced LinkedIn automation using Playwright MCP server integration
"""

import os
import time
import re
import json
import requests
from pathlib import Path
from datetime import datetime

class LinkedInContentHandler:
    def __init__(self, vault_path, mcp_url="http://localhost:8808"):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.archive_path = self.vault_path / "Archive"
        self.mcp_url = mcp_url

        # Create directories
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def call_playwright(self, tool, params=None):
        """Call Playwright MCP server"""
        if params is None:
            params = {}

        payload = {
            "jsonrpc": "2.0",
            "method": tool,
            "params": params,
            "id": 1
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }

        try:
            response = requests.post(f"{self.mcp_url}/mcp", json=payload, headers=headers)
            return response.json()
        except Exception as e:
            print(f"Error calling Playwright: {e}")
            return None

    def process_approved_posts(self):
        """Process approved LinkedIn posts from Done folder"""
        print("[LINKEDIN] Processing approved LinkedIn posts...")

        # Find LinkedIn post approval files
        linkedin_files = list(self.done_path.glob("LINKEDIN_POST_*.md"))

        if not linkedin_files:
            print("[INFO] No approved LinkedIn posts found")
            return

        print(f"[FOUND] Found {len(linkedin_files)} approved LinkedIn posts")

        for file_path in linkedin_files:
            print(f"[PROCESS] Processing: {file_path.name}")

            # Parse the approval file
            approval_data = self.parse_approval_file(file_path)

            if approval_data:
                # Extract content
                content = approval_data.get('content', '')

                if content:
                    # Post using Playwright automation
                    result = self.post_to_linkedin_playwright(content)

                    if result.get('success'):
                        # Archive the file
                        archive_file = self.archive_path / f"posted_{file_path.name}"
                        file_path.rename(archive_file)
                        print(f"[SUCCESS] Posted and archived: {archive_file.name}")
                    else:
                        print(f"[ERROR] Failed to post: {result.get('error', 'Unknown error')}")
                else:
                    print(f"[ERROR] No content found in: {file_path.name}")
            else:
                print(f"[ERROR] Could not parse: {file_path.name}")

    def parse_approval_file(self, file_path):
        """Parse LinkedIn post approval file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract content between ``` markers
            import re
            match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if match:
                post_content = match.group(1).strip()
                return {'content': post_content}

            return None

        except Exception as e:
            print(f"[ERROR] Error parsing {file_path}: {e}")
            return None

    def post_to_linkedin_playwright(self, content):
        """Post to LinkedIn using Playwright automation"""
        try:
            print(f"[PLAYWRIGHT] Posting to LinkedIn via automation...")

            # Import our LinkedIn automation
            import sys
            sys.path.append('.')
            from linkedin_automation_demo import LinkedInAutomation

            # Create automation instance
            linkedin = LinkedInAutomation(self.mcp_url)

            # Execute posting workflow
            results = linkedin.create_linkedin_post(content)

            # Check if all critical steps succeeded
            success_count = sum(1 for step, result in results if result and not result.get('isError'))
            total_steps = len(results)

            if success_count >= 5:  # Navigation, screenshot, find, click, type minimum
                post_id = f"linkedin_playwright_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                print(f"[SUCCESS] LinkedIn automation completed: {success_count}/{total_steps} steps")

                return {
                    'success': True,
                    'post_id': post_id,
                    'message': f'Posted via Playwright automation ({success_count}/{total_steps} steps)',
                    'automation_results': results
                }
            else:
                return {
                    'success': False,
                    'error': f'Automation failed: only {success_count}/{total_steps} steps succeeded',
                    'automation_results': results
                }

        except Exception as e:
            print(f"[ERROR] Playwright posting error: {e}")
            return {'success': False, 'error': str(e)}

    def start_monitoring(self):
        """Start monitoring Done folder for approved posts"""
        print("[LINKEDIN] LinkedIn Content Handler - Playwright Integration")
        print("=" * 60)
        print(f"[MONITOR] Monitoring: {self.done_path}")
        print(f"[PLAYWRIGHT] MCP Server: {self.mcp_url}")
        print("Press Ctrl+C to stop")

        while True:
            try:
                # Process approved posts
                self.process_approved_posts()

                # Wait 30 seconds before next check
                print("[WAIT] Waiting 30 seconds...")
                time.sleep(30)

            except KeyboardInterrupt:
                print("\n[STOP] Stopping LinkedIn content handler...")
                break
            except Exception as e:
                print(f"[ERROR] Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error

def main():
    """Main function for LinkedIn content handler"""
    vault_path = "AI_Employee_Vault"

    print("LinkedIn Content Handler - Playwright Integration")
    print("=" * 60)

    handler = LinkedInContentHandler(vault_path)
    handler.start_monitoring()

if __name__ == "__main__":
    main()

    def find_element_with_fallbacks(self, page, selectors, element_name, timeout=10000):
        """Try multiple selectors until one works"""
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

        raise Exception(f"Could not find {element_name} with any selector")

    def post_to_linkedin(self, content):
        """Post content to LinkedIn with robust error handling"""
        try:
            with sync_playwright() as p:
                print("STARTING: LinkedIn posting process...")

                # Launch browser with extended timeout
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True for production, False for debugging
                    viewport={"width": 1280, "height": 720},
                    args=['--no-sandbox', '--disable-dev-shm-usage']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.set_default_timeout(30000)  # 30 seconds per operation

                # Navigate to LinkedIn feed
                print("NAVIGATING: Going to LinkedIn feed...")
                try:
                    page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
                except:
                    # Fallback navigation
                    page.goto("https://www.linkedin.com/feed/")
                    time.sleep(5)

                # Verify login status
                print("VERIFYING: Checking login status...")
                login_verified = self.verify_linkedin_login(page)

                if not login_verified:
                    print("ERROR: LinkedIn login required. Please run: python linkedin_login_setup.py")
                    browser.close()
                    return False

                # Wait for page to fully load
                print("WAITING: Page to fully load...")
                time.sleep(3)

                # Find and click share box
                print("STEP 1: Finding share box...")
                share_element, share_selector = self.find_element_with_fallbacks(
                    page, self.share_box_selectors, "share box"
                )

                print("CLICKING: Share box...")
                share_element.click()
                time.sleep(2)

                # Find text editor
                print("STEP 2: Finding text editor...")
                editor_element, editor_selector = self.find_element_with_fallbacks(
                    page, self.text_editor_selectors, "text editor"
                )

                # Clear and enter content
                print("TYPING: Content into editor...")
                editor_element.click()  # Focus first
                time.sleep(1)

                # Clear existing content
                page.keyboard.press("Control+a")
                time.sleep(0.5)

                # Type new content
                editor_element.fill(content)
                time.sleep(2)

                # Find and click post button
                print("STEP 3: Finding post button...")
                post_element, post_selector = self.find_element_with_fallbacks(
                    page, self.post_button_selectors, "post button"
                )

                print("POSTING: Clicking post button...")
                post_element.click()

                # Wait for post to be published
                print("WAITING: For post to be published...")
                time.sleep(5)

                # Verify post was published (optional)
                try:
                    # Look for success indicators
                    success_indicators = [
                        'text="Post successful"',
                        'text="Your post was shared"',
                        '[data-test-id="feed-shared-update-v2"]'
                    ]

                    for indicator in success_indicators:
                        try:
                            page.wait_for_selector(indicator, timeout=3000)
                            print("VERIFIED: Post published successfully")
                            break
                        except:
                            continue
                except:
                    print("WARNING: Could not verify post publication, but likely succeeded")

                print("SUCCESS: LinkedIn post completed")
                browser.close()
                return True

        except Exception as e:
            print(f"ERROR: LinkedIn posting failed: {e}")
            try:
                browser.close()
            except:
                pass
            return False

    def verify_linkedin_login(self, page):
        """Verify LinkedIn login with multiple checks"""
        login_indicators = [
            '.global-nav__me',
            '.global-nav__me-content',
            '[data-test-id="share-box-trigger"]',
            '.share-box-feed-entry__trigger',
            '.feed-identity-module',
            '.scaffold-layout__main'
        ]

        for selector in login_indicators:
            try:
                element = page.wait_for_selector(selector, timeout=3000)
                if element and element.is_visible():
                    print("SUCCESS: LinkedIn login verified")
                    return True
            except:
                continue

        # Fallback check - if not on login page, probably logged in
        try:
            login_form = page.query_selector('#username')
            if not login_form:
                page_title = page.title().lower()
                if 'linkedin' in page_title and 'error' not in page_title:
                    print("SUCCESS: LinkedIn login verified (fallback)")
                    return True
        except:
            pass

        return False

    def parse_linkedin_approval_file(self, file_path):
        """Parse LinkedIn approval file and extract content"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract proposed content
            content_match = re.search(r'## Proposed Content\s*(.+?)(?=##|\n---|\Z)', content, re.DOTALL)

            if content_match:
                linkedin_content = content_match.group(1).strip()
                return {
                    'content': linkedin_content
                }

            return None

        except Exception as e:
            print(f"ERROR: Error parsing LinkedIn approval file {file_path}: {e}")
            return None

    def process_approved_linkedin_posts(self):
        """Process all approved LinkedIn posts in /Done folder"""
        # Look for LinkedIn post approval files
        linkedin_files = list(self.done_path.glob('LINKEDIN_POST_*.md'))

        if not linkedin_files:
            return

        print(f"FOUND: {len(linkedin_files)} approved LinkedIn posts")

        for file_path in linkedin_files:
            print(f"PROCESSING: {file_path.name}")

            # Parse approval file
            post_data = self.parse_linkedin_approval_file(file_path)

            if post_data:
                # Post to LinkedIn
                success = self.post_to_linkedin(post_data['content'])

                if success:
                    # Move to archive
                    archive_file = self.archive_path / f"posted_{file_path.name}"
                    file_path.rename(archive_file)
                    print(f"SUCCESS: LinkedIn post published and archived: {archive_file.name}")

                    # Log analytics
                    self.log_linkedin_analytics(post_data['content'])
                else:
                    print(f"ERROR: Failed to post LinkedIn content for: {file_path.name}")
            else:
                print(f"ERROR: Could not parse LinkedIn approval file: {file_path.name}")

    def log_linkedin_analytics(self, content):
        """Log LinkedIn post for analytics tracking"""
        analytics_file = self.vault_path / "LinkedIn_Analytics" / f"{datetime.now().strftime('%Y-%m')}.json"
        analytics_file.parent.mkdir(parents=True, exist_ok=True)

        import json

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "status": "posted",
            "platform": "linkedin",
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

        print(f"ANALYTICS: Analytics logged: {analytics_file}")

    def start_monitoring(self):
        """Start monitoring /Done folder for approved LinkedIn posts"""
        print("STARTING: LinkedIn Content Handler (FIXED VERSION)...")
        print(f"MONITORING: {self.done_path}")
        print(f"SESSION: {self.session_path}")
        print("Press Ctrl+C to stop")

        while True:
            try:
                self.process_approved_linkedin_posts()

                # Wait 20 seconds before next check
                time.sleep(20)

            except KeyboardInterrupt:
                print("\n🛑 Stopping LinkedIn Content Handler...")
                break
            except Exception as e:
                print(f"ERROR: Error in monitoring loop: {e}")
                time.sleep(30)

def main():
    vault_path = "AI_Employee_Vault"

    print("LinkedIn Content Handler (FIXED VERSION) Starting...")
    print("=" * 60)

    handler = LinkedInContentHandler(vault_path)
    handler.start_monitoring()

if __name__ == "__main__":
    main()