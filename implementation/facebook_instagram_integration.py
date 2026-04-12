#!/usr/bin/env python3
"""
Facebook & Instagram Integration for AI Employee
Post content and generate activity summaries
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
logger = logging.getLogger('FacebookInstagramIntegration')

# Facebook/Instagram API Configuration
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')

VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"

class FacebookInstagramManager:
    """Manage Facebook and Instagram posting and analytics"""

    def __init__(self):
        self.page_token = FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.instagram_id = INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.graph_api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.graph_api_version}'

    def post_to_facebook(self, message, link=None, image_url=None):
        """Post to Facebook Page"""
        if not self.page_token or not self.page_id:
            logger.error("❌ Facebook credentials not configured")
            return None

        url = f"{self.base_url}/{self.page_id}/feed"

        params = {
            'message': message,
            'access_token': self.page_token
        }

        if link:
            params['link'] = link

        if image_url:
            params['picture'] = image_url

        try:
            response = requests.post(url, params=params, timeout=30)

            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id')
                logger.info(f"✅ Facebook post published: {post_id}")
                return post_id
            else:
                logger.error(f"❌ Failed to post to Facebook: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error posting to Facebook: {e}")
            return None

    def post_to_instagram(self, image_url, caption):
        """Post to Instagram Business Account"""
        if not self.page_token or not self.instagram_id:
            logger.error("❌ Instagram credentials not configured")
            return None

        # Step 1: Create media container
        container_url = f"{self.base_url}/{self.instagram_id}/media"

        container_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.page_token
        }

        try:
            # Create container
            container_response = requests.post(container_url, params=container_params, timeout=30)

            if container_response.status_code != 200:
                logger.error(f"❌ Failed to create Instagram container: {container_response.text}")
                return None

            container_id = container_response.json().get('id')

            # Step 2: Publish media
            publish_url = f"{self.base_url}/{self.instagram_id}/media_publish"

            publish_params = {
                'creation_id': container_id,
                'access_token': self.page_token
            }

            publish_response = requests.post(publish_url, params=publish_params, timeout=30)

            if publish_response.status_code == 200:
                post_id = publish_response.json().get('id')
                logger.info(f"✅ Instagram post published: {post_id}")
                return post_id
            else:
                logger.error(f"❌ Failed to publish Instagram post: {publish_response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Error posting to Instagram: {e}")
            return None

    def get_facebook_insights(self):
        """Get Facebook Page insights"""
        if not self.page_token or not self.page_id:
            return {}

        url = f"{self.base_url}/{self.page_id}/insights"

        params = {
            'metric': 'page_impressions,page_engaged_users,page_post_engagements',
            'period': 'week',
            'access_token': self.page_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"❌ Failed to fetch Facebook insights: {response.text}")
                return []

        except Exception as e:
            logger.error(f"❌ Error fetching Facebook insights: {e}")
            return []

    def get_instagram_insights(self):
        """Get Instagram Business Account insights"""
        if not self.page_token or not self.instagram_id:
            return {}

        url = f"{self.base_url}/{self.instagram_id}/insights"

        params = {
            'metric': 'impressions,reach,profile_views',
            'period': 'week',
            'access_token': self.page_token
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"❌ Failed to fetch Instagram insights: {response.text}")
                return []

        except Exception as e:
            logger.error(f"❌ Error fetching Instagram insights: {e}")
            return []

    def generate_summary(self, fb_insights, ig_insights):
        """Generate combined Facebook/Instagram summary"""
        summary = "## Facebook & Instagram Activity Summary\n\n"

        # Facebook metrics
        summary += "### Facebook Page\n"
        if fb_insights:
            for metric in fb_insights:
                name = metric.get('name', 'Unknown')
                values = metric.get('values', [])
                if values:
                    value = values[0].get('value', 0)
                    summary += f"- {name}: {value}\n"
        else:
            summary += "- No data available\n"

        summary += "\n### Instagram Business\n"
        if ig_insights:
            for metric in ig_insights:
                name = metric.get('name', 'Unknown')
                values = metric.get('values', [])
                if values:
                    value = values[0].get('value', 0)
                    summary += f"- {name}: {value}\n"
        else:
            summary += "- No data available\n"

        return summary

def process_facebook_posts():
    """Process approved Facebook posts from vault"""
    logger.info("📘 Processing Facebook posts...")

    manager = FacebookInstagramManager()
    processed_count = 0

    # Find approved Facebook posts
    facebook_files = list(APPROVED_PATH.glob("FACEBOOK_POST_*.md"))

    for post_file in facebook_files:
        try:
            content = post_file.read_text(encoding='utf-8')

            # Extract post content
            if '---' in content:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    post_content = parts[2].strip()

                    # Remove markdown headers
                    post_content = post_content.replace('## Post Content', '').strip()
                    lines = post_content.split('\n')
                    message = '\n'.join(line for line in lines if line.strip())

                    # Post to Facebook
                    post_id = manager.post_to_facebook(message)

                    if post_id:
                        # Log success
                        log_social_post('facebook', post_file.name, post_id, message)

                        # Move to Done
                        done_file = DONE_PATH / post_file.name
                        post_file.rename(done_file)

                        processed_count += 1
                        logger.info(f"✅ Posted and moved to Done: {post_file.name}")

        except Exception as e:
            logger.error(f"❌ Error processing {post_file.name}: {e}")

    logger.info(f"✅ Processed {processed_count} Facebook posts")
    return processed_count

def process_instagram_posts():
    """Process approved Instagram posts from vault"""
    logger.info("📸 Processing Instagram posts...")

    manager = FacebookInstagramManager()
    processed_count = 0

    # Find approved Instagram posts
    instagram_files = list(APPROVED_PATH.glob("INSTAGRAM_POST_*.md"))

    for post_file in instagram_files:
        try:
            content = post_file.read_text(encoding='utf-8')

            # Extract metadata and content
            if '---' in content:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Parse frontmatter for image_url
                    frontmatter = parts[1]
                    image_url = None
                    for line in frontmatter.split('\n'):
                        if 'image_url:' in line:
                            image_url = line.split('image_url:')[1].strip()

                    caption = parts[2].strip()
                    caption = caption.replace('## Caption', '').strip()

                    if image_url:
                        # Post to Instagram
                        post_id = manager.post_to_instagram(image_url, caption)

                        if post_id:
                            # Log success
                            log_social_post('instagram', post_file.name, post_id, caption)

                            # Move to Done
                            done_file = DONE_PATH / post_file.name
                            post_file.rename(done_file)

                            processed_count += 1
                            logger.info(f"✅ Posted and moved to Done: {post_file.name}")
                    else:
                        logger.warning(f"⚠️ No image_url found in {post_file.name}")

        except Exception as e:
            logger.error(f"❌ Error processing {post_file.name}: {e}")

    logger.info(f"✅ Processed {processed_count} Instagram posts")
    return processed_count

def log_social_post(platform, filename, post_id, content):
    """Log social media post to audit trail"""
    LOGS_PATH.mkdir(exist_ok=True)

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': f'{platform}_post',
        'filename': filename,
        'post_id': post_id,
        'content_preview': content[:100],
        'status': 'success'
    }

    log_file = LOGS_PATH / f"social_media_{datetime.now().strftime('%Y%m%d')}.json"

    try:
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    except Exception as e:
        logger.error(f"Error logging social post: {e}")

def generate_social_summary():
    """Generate combined social media summary"""
    logger.info("📊 Generating social media summary...")

    manager = FacebookInstagramManager()

    fb_insights = manager.get_facebook_insights()
    ig_insights = manager.get_instagram_insights()

    summary = manager.generate_summary(fb_insights, ig_insights)

    # Save summary to vault
    summary_file = VAULT_PATH / "Updates" / f"SOCIAL_SUMMARY_{datetime.now().strftime('%Y%m%d')}.md"
    summary_file.parent.mkdir(exist_ok=True)

    summary_content = f"""---
type: social_media_summary
generated: {datetime.now().isoformat()}
platforms: [facebook, instagram]
---

# Social Media Activity Summary

{summary}

---
*Generated by AI Employee Social Media Integration*
"""

    summary_file.write_text(summary_content, encoding='utf-8')
    logger.info(f"✅ Social media summary saved: {summary_file.name}")

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("FACEBOOK & INSTAGRAM INTEGRATION")
    logger.info("="*70)

    # Process approved posts
    fb_count = process_facebook_posts()
    ig_count = process_instagram_posts()

    # Generate summary
    generate_social_summary()

    logger.info(f"✅ Social media integration complete ({fb_count} FB, {ig_count} IG)")
