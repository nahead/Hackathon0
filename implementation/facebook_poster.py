#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Page Poster - Gold Tier Requirement
Posts to Facebook business page using Graph API
"""

import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
APPROVED_FOLDER = VAULT_PATH / "Approved"
DONE_FOLDER = VAULT_PATH / "Done"

FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
FACEBOOK_API_VERSION = os.getenv('FACEBOOK_GRAPH_API_VERSION', 'v18.0')

class FacebookPoster:
    """Post to Facebook business page"""

    def __init__(self):
        self.access_token = FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.api_version = FACEBOOK_API_VERSION
        self.api_base = f"https://graph.facebook.com/{self.api_version}"

    def check_credentials(self):
        """Check if credentials are configured"""
        if not self.access_token or self.access_token == 'your_page_access_token_here':
            print("[ERROR] FACEBOOK_PAGE_ACCESS_TOKEN not configured in .env")
            return False

        if not self.page_id or self.page_id == 'your_page_id_here':
            print("[ERROR] FACEBOOK_PAGE_ID not configured in .env")
            return False

        return True

    def verify_token(self):
        """Verify access token is valid"""
        url = f"{self.api_base}/me"
        params = {'access_token': self.access_token}

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Authenticated as: {data.get('name', 'Unknown')}")
                return True
            else:
                print(f"[ERROR] Authentication failed: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Could not verify token: {e}")
            return False

    def post_to_facebook(self, message):
        """Post message to Facebook page"""
        url = f"{self.api_base}/{self.page_id}/feed"

        data = {
            'message': message,
            'access_token': self.access_token
        }

        try:
            print("[API] Posting to Facebook...")
            response = requests.post(url, data=data, timeout=30)

            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id', 'unknown')
                print("[OK] ✅ Post published successfully!")
                print(f"[INFO] Post ID: {post_id}")
                return True
            else:
                print(f"[ERROR] ❌ Post failed: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Exception while posting: {e}")
            return False

    def process_approved_posts(self):
        """Process all approved Facebook posts"""

        if not APPROVED_FOLDER.exists():
            print(f"[ERROR] Approved folder not found: {APPROVED_FOLDER}")
            return

        # Find Facebook posts
        facebook_posts = list(APPROVED_FOLDER.glob("FACEBOOK_POST_*.md"))

        if not facebook_posts:
            print("[INFO] No approved Facebook posts found")
            return

        print(f"\n[FOUND] {len(facebook_posts)} approved post(s)")

        success_count = 0
        fail_count = 0

        for post_file in facebook_posts:
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

                # Post to Facebook
                success = self.post_to_facebook(post_text)

                if success:
                    # Move to Done folder
                    DONE_FOLDER.mkdir(exist_ok=True)
                    done_path = DONE_FOLDER / post_file.name
                    post_file.rename(done_path)
                    print(f"\n[SUCCESS] ✅ Posted and moved to Done")
                    success_count += 1
                else:
                    print(f"\n[FAILED] ❌ Could not post")
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
    print("FACEBOOK PAGE POSTER - GOLD TIER")
    print("="*70)

    print(f"\n[CONFIG] Vault path: {VAULT_PATH}")

    # Create poster instance
    poster = FacebookPoster()

    # Check credentials
    print("\n[STEP 1] Checking credentials...")
    if not poster.check_credentials():
        print("\n[ERROR] Facebook credentials not configured")
        print("\n[SETUP] To configure:")
        print("  1. Create Facebook App at https://developers.facebook.com")
        print("  2. Get Page Access Token")
        print("  3. Add to .env file:")
        print("     FACEBOOK_PAGE_ACCESS_TOKEN=your_token")
        print("     FACEBOOK_PAGE_ID=your_page_id")
        return

    # Verify token
    print("\n[STEP 2] Verifying access token...")
    if not poster.verify_token():
        print("\n[ERROR] Access token is invalid or expired")
        print("[INFO] Get a new token from Facebook Developer Console")
        return

    # Process approved posts
    print("\n[STEP 3] Processing approved posts...")
    poster.process_approved_posts()

    print("\n" + "="*70)
    print("[DONE] Facebook posting complete")
    print("="*70)

if __name__ == "__main__":
    main()
