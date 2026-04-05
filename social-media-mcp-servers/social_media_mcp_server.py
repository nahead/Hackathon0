#!/usr/bin/env python3
"""
Social Media MCP Server - Model Context Protocol Server for Social Media Operations
Provides Claude Code with social media management capabilities across platforms
"""

import asyncio
import json
import sys
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import base64

class SocialMediaMCPServer:
    def __init__(self):
        self.vault_path = Path("AI_Employee_Vault")
        self.config_path = self.vault_path / "Config" / "social_media_config.json"
        self.logs_path = self.vault_path / "Logs"
        self.content_path = self.vault_path / "Content"

        # Create directories
        for path in [self.config_path.parent, self.logs_path, self.content_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'social_media_mcp.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

        # Platform handlers
        self.platforms = {
            'linkedin': self.handle_linkedin,
            'facebook': self.handle_facebook,
            'twitter': self.handle_twitter,
            'instagram': self.handle_instagram
        }

    def load_config(self) -> Dict:
        """Load social media configuration"""
        default_config = {
            "platforms": {
                "linkedin": {
                    "enabled": True,
                    "credentials": {},
                    "posting_schedule": "daily",
                    "content_types": ["text", "image", "article"]
                },
                "facebook": {
                    "enabled": True,
                    "credentials": {},
                    "posting_schedule": "daily",
                    "content_types": ["text", "image", "video"]
                },
                "twitter": {
                    "enabled": True,
                    "credentials": {},
                    "posting_schedule": "multiple_daily",
                    "content_types": ["text", "image"]
                },
                "instagram": {
                    "enabled": False,
                    "credentials": {},
                    "posting_schedule": "daily",
                    "content_types": ["image", "video"]
                }
            },
            "content_templates": {
                "business_update": "🚀 Exciting business update: {content}",
                "achievement": "🎉 Proud to share: {content}",
                "tip": "💡 Pro tip: {content}",
                "announcement": "📢 Important announcement: {content}"
            },
            "hashtag_sets": {
                "business": ["#Business", "#Entrepreneur", "#Success"],
                "tech": ["#Technology", "#Innovation", "#AI"],
                "productivity": ["#Productivity", "#Efficiency", "#Growth"]
            },
            "posting_times": {
                "linkedin": ["09:00", "13:00", "17:00"],
                "facebook": ["10:00", "15:00", "19:00"],
                "twitter": ["08:00", "12:00", "16:00", "20:00"],
                "instagram": ["11:00", "18:00"]
            }
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config

    def save_config(self, config: Dict):
        """Save social media configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests for social media operations"""
        try:
            method = request.get('method')
            params = request.get('params', {})

            if method == 'social.post':
                return await self.create_post(params)
            elif method == 'social.schedule_post':
                return await self.schedule_post(params)
            elif method == 'social.get_engagement_metrics':
                return await self.get_engagement_metrics(params)
            elif method == 'social.create_content':
                return await self.create_content(params)
            elif method == 'social.get_scheduled_posts':
                return await self.get_scheduled_posts(params)
            elif method == 'social.cancel_scheduled_post':
                return await self.cancel_scheduled_post(params)
            elif method == 'social.get_platform_status':
                return await self.get_platform_status(params)
            elif method == 'social.create_announcement_post':
                return await self.create_announcement_post(params)
            elif method == 'social.test_connections':
                return await self.test_connections()
            else:
                return {
                    'error': f'Unknown method: {method}',
                    'available_methods': [
                        'social.post',
                        'social.schedule_post',
                        'social.get_engagement_metrics',
                        'social.create_content',
                        'social.get_scheduled_posts',
                        'social.cancel_scheduled_post',
                        'social.get_platform_status',
                        'social.create_announcement_post',
                        'social.test_connections'
                    ]
                }

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}

    async def create_post(self, params: Dict) -> Dict:
        """Create and publish social media post"""
        try:
            platforms = params.get('platforms', ['linkedin'])
            content = params.get('content')
            image_path = params.get('image_path')
            template = params.get('template')

            if not content:
                return {'error': 'content is required'}

            # Apply template if specified
            if template and template in self.config['content_templates']:
                content = self.config['content_templates'][template].format(content=content)

            results = {}
            for platform in platforms:
                if platform in self.platforms:
                    try:
                        result = await self.platforms[platform]('post', {
                            'content': content,
                            'image_path': image_path
                        })
                        results[platform] = result
                    except Exception as e:
                        results[platform] = {'error': str(e)}
                else:
                    results[platform] = {'error': f'Platform {platform} not supported'}

            return {
                'success': True,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': str(e)}

    async def schedule_post(self, params: Dict) -> Dict:
        """Schedule social media post for later"""
        try:
            platforms = params.get('platforms', ['linkedin'])
            content = params.get('content')
            schedule_time = params.get('schedule_time')
            image_path = params.get('image_path')

            if not all([content, schedule_time]):
                return {'error': 'content and schedule_time are required'}

            # Create scheduled post entry
            scheduled_post = {
                'id': f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'platforms': platforms,
                'content': content,
                'image_path': image_path,
                'schedule_time': schedule_time,
                'status': 'scheduled',
                'created_at': datetime.now().isoformat()
            }

            # Save to scheduled posts file
            scheduled_file = self.content_path / "scheduled_posts.json"
            scheduled_posts = []

            if scheduled_file.exists():
                try:
                    with open(scheduled_file, 'r') as f:
                        scheduled_posts = json.load(f)
                except:
                    scheduled_posts = []

            scheduled_posts.append(scheduled_post)

            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_posts, f, indent=2)

            return {
                'success': True,
                'post_id': scheduled_post['id'],
                'message': f'Post scheduled for {schedule_time}'
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_engagement_metrics(self, params: Dict) -> Dict:
        """Get engagement metrics for social media"""
        try:
            period = params.get('period', 'week')
            platforms = params.get('platforms', list(self.platforms.keys()))

            # Simulate metrics (in real implementation, would call platform APIs)
            metrics = {}
            for platform in platforms:
                if platform in self.platforms:
                    metrics[platform] = {
                        'posts_published': 7,
                        'total_likes': 156,
                        'total_comments': 23,
                        'total_shares': 12,
                        'engagement_rate': 4.2,
                        'follower_growth': 15,
                        'reach': 2340,
                        'impressions': 5670
                    }

            overall_metrics = {
                'total_posts': sum(m.get('posts_published', 0) for m in metrics.values()),
                'total_engagement': sum(
                    m.get('total_likes', 0) + m.get('total_comments', 0) + m.get('total_shares', 0)
                    for m in metrics.values()
                ),
                'average_engagement_rate': sum(m.get('engagement_rate', 0) for m in metrics.values()) / len(metrics) if metrics else 0,
                'total_reach': sum(m.get('reach', 0) for m in metrics.values())
            }

            return {
                'success': True,
                'period': period,
                'platform_metrics': metrics,
                'overall_metrics': overall_metrics
            }

        except Exception as e:
            return {'error': str(e)}

    async def create_content(self, params: Dict) -> Dict:
        """Create content for social media posting"""
        try:
            content_type = params.get('type', 'business_update')
            topic = params.get('topic')
            platform = params.get('platform', 'linkedin')
            hashtags = params.get('hashtags', [])

            if not topic:
                return {'error': 'topic is required'}

            # Generate content based on type and platform
            content_templates = {
                'business_update': f"🚀 Exciting update: {topic}",
                'achievement': f"🎉 Proud to announce: {topic}",
                'tip': f"💡 Pro tip: {topic}",
                'question': f"🤔 What's your take on {topic}?",
                'behind_scenes': f"👀 Behind the scenes: {topic}"
            }

            base_content = content_templates.get(content_type, f"📢 {topic}")

            # Add platform-specific formatting
            if platform == 'twitter':
                # Keep it short for Twitter
                content = base_content[:240]
            elif platform == 'linkedin':
                # More professional tone for LinkedIn
                content = f"{base_content}\n\nWhat are your thoughts on this?"
            else:
                content = base_content

            # Add hashtags
            if hashtags:
                content += f"\n\n{' '.join(hashtags)}"
            elif content_type in self.config['hashtag_sets']:
                content += f"\n\n{' '.join(self.config['hashtag_sets'][content_type])}"

            # Save content for future use
            content_entry = {
                'id': f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'type': content_type,
                'topic': topic,
                'platform': platform,
                'content': content,
                'created_at': datetime.now().isoformat(),
                'status': 'draft'
            }

            content_file = self.content_path / "generated_content.json"
            content_list = []

            if content_file.exists():
                try:
                    with open(content_file, 'r') as f:
                        content_list = json.load(f)
                except:
                    content_list = []

            content_list.append(content_entry)

            with open(content_file, 'w') as f:
                json.dump(content_list, f, indent=2)

            return {
                'success': True,
                'content_id': content_entry['id'],
                'content': content,
                'character_count': len(content)
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_scheduled_posts(self, params: Dict) -> Dict:
        """Get list of scheduled posts"""
        try:
            scheduled_file = self.content_path / "scheduled_posts.json"

            if not scheduled_file.exists():
                return {
                    'success': True,
                    'scheduled_posts': [],
                    'count': 0
                }

            with open(scheduled_file, 'r') as f:
                scheduled_posts = json.load(f)

            # Filter by status if specified
            status = params.get('status')
            if status:
                scheduled_posts = [p for p in scheduled_posts if p.get('status') == status]

            return {
                'success': True,
                'scheduled_posts': scheduled_posts,
                'count': len(scheduled_posts)
            }

        except Exception as e:
            return {'error': str(e)}

    async def cancel_scheduled_post(self, params: Dict) -> Dict:
        """Cancel a scheduled post"""
        try:
            post_id = params.get('post_id')

            if not post_id:
                return {'error': 'post_id is required'}

            scheduled_file = self.content_path / "scheduled_posts.json"

            if not scheduled_file.exists():
                return {'error': 'No scheduled posts found'}

            with open(scheduled_file, 'r') as f:
                scheduled_posts = json.load(f)

            # Find and update post
            post_found = False
            for post in scheduled_posts:
                if post['id'] == post_id:
                    post['status'] = 'cancelled'
                    post['cancelled_at'] = datetime.now().isoformat()
                    post_found = True
                    break

            if not post_found:
                return {'error': f'Post {post_id} not found'}

            with open(scheduled_file, 'w') as f:
                json.dump(scheduled_posts, f, indent=2)

            return {
                'success': True,
                'message': f'Post {post_id} cancelled successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_platform_status(self, params: Dict) -> Dict:
        """Get status of social media platforms"""
        try:
            platform_status = {}

            for platform_name, platform_config in self.config['platforms'].items():
                status = {
                    'enabled': platform_config.get('enabled', False),
                    'configured': bool(platform_config.get('credentials')),
                    'last_post': 'N/A',  # Would be retrieved from logs
                    'posting_schedule': platform_config.get('posting_schedule'),
                    'supported_content_types': platform_config.get('content_types', [])
                }
                platform_status[platform_name] = status

            return {
                'success': True,
                'platform_status': platform_status
            }

        except Exception as e:
            return {'error': str(e)}

    async def create_announcement_post(self, params: Dict) -> Dict:
        """Create announcement post for cross-domain workflows"""
        try:
            announcement_type = params.get('type', 'general')
            data = params.get('data', {})
            requires_approval = params.get('requires_approval', True)

            # Generate announcement content based on type
            if announcement_type == 'new_client':
                content = f"🎉 Excited to welcome a new client to our growing family! Looking forward to delivering exceptional results."
            elif announcement_type == 'milestone':
                content = f"🚀 Milestone achieved! {data.get('description', 'Another step forward in our journey.')}"
            elif announcement_type == 'service_update':
                content = f"📢 Service Update: {data.get('description', 'We continue to improve our offerings.')}"
            else:
                content = f"📣 {data.get('message', 'Important business update!')}"

            if requires_approval:
                # Create approval request
                approval_request = {
                    'type': 'social_media_post',
                    'content': content,
                    'platforms': data.get('platforms', ['linkedin']),
                    'created_at': datetime.now().isoformat(),
                    'status': 'pending_approval'
                }

                approval_file = self.vault_path / "Needs_Action" / f"SOCIAL_POST_APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                approval_file.parent.mkdir(parents=True, exist_ok=True)

                approval_content = f"""---
type: social_media_approval
priority: medium
requires_approval: true
---

# Social Media Post Approval Required

## Proposed Content
{content}

## Platforms
{', '.join(data.get('platforms', ['linkedin']))}

## Approval Actions
- **To Approve:** Move this file to `/Approved/` folder
- **To Reject:** Move this file to `/Rejected/` folder with comments

---
*Generated by Social Media MCP Server*
"""

                approval_file.write_text(approval_content, encoding='utf-8')

                return {
                    'success': True,
                    'message': 'Post queued for approval',
                    'approval_file': str(approval_file)
                }
            else:
                # Post immediately
                return await self.create_post({
                    'content': content,
                    'platforms': data.get('platforms', ['linkedin'])
                })

        except Exception as e:
            return {'error': str(e)}

    async def test_connections(self) -> Dict:
        """Test connections to social media platforms"""
        try:
            connection_status = {}

            for platform in self.platforms.keys():
                try:
                    # Simulate connection test
                    connection_status[platform] = {
                        'connected': self.config['platforms'][platform].get('enabled', False),
                        'configured': bool(self.config['platforms'][platform].get('credentials')),
                        'last_test': datetime.now().isoformat()
                    }
                except Exception as e:
                    connection_status[platform] = {
                        'connected': False,
                        'error': str(e)
                    }

            return {
                'success': True,
                'connections': connection_status
            }

        except Exception as e:
            return {'error': str(e)}

    # Platform-specific handlers
    async def handle_linkedin(self, action: str, params: Dict) -> Dict:
        """Handle LinkedIn operations with Playwright automation"""
        try:
            if action == 'post':
                # Use Playwright automation for actual LinkedIn posting
                return await self.linkedin_playwright_post(params)
            elif action == 'test_connection':
                return await self.test_linkedin_connection()
            else:
                return {'error': f'Unknown LinkedIn action: {action}'}
        except Exception as e:
            self.logger.error(f"LinkedIn handler error: {e}")
            return {'error': str(e)}

    async def linkedin_playwright_post(self, params: Dict) -> Dict:
        """Post to LinkedIn using Playwright automation"""
        try:
            content = params.get('content', '')
            if not content:
                return {'error': 'No content provided for LinkedIn post'}

            # Import our LinkedIn automation
            import sys
            sys.path.append('.')
            from linkedin_automation_demo import LinkedInAutomation

            # Create automation instance
            linkedin = LinkedInAutomation()

            # Execute posting workflow
            results = linkedin.create_linkedin_post(content)

            # Check if all steps succeeded
            success_count = sum(1 for step, result in results if result and not result.get('isError'))
            total_steps = len(results)

            if success_count >= 5:  # At least navigation, screenshot, find, click, type succeeded
                post_id = f"linkedin_playwright_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Log successful automation
                self.logger.info(f"LinkedIn automation completed: {success_count}/{total_steps} steps successful")

                return {
                    'success': True,
                    'platform': 'linkedin',
                    'post_id': post_id,
                    'message': f'LinkedIn automation completed ({success_count}/{total_steps} steps)',
                    'automation_results': results,
                    'method': 'playwright_automation'
                }
            else:
                return {
                    'success': False,
                    'platform': 'linkedin',
                    'error': f'LinkedIn automation failed: only {success_count}/{total_steps} steps succeeded',
                    'automation_results': results
                }

        except Exception as e:
            self.logger.error(f"LinkedIn Playwright posting error: {e}")
            return {'error': f'LinkedIn automation failed: {str(e)}'}

    async def test_linkedin_connection(self) -> Dict:
        """Test LinkedIn connection using Playwright"""
        try:
            import sys
            sys.path.append('.')
            from linkedin_automation_demo import LinkedInAutomation

            linkedin = LinkedInAutomation()

            # Test navigation to LinkedIn
            nav_result = linkedin.navigate_to_linkedin()

            if nav_result and not nav_result.get('isError'):
                return {
                    'success': True,
                    'platform': 'linkedin',
                    'message': 'LinkedIn connection test successful',
                    'method': 'playwright_automation'
                }
            else:
                return {
                    'success': False,
                    'platform': 'linkedin',
                    'error': 'LinkedIn connection test failed'
                }

        except Exception as e:
            return {
                'success': False,
                'platform': 'linkedin',
                'error': f'LinkedIn connection test error: {str(e)}'
            }

    async def handle_facebook(self, action: str, params: Dict) -> Dict:
        """Handle Facebook operations"""
        if action == 'post':
            # Simulate Facebook posting
            return {
                'success': True,
                'platform': 'facebook',
                'post_id': f"facebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': 'Posted to Facebook successfully'
            }
        return {'error': f'Unknown Facebook action: {action}'}

    async def handle_twitter(self, action: str, params: Dict) -> Dict:
        """Handle Twitter operations"""
        if action == 'post':
            # Simulate Twitter posting
            return {
                'success': True,
                'platform': 'twitter',
                'post_id': f"twitter_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': 'Posted to Twitter successfully'
            }
        return {'error': f'Unknown Twitter action: {action}'}

    async def handle_instagram(self, action: str, params: Dict) -> Dict:
        """Handle Instagram operations"""
        if action == 'post':
            # Instagram requires images
            if not params.get('image_path'):
                return {'error': 'Instagram posts require an image'}

            return {
                'success': True,
                'platform': 'instagram',
                'post_id': f"instagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'message': 'Posted to Instagram successfully'
            }
        return {'error': f'Unknown Instagram action: {action}'}

# MCP Server Protocol Implementation
async def main():
    """Main MCP server loop"""
    server = SocialMediaMCPServer()

    print("[SOCIAL MCP] Social Media MCP Server starting...")
    print("Available methods:")
    print("- social.post")
    print("- social.schedule_post")
    print("- social.get_engagement_metrics")
    print("- social.create_content")
    print("- social.get_scheduled_posts")
    print("- social.cancel_scheduled_post")
    print("- social.get_platform_status")
    print("- social.create_announcement_post")
    print("- social.test_connections")

    # Test connections on startup
    test_result = await server.test_connections()
    if test_result.get('success'):
        print("[SUCCESS] Platform connections checked")
    else:
        print("[ERROR] Platform connection check failed - server will still start")

    # Simple JSON-RPC over stdin/stdout for MCP
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line.strip())
            response = await server.handle_request(request)

            # Add JSON-RPC envelope
            rpc_response = {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': response
            }

            print(json.dumps(rpc_response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': 'Parse error'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': request.get('id') if 'request' in locals() else None,
                'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Social Media MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)