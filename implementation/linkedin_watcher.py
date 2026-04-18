#!/usr/bin/env python3
"""
LinkedIn Post Watcher - Monitors Approved/ folder and auto-posts to LinkedIn
Runs continuously, checking every 60 seconds for new posts
"""

import os
import time
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInWatcher:
    def __init__(self):
        self.vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
        self.approved_path = self.vault_path / "Approved"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"

        # LinkedIn credentials
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.person_urn = os.getenv('LINKEDIN_PERSON_URN', '')

        # Ensure directories exist
        self.approved_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        self.log(f"✅ LinkedIn Watcher initialized")
        self.log(f"📁 Watching: {self.approved_path}")
        self.log(f"🔑 LinkedIn configured: {bool(self.access_token and self.person_urn)}")

    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"

        # Print to console (ASCII-safe for Windows)
        try:
            print(log_message)
        except UnicodeEncodeError:
            # Fallback: remove emojis for console
            ascii_message = log_message.encode('ascii', 'ignore').decode('ascii')
            print(ascii_message)

        # Write to log file with full UTF-8 support
        log_file = self.logs_path / f"linkedin_watcher_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')

    def extract_post_content(self, file_path):
        """Extract post content from markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove frontmatter if present
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            return content
        except Exception as e:
            self.log(f"❌ Error reading {file_path.name}: {e}")
            return None

    def post_to_linkedin(self, content):
        """Post content to LinkedIn"""
        if not self.access_token or not self.person_urn:
            self.log("❌ LinkedIn credentials not configured")
            return None

        url = "https://api.linkedin.com/v2/ugcPosts"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        payload = {
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
            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 201:
                post_id = response.headers.get('X-RestLi-Id', 'unknown')
                self.log(f"✅ Posted to LinkedIn successfully! Post ID: {post_id}")
                return post_id
            else:
                self.log(f"❌ LinkedIn API error: {response.status_code}")
                self.log(f"Response: {response.text}")
                return None

        except Exception as e:
            self.log(f"❌ Error posting to LinkedIn: {e}")
            return None

    def process_approved_posts(self):
        """Check Approved/ folder and post any LinkedIn posts"""
        try:
            # Find all LinkedIn post files
            linkedin_posts = list(self.approved_path.glob("LINKEDIN_POST_*.md"))

            if not linkedin_posts:
                return 0

            self.log(f"📋 Found {len(linkedin_posts)} LinkedIn post(s) to process")

            posted_count = 0
            for post_file in linkedin_posts:
                self.log(f"📝 Processing: {post_file.name}")

                # Extract content
                content = self.extract_post_content(post_file)
                if not content:
                    continue

                # Post to LinkedIn
                post_id = self.post_to_linkedin(content)

                if post_id:
                    # Move to Done/
                    done_file = self.done_path / post_file.name
                    post_file.rename(done_file)
                    self.log(f"✅ Moved {post_file.name} to Done/")
                    posted_count += 1
                else:
                    self.log(f"⚠️ Failed to post {post_file.name}, keeping in Approved/")

            return posted_count

        except Exception as e:
            self.log(f"❌ Error processing posts: {e}")
            return 0

    def run(self):
        """Main loop - check every 60 seconds"""
        self.log("🚀 LinkedIn Watcher started - checking every 60 seconds")
        self.log("Press Ctrl+C to stop")

        check_count = 0

        try:
            while True:
                check_count += 1
                self.log(f"🔍 Check #{check_count} - Scanning Approved/ folder...")

                posted = self.process_approved_posts()

                if posted > 0:
                    self.log(f"✅ Posted {posted} LinkedIn post(s)")
                else:
                    self.log("💤 No posts to process")

                self.log(f"⏰ Next check in 60 seconds...")
                time.sleep(60)

        except KeyboardInterrupt:
            self.log("\n👋 LinkedIn Watcher stopped by user")
        except Exception as e:
            self.log(f"❌ Fatal error: {e}")
            raise

if __name__ == "__main__":
    watcher = LinkedInWatcher()
    watcher.run()
