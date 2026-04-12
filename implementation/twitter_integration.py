#!/usr/bin/env python3
"""
Twitter (X) Integration for AI Employee
Post tweets and generate activity summaries
"""

import os
import sys
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TwitterIntegration')

# Twitter API Configuration
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"

class TwitterManager:
    """Manage Twitter posting and analytics"""

    def __init__(self):
        self.api_key = TWITTER_API_KEY
        self.api_secret = TWITTER_API_SECRET
        self.access_token = TWITTER_ACCESS_TOKEN
        self.access_secret = TWITTER_ACCESS_SECRET
        self.bearer_token = TWITTER_BEARER_TOKEN

        # Twitter API v2 endpoint
        self.api_url = "https://api.twitter.com/2/tweets"

    def post_tweet(self, content, media_ids=None):
        """Post a tweet using Twitter API v2"""
        if not self.bearer_token:
            logger.error("❌ Twitter Bearer Token not configured")
            return None

        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'text': content
        }

        if media_ids:
            payload['media'] = {'media_ids': media_ids}

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 201:
                result = response.json()
                tweet_id = result['data']['id']
                logger.info(f"✅ Tweet posted successfully: {tweet_id}")
                return tweet_id
            else:
                logger.error(f"❌ Failed to post tweet: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error posting tweet: {e}")
            return None

    def get_user_tweets(self, user_id, max_results=10):
        """Get recent tweets from user"""
        if not self.bearer_token:
            logger.error("❌ Twitter Bearer Token not configured")
            return []

        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }

        params = {
            'max_results': max_results,
            'tweet.fields': 'created_at,public_metrics'
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"❌ Failed to fetch tweets: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Error fetching tweets: {e}")
            return []

    def generate_summary(self, tweets):
        """Generate summary of Twitter activity"""
        if not tweets:
            return "No recent Twitter activity"

        total_tweets = len(tweets)
        total_likes = sum(t.get('public_metrics', {}).get('like_count', 0) for t in tweets)
        total_retweets = sum(t.get('public_metrics', {}).get('retweet_count', 0) for t in tweets)
        total_replies = sum(t.get('public_metrics', {}).get('reply_count', 0) for t in tweets)

        summary = f"""## Twitter Activity Summary

**Period:** Last {total_tweets} tweets
**Total Engagement:** {total_likes + total_retweets + total_replies}

### Metrics:
- 👍 Likes: {total_likes}
- 🔄 Retweets: {total_retweets}
- 💬 Replies: {total_replies}

### Top Performing Tweet:
"""
        # Find top tweet by engagement
        if tweets:
            top_tweet = max(tweets, key=lambda t: sum(t.get('public_metrics', {}).values()))
            summary += f"- {top_tweet.get('text', '')[:100]}...\n"
            summary += f"- Engagement: {sum(top_tweet.get('public_metrics', {}).values())}\n"

        return summary

def process_twitter_posts():
    """Process approved Twitter posts from vault"""
    logger.info("🐦 Processing Twitter posts...")

    twitter = TwitterManager()
    processed_count = 0

    # Find approved Twitter posts
    twitter_files = list(APPROVED_PATH.glob("TWITTER_POST_*.md"))

    for post_file in twitter_files:
        try:
            content = post_file.read_text(encoding='utf-8')

            # Extract tweet content (after frontmatter)
            if '---' in content:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    tweet_content = parts[2].strip()

                    # Remove markdown headers and formatting
                    tweet_content = tweet_content.replace('## Tweet Content', '').strip()
                    tweet_content = tweet_content.split('\n\n')[0]  # First paragraph

                    # Post tweet
                    tweet_id = twitter.post_tweet(tweet_content)

                    if tweet_id:
                        # Log success
                        log_twitter_post(post_file.name, tweet_id, tweet_content)

                        # Move to Done
                        done_file = DONE_PATH / post_file.name
                        post_file.rename(done_file)

                        processed_count += 1
                        logger.info(f"✅ Posted and moved to Done: {post_file.name}")

        except Exception as e:
            logger.error(f"❌ Error processing {post_file.name}: {e}")

    logger.info(f"✅ Processed {processed_count} Twitter posts")
    return processed_count

def log_twitter_post(filename, tweet_id, content):
    """Log Twitter post to audit trail"""
    LOGS_PATH.mkdir(exist_ok=True)

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': 'twitter_post',
        'filename': filename,
        'tweet_id': tweet_id,
        'content_preview': content[:100],
        'status': 'success'
    }

    log_file = LOGS_PATH / f"twitter_{datetime.now().strftime('%Y%m%d')}.json"

    try:
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    except Exception as e:
        logger.error(f"Error logging Twitter post: {e}")

def generate_twitter_summary():
    """Generate Twitter activity summary"""
    logger.info("📊 Generating Twitter summary...")

    twitter = TwitterManager()

    # Get user ID (you'll need to set this)
    user_id = os.getenv('TWITTER_USER_ID', '')

    if not user_id:
        logger.warning("⚠️ TWITTER_USER_ID not set, skipping summary")
        return

    tweets = twitter.get_user_tweets(user_id)
    summary = twitter.generate_summary(tweets)

    # Save summary to vault
    summary_file = VAULT_PATH / "Updates" / f"TWITTER_SUMMARY_{datetime.now().strftime('%Y%m%d')}.md"
    summary_file.parent.mkdir(exist_ok=True)

    summary_content = f"""---
type: twitter_summary
generated: {datetime.now().isoformat()}
---

# Twitter Activity Summary

{summary}

---
*Generated by AI Employee Twitter Integration*
"""

    summary_file.write_text(summary_content, encoding='utf-8')
    logger.info(f"✅ Twitter summary saved: {summary_file.name}")

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("TWITTER (X) INTEGRATION")
    logger.info("="*70)

    # Process approved posts
    processed = process_twitter_posts()

    # Generate summary
    generate_twitter_summary()

    logger.info("✅ Twitter integration complete")
