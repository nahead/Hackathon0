#!/usr/bin/env python3
"""
Twitter API Handler - Official API-based Twitter automation
No browser automation - uses official Twitter API v2
"""

import os
import time
import re
import json
from pathlib import Path
from datetime import datetime
import requests
from requests_oauthlib import OAuth1Session

class TwitterAPIHandler:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.archive_path = self.vault_path / "Archive"
        self.failed_path = self.vault_path / "Failed"

        # Create directories
        for path in [self.archive_path, self.failed_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Load Twitter API credentials from environment
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        # Validate credentials
        self._validate_credentials()

        # Setup OAuth1 session for API v1.1 (posting)
        self.oauth = OAuth1Session(
            self.api_key,
            client_secret=self.api_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret,
        )

    def _validate_credentials(self):
        """Validate Twitter API credentials"""
        missing_creds = []

        if not self.api_key:
            missing_creds.append('TWITTER_API_KEY')
        if not self.api_secret:
            missing_creds.append('TWITTER_API_SECRET')
        if not self.access_token:
            missing_creds.append('TWITTER_ACCESS_TOKEN')
        if not self.access_token_secret:
            missing_creds.append('TWITTER_ACCESS_TOKEN_SECRET')
        if not self.bearer_token:
            missing_creds.append('TWITTER_BEARER_TOKEN')

        if missing_creds:
            print("ERROR: Missing Twitter API credentials:")
            for cred in missing_creds:
                print(f"   - {cred}")
            print("\nPlease add these to your .env file:")
            print("TWITTER_API_KEY=your_api_key")
            print("TWITTER_API_SECRET=your_api_secret")
            print("TWITTER_ACCESS_TOKEN=your_access_token")
            print("TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret")
            print("TWITTER_BEARER_TOKEN=your_bearer_token")
            raise ValueError("Missing Twitter API credentials")

        print("OK: Twitter API credentials loaded")

    def test_api_connection(self):
        """Test Twitter API connection"""
        try:
            # Test with a simple API call to verify credentials
            url = "https://api.twitter.com/1.1/account/verify_credentials.json"
            response = self.oauth.get(url)

            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('screen_name', 'Unknown')
                print(f"SUCCESS: Twitter API connection successful!")
                print(f"📱 Connected as: @{username}")
                return True
            else:
                print(f"ERROR: Twitter API connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"ERROR: Twitter API test failed: {e}")
            return False

    def post_tweet(self, content):
        """Post tweet using Twitter API"""
        try:
            # Validate content length
            if len(content) > 280:
                print(f"ERROR: Tweet too long: {len(content)} characters (max 280)")
                return False

            print(f"POSTING: Posting tweet ({len(content)} characters)...")
            print(f"Content: {content[:50]}...")

            # Post tweet using API v1.1
            url = "https://api.twitter.com/1.1/statuses/update.json"
            payload = {"status": content}

            response = self.oauth.post(url, data=payload)

            if response.status_code == 200:
                tweet_data = response.json()
                tweet_id = tweet_data.get('id_str')
                tweet_url = f"https://twitter.com/i/status/{tweet_id}"

                print("SUCCESS: Tweet posted successfully!")
                print(f"🔗 Tweet URL: {tweet_url}")
                print(f"ANALYTICS: Tweet ID: {tweet_id}")

                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url,
                    'response': tweet_data
                }

            else:
                print(f"ERROR: Tweet posting failed: {response.status_code}")
                print(f"Response: {response.text}")
                return {'success': False, 'error': response.text}

        except Exception as e:
            print(f"ERROR: Error posting tweet: {e}")
            return {'success': False, 'error': str(e)}

    def process_approved_tweets(self):
        """Process approved tweets using Twitter API"""
        twitter_files = list(self.done_path.glob('TWITTER_POST_*.md'))

        if not twitter_files:
            return

        print(f"FOUND: {len(twitter_files)} approved Twitter posts")

        for file_path in twitter_files:
            print(f"\nPROCESSING: {file_path.name}")

            # Parse file
            tweet_data = self._parse_twitter_file(file_path)

            if not tweet_data:
                print(f"ERROR: Could not parse file: {file_path.name}")
                failed_file = self.failed_path / f"parse_error_{file_path.name}"
                file_path.rename(failed_file)
                continue

            # Post tweet via API
            result = self.post_tweet(tweet_data['content'])

            if result.get('success'):
                # Archive successful post
                archive_file = self.archive_path / f"api_posted_{file_path.name}"
                file_path.rename(archive_file)
                print(f"SUCCESS: Tweet posted and archived: {archive_file.name}")

                # Log analytics
                self._log_tweet_analytics(tweet_data['content'], result)

            else:
                # Move to failed folder
                failed_file = self.failed_path / f"api_failed_{file_path.name}"
                file_path.rename(failed_file)
                print(f"ERROR: Tweet failed, moved to: {failed_file.name}")

    def _parse_twitter_file(self, file_path):
        """Parse Twitter approval file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            content_match = re.search(r'## Proposed Content\s*```\s*(.+?)\s*```', content, re.DOTALL)

            if content_match:
                return {'content': content_match.group(1).strip()}
            return None

        except Exception as e:
            print(f"ERROR: Error parsing file: {e}")
            return None

    def _log_tweet_analytics(self, content, result):
        """Log tweet analytics"""
        analytics_file = self.vault_path / "Twitter_Analytics" / f"{datetime.now().strftime('%Y-%m')}.json"
        analytics_file.parent.mkdir(parents=True, exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "character_count": len(content),
            "tweet_id": result.get('tweet_id'),
            "tweet_url": result.get('tweet_url'),
            "status": "posted_via_api",
            "method": "twitter_api_v1.1"
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
        """Start monitoring for approved Twitter posts"""
        print("STARTING: Twitter API Handler Starting...")
        print(f"📁 Monitoring: {self.done_path}")
        print(f"📁 Archive: {self.archive_path}")
        print(f"📁 Failed: {self.failed_path}")
        print("Press Ctrl+C to stop")

        # Test API connection on startup
        if not self.test_api_connection():
            print("ERROR: Cannot start - API connection failed")
            return

        while True:
            try:
                self.process_approved_tweets()
                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                print("\n🛑 Stopping Twitter API Handler...")
                break
            except Exception as e:
                print(f"ERROR: Error in monitoring: {e}")
                time.sleep(60)

def main():
    print("Twitter API Handler")
    print("=" * 30)
    print("Official Twitter API integration - No browser automation!")
    print()

    try:
        handler = TwitterAPIHandler("AI_Employee_Vault")
        handler.start_monitoring()
    except ValueError as e:
        print(f"ERROR: Setup error: {e}")
        print("\nPlease configure Twitter API credentials first")

if __name__ == "__main__":
    main()