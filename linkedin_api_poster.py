#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn API Poster - Silver Tier Requirement
Posts to LinkedIn using official API (OAuth)
More reliable than Playwright automation
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding
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

LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN', '')

class LinkedInAPIPoster:
    """Post to LinkedIn using official API"""

    def __init__(self):
        self.access_token = LINKEDIN_ACCESS_TOKEN
        self.person_urn = LINKEDIN_PERSON_URN
        self.api_base = "https://api.linkedin.com/v2"

    def check_credentials(self):
        """Check if credentials are configured"""
        if not self.access_token or self.access_token == 'your_access_token_here':
            print("[ERROR] LINKEDIN_ACCESS_TOKEN not configured in .env")
            return False

        if not self.person_urn or self.person_urn == 'your_person_id_here':
            print("[ERROR] LINKEDIN_PERSON_URN not configured in .env")
            return False

        return True

    def get_user_info(self):
        """Get user info to verify token"""
        url = f"{self.api_base}/userinfo"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Authenticated as: {data.get('name', 'Unknown')}")
                return data
            else:
                print(f"[ERROR] Authentication failed: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return None

        except Exception as e:
            print(f"[ERROR] Could not verify token: {e}")
            return None

    def post_to_linkedin(self, content):
        """Post content to LinkedIn using API"""

        url = f"{self.api_base}/ugcPosts"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Prepare post data
        post_data = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        try:
            print("[API] Posting to LinkedIn...")
            response = requests.post(
                url,
                headers=headers,
                json=post_data,
                timeout=30
            )

            if response.status_code == 201:
                print("[OK] ✅ Post published successfully!")
                post_id = response.headers.get('X-RestLi-Id', 'unknown')
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
    print("LINKEDIN API POSTER - SILVER TIER")
    print("="*70)

    print(f"\n[CONFIG] Vault path: {VAULT_PATH}")

    # Create poster instance
    poster = LinkedInAPIPoster()

    # Check credentials
    print("\n[STEP 1] Checking credentials...")
    if not poster.check_credentials():
        print("\n[ERROR] LinkedIn API credentials not configured")
        print("\n[SETUP] To configure:")
        print("  1. Run: python setup_linkedin_oauth.py")
        print("  2. Follow the OAuth flow")
        print("  3. Add credentials to .env file:")
        print("     LINKEDIN_ACCESS_TOKEN=your_token")
        print("     LINKEDIN_PERSON_URN=urn:li:person:your_id")
        print("\n[GUIDE] See: LINKEDIN_SETUP_GUIDE.md")
        return

    # Verify token
    print("\n[STEP 2] Verifying access token...")
    user_info = poster.get_user_info()
    if not user_info:
        print("\n[ERROR] Access token is invalid or expired")
        print("[INFO] Run: python setup_linkedin_oauth.py")
        print("[INFO] to get a new token")
        return

    # Process approved posts
    print("\n[STEP 3] Processing approved posts...")
    poster.process_approved_posts()

    print("\n" + "="*70)
    print("[DONE] LinkedIn API posting complete")
    print("="*70)

if __name__ == "__main__":
    main()
