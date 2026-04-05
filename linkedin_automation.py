#!/usr/bin/env python3
"""
LinkedIn Automation - Generate and post business content for lead generation
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher

# LinkedIn automation using Playwright for web interaction
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: pip install playwright && playwright install")

class LinkedInAutomation(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = "linkedin_session"):
        super().__init__(vault_path, check_interval=3600)  # Check every hour
        self.session_path = Path(session_path)
        self.content_templates = self._load_content_templates()
        self.posting_schedule = self._load_posting_schedule()
        self.last_post_time = None

        # Create directories
        self.session_path.mkdir(exist_ok=True)
        (self.vault_path / "LinkedIn_Content").mkdir(exist_ok=True)
        (self.vault_path / "LinkedIn_Analytics").mkdir(exist_ok=True)

    def _load_content_templates(self):
        """Load content templates for business posts"""
        return {
            "business_tips": [
                "🚀 Business Tip: {tip}\n\n💡 How has this strategy worked for your business?\n\n#BusinessTips #Entrepreneurship #Growth",
                "📈 Growth Strategy: {strategy}\n\n🎯 What's your experience with this approach?\n\n#BusinessGrowth #Strategy #Success",
                "💼 Professional Insight: {insight}\n\n🤝 Share your thoughts in the comments!\n\n#ProfessionalDevelopment #Business #Leadership"
            ],
            "industry_updates": [
                "🔥 Industry Update: {update}\n\n📊 What do you think this means for our industry?\n\n#IndustryNews #TechTrends #Innovation",
                "⚡ Breaking: {news}\n\n💭 How will this impact your business strategy?\n\n#BusinessNews #MarketTrends #Strategy"
            ],
            "value_content": [
                "🎯 Free Resource: {resource}\n\n📚 Save this post for later reference!\n\n#FreeResource #BusinessTools #Productivity",
                "💡 Quick Tutorial: {tutorial}\n\n🔄 Repost if you found this helpful!\n\n#Tutorial #BusinessHacks #Tips"
            ]
        }

    def _load_posting_schedule(self):
        """Load optimal posting schedule"""
        return {
            "monday": ["09:00", "17:00"],
            "tuesday": ["10:00", "15:00"],
            "wednesday": ["09:00", "16:00"],
            "thursday": ["10:00", "17:00"],
            "friday": ["09:00", "14:00"],
            "saturday": [],  # No weekend posting
            "sunday": []
        }

    def check_for_updates(self) -> list:
        """Check if it's time to create new LinkedIn content"""
        now = datetime.now()

        # Check if we should create new content
        if self._should_create_content(now):
            return ["create_content"]

        return []

    def _should_create_content(self, now):
        """Determine if we should create new content"""
        # Don't post more than twice per day
        if self.last_post_time and (now - self.last_post_time).hours < 4:
            return False

        # Check if current time matches posting schedule
        day_name = now.strftime("%A").lower()
        current_time = now.strftime("%H:%M")

        schedule = self.posting_schedule.get(day_name, [])

        # Check if current time is within 30 minutes of scheduled time
        for scheduled_time in schedule:
            scheduled_dt = datetime.strptime(scheduled_time, "%H:%M").time()
            current_dt = now.time()

            # Calculate time difference
            time_diff = abs((datetime.combine(now.date(), current_dt) -
                           datetime.combine(now.date(), scheduled_dt)).total_seconds())

            if time_diff <= 1800:  # Within 30 minutes
                return True

        return False

    def create_action_file(self, item) -> Path:
        """Create LinkedIn content and approval request"""
        if item == "create_content":
            return self._generate_linkedin_content()
        return None

    def _generate_linkedin_content(self):
        """Generate LinkedIn content for approval"""
        # Select content type and template
        content_type = self._select_content_type()
        template = self._select_template(content_type)

        # Generate specific content based on type
        content = self._create_specific_content(content_type, template)

        # Create approval request
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.vault_path / "Pending_Approval" / filename

        approval_content = f"""---
type: approval_request
action: linkedin_post
priority: medium
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(hours=24)).isoformat()}
status: pending
platform: linkedin
content_type: {content_type}
---

# LinkedIn Post Approval Request

## Proposed Content
{content}

## Post Details
- **Platform**: LinkedIn
- **Content Type**: {content_type.replace('_', ' ').title()}
- **Scheduled Time**: Next available slot
- **Target Audience**: Professional network
- **Objective**: Lead generation and engagement

## Expected Outcomes
- Increase brand visibility
- Generate engagement (likes, comments, shares)
- Attract potential leads
- Establish thought leadership

## Company Handbook Compliance
⚠️ **APPROVAL REQUIRED**: Social media posting requires human approval per Company Handbook

## To Approve
Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder

## Analytics Tracking
- Post engagement will be tracked
- Lead generation metrics will be monitored
- ROI analysis will be provided

---
*Generated by LinkedIn Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        filepath.write_text(approval_content, encoding='utf-8')
        self.logger.info(f"Created LinkedIn post approval request: {filename}")

        return filepath

    def _select_content_type(self):
        """Select content type based on strategy"""
        # Rotate content types for variety
        types = ["business_tips", "industry_updates", "value_content"]

        # Simple rotation based on day of week
        day_index = datetime.now().weekday()
        return types[day_index % len(types)]

    def _select_template(self, content_type):
        """Select template from content type"""
        templates = self.content_templates.get(content_type, [])
        if not templates:
            return "📢 Business Update: {content}\n\n#Business #Professional"

        # Rotate templates
        template_index = datetime.now().hour % len(templates)
        return templates[template_index]

    def _create_specific_content(self, content_type, template):
        """Create specific content based on type"""
        content_map = {
            "business_tips": {
                "tip": "Focus on solving real problems for your customers. The best businesses are built on genuine value creation, not just profit maximization.",
                "strategy": "Implement a customer feedback loop. Regular surveys and direct communication help you stay aligned with market needs.",
                "insight": "Consistency beats perfection. Small daily improvements compound into significant long-term success."
            },
            "industry_updates": {
                "update": "AI automation is transforming business operations across industries. Companies adopting AI-first approaches are seeing 40% efficiency gains.",
                "news": "Remote work productivity tools are evolving rapidly. The future of work is becoming increasingly flexible and technology-driven."
            },
            "value_content": {
                "resource": "5-step business automation checklist that can save you 10+ hours per week. Comment 'AUTOMATION' for the free download!",
                "tutorial": "How to set up automated customer follow-ups in 3 simple steps: 1) Define trigger events 2) Create email sequences 3) Monitor and optimize"
            }
        }

        content_data = content_map.get(content_type, {})

        # Fill template with content
        filled_template = template
        for key, value in content_data.items():
            filled_template = filled_template.replace(f"{{{key}}}", value)

        return filled_template

    def post_to_linkedin(self, content, approved_file_path):
        """Post approved content to LinkedIn"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available for LinkedIn posting")
            return False

        try:
            with sync_playwright() as p:
                # Launch browser with persistent session
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Set to True for production
                    viewport={"width": 1280, "height": 720}
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to LinkedIn
                page.goto("https://www.linkedin.com/feed/")

                # Wait for login or feed to load
                try:
                    # Check if already logged in
                    page.wait_for_selector('[data-test-id="share-box-trigger"]', timeout=10000)
                except:
                    self.logger.warning("LinkedIn login required. Please log in manually.")
                    input("Press Enter after logging in...")

                # Click share box
                page.click('[data-test-id="share-box-trigger"]')

                # Wait for compose dialog
                page.wait_for_selector('[data-test-id="share-box-text-editor"]')

                # Enter content
                page.fill('[data-test-id="share-box-text-editor"]', content)

                # Wait a moment for content to be processed
                time.sleep(2)

                # Click post button
                page.click('[data-test-id="share-actions-post-button"]')

                # Wait for post to be published
                time.sleep(3)

                browser.close()

                # Log successful post
                self._log_linkedin_post(content, approved_file_path)
                self.last_post_time = datetime.now()

                return True

        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return False

    def _log_linkedin_post(self, content, approved_file_path):
        """Log LinkedIn post for analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "content": content[:100] + "..." if len(content) > 100 else content,
            "approved_file": str(approved_file_path),
            "status": "posted",
            "platform": "linkedin"
        }

        # Save to analytics log
        analytics_file = self.vault_path / "LinkedIn_Analytics" / f"{datetime.now().strftime('%Y-%m')}.json"

        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                analytics = json.load(f)
        else:
            analytics = []

        analytics.append(log_entry)

        with open(analytics_file, 'w') as f:
            json.dump(analytics, f, indent=2)

        self.logger.info("LinkedIn post logged to analytics")

if __name__ == "__main__":
    import sys

    vault_path = "AI_Employee_Vault"
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]

    automation = LinkedInAutomation(vault_path)
    print(f"Starting LinkedIn Automation for: {vault_path}")
    print("Generating business content for lead generation...")
    print("Press Ctrl+C to stop")

    automation.run()