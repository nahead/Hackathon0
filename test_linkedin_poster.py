#!/usr/bin/env python3
"""
Test LinkedIn Posting
Tests posting content to LinkedIn (requires LinkedIn API credentials)
"""

import os
import requests
from datetime import datetime
from pathlib import Path

def test_linkedin_api():
    """Test LinkedIn API connection"""
    print("🔍 Testing LinkedIn API Connection...")

    # Get credentials from environment
    linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if not linkedin_access_token:
        print("❌ ERROR: LINKEDIN_ACCESS_TOKEN environment variable not set")
        print("\nTo get LinkedIn API access:")
        print("1. Go to: https://www.linkedin.com/developers/")
        print("2. Create an app")
        print("3. Get OAuth 2.0 access token")
        print("4. Set: export LINKEDIN_ACCESS_TOKEN='your_token'")
        return False

    try:
        # Test API connection by getting user profile
        url = "https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {linkedin_access_token}",
            "Content-Type": "application/json"
        }

        print("\n📡 Testing API connection...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Connected to LinkedIn API")
            print(f"   User ID: {user_data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ API connection failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def post_to_linkedin(content, dry_run=True):
    """Post content to LinkedIn"""
    print("\n🔍 Testing LinkedIn Posting...")

    if dry_run:
        print("⚠️ DRY RUN MODE - No actual posting")
        print("\nContent to be posted:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        print("\n✅ Dry run successful - content validated")
        return True

    linkedin_access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    linkedin_person_urn = os.getenv('LINKEDIN_PERSON_URN')

    if not linkedin_access_token or not linkedin_person_urn:
        print("❌ ERROR: Missing LinkedIn credentials")
        print("   Required: LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN")
        return False

    try:
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        post_data = {
            "author": linkedin_person_urn,
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

        print("\n📤 Posting to LinkedIn...")
        response = requests.post(url, headers=headers, json=post_data, timeout=10)

        if response.status_code == 201:
            result = response.json()
            print(f"✅ Posted successfully!")
            print(f"   Post ID: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Posting failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def process_approved_posts():
    """Process approved LinkedIn posts"""
    print("\n🔍 Checking for Approved Posts...")

    approved_path = Path("AI_Employee_Vault/Approved")
    if not approved_path.exists():
        print("⚠️ No Approved folder found")
        return []

    # Find approved LinkedIn posts
    approved_posts = list(approved_path.glob("LINKEDIN_POST_*.md"))

    if not approved_posts:
        print("ℹ️ No approved LinkedIn posts found")
        print("\nTo approve a post:")
        print("1. Run: python test_linkedin_content.py")
        print("2. Move a file from Pending_Approval/ to Approved/")
        return []

    print(f"📬 Found {len(approved_posts)} approved post(s)")

    posts_to_publish = []
    for post_file in approved_posts:
        content = post_file.read_text(encoding='utf-8')

        # Extract content between ``` markers
        if '```' in content:
            parts = content.split('```')
            if len(parts) >= 3:
                post_content = parts[1].strip()
                posts_to_publish.append({
                    'file': post_file,
                    'content': post_content
                })
                print(f"   ✅ {post_file.name}")

    return posts_to_publish

if __name__ == "__main__":
    print("=" * 60)
    print("LINKEDIN POSTING TEST")
    print("=" * 60)

    # Check for dry run mode
    dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    if dry_run:
        print("\n⚠️ RUNNING IN DRY RUN MODE")
        print("   Set DRY_RUN=false to post for real")
    else:
        print("\n🚨 LIVE POSTING MODE")
        print("   Posts will be published to LinkedIn!")

    # Test API connection (skip in dry run)
    if not dry_run:
        if not test_linkedin_api():
            print("\n❌ API connection failed, exiting")
            exit(1)

    # Process approved posts
    posts = process_approved_posts()

    if posts:
        print(f"\n📤 Processing {len(posts)} post(s)...")

        for i, post in enumerate(posts, 1):
            print(f"\n--- POST {i}/{len(posts)} ---")
            success = post_to_linkedin(post['content'], dry_run=dry_run)

            if success and not dry_run:
                # Move to Done folder
                done_path = Path("AI_Employee_Vault/Done")
                done_path.mkdir(parents=True, exist_ok=True)
                post['file'].rename(done_path / post['file'].name)
                print(f"   ✅ Moved to Done: {post['file'].name}")

        print("\n" + "=" * 60)
        print("✅ POSTING TEST COMPLETE")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ℹ️ NO POSTS TO PROCESS")
        print("\nRun: python test_linkedin_content.py first")
        print("=" * 60)
