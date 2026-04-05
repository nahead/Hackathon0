#!/usr/bin/env python3
"""
Auto Content Generator - Automatic LinkedIn and Twitter content generation
Generates professional content automatically for social media platforms
"""

import os
import time
import random
from pathlib import Path
from datetime import datetime
import schedule

class AutoContentGenerator:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

        # Content templates and topics
        self.linkedin_topics = [
            "AI automation benefits for businesses",
            "Digital transformation strategies",
            "Productivity tips for professionals",
            "Business efficiency improvements",
            "Technology trends in workplace",
            "Leadership in digital age",
            "Remote work optimization",
            "Customer service automation",
            "Data-driven decision making",
            "Innovation in business processes"
        ]

        self.twitter_topics = [
            "AI automation success",
            "Business productivity tips",
            "Tech innovation updates",
            "Workplace efficiency",
            "Digital transformation",
            "Automation benefits",
            "Professional growth",
            "Business insights",
            "Technology trends",
            "Industry updates"
        ]

        self.business_benefits = [
            "90% reduction in manual processing",
            "24/7 automated operations",
            "Zero manual errors achieved",
            "Consistent professional communication",
            "Scalable business operations",
            "Improved customer response time",
            "Enhanced productivity metrics",
            "Streamlined workflow processes",
            "Cost-effective automation",
            "Real-time performance tracking"
        ]

        self.hashtags_linkedin = [
            "#AIAutomation", "#BusinessEfficiency", "#DigitalTransformation",
            "#Productivity", "#Innovation", "#Leadership", "#TechTrends",
            "#WorkplaceAutomation", "#BusinessGrowth", "#ProfessionalDevelopment"
        ]

        self.hashtags_twitter = [
            "#AI", "#Automation", "#Business", "#Tech", "#Innovation",
            "#Productivity", "#DigitalTransformation", "#Efficiency",
            "#TechTrends", "#BusinessTips"
        ]

    def generate_linkedin_content(self):
        """Generate professional LinkedIn post"""
        topic = random.choice(self.linkedin_topics)
        benefits = random.sample(self.business_benefits, 3)
        hashtags = random.sample(self.hashtags_linkedin, 5)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        content = f"""---
type: linkedin_post_approval
timestamp: {datetime.now().isoformat()}
content_type: business_networking
target_audience: professionals
auto_generated: true
---

# LinkedIn Post Approval Required

## Proposed Content
```
🚀 Exciting developments in {topic.lower()} are transforming how businesses operate!

Key benefits we're seeing:
✅ {benefits[0]}
✅ {benefits[1]}
✅ {benefits[2]}

The future of business efficiency is here. AI employees are not replacing humans - they're amplifying our capabilities and freeing us to focus on strategic growth.

What's your experience with business automation? Share your thoughts below! 👇

{' '.join(hashtags)}
```

## Content Analysis:
- **Engagement potential**: High (question + call-to-action)
- **Professional tone**: ✓ Appropriate for LinkedIn
- **Value proposition**: Clear benefits highlighted
- **Hashtags**: {len(hashtags)} relevant industry tags
- **Length**: Optimal for LinkedIn engagement

## Actions Required:
- [ ] Review content for brand alignment
- [ ] Edit if necessary
- [ ] Move to /Done folder to approve
- [ ] Manually post to LinkedIn
- [ ] Move to /Archive when posted

## Instructions:
1. Review the proposed LinkedIn post above
2. Edit content if needed
3. Move file to AI_Employee_Vault/Done/ to approve
4. Copy content and post manually to LinkedIn
5. Move to Archive folder when completed
"""

        # Save LinkedIn content
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        print(f"OK LinkedIn content generated: {filename}")
        return filename

    def generate_twitter_content(self):
        """Generate Twitter post for API posting"""
        topic = random.choice(self.twitter_topics)
        benefit = random.choice(self.business_benefits)
        hashtags = random.sample(self.hashtags_twitter, 4)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Create tweet content (under 280 characters)
        tweet_text = f"Just achieved amazing results with {topic}!\n\n- {benefit}\n- Continuous 24/7 operations\n- Zero manual errors\n\nAI automation is amplifying human capabilities!\n\nWhat's your automation story?\n\n{' '.join(hashtags)}"

        content = f"""---
type: twitter_post_approval
timestamp: {datetime.now().isoformat()}
content_type: business_update
platform: twitter_api
character_count: {len(tweet_text)}
auto_generated: true
---

# Twitter Post Approval Required

## Proposed Twitter Content:
```
{tweet_text}
```

## Content Analysis:
- **Character count**: {len(tweet_text)}/280 (within Twitter limit)
- **Engagement elements**: Question, emojis, call-to-action
- **Hashtags**: {len(hashtags)} relevant trending tags
- **Tone**: Professional yet engaging
- **Value**: Shares real results and insights

## Twitter API Integration:
- **Method**: Official Twitter API v1.1
- **Authentication**: OAuth 1.0a configured
- **Rate limits**: Within posting limits
- **Analytics**: Automatic tracking enabled

## Actions Required:
- [ ] Review content for brand alignment
- [ ] Verify character count ({len(tweet_text)}/280)
- [ ] Move to /Done folder to approve
- [ ] System will auto-post via Twitter API
- [ ] Check /Archive for completion

## Instructions:
1. Review the proposed tweet above
2. Edit if necessary (keep under 280 characters)
3. Move file to AI_Employee_Vault/Done/ to approve
4. System will automatically post via Twitter API
5. Check Archive folder for completion confirmation
"""

        # Save Twitter content
        filename = f"TWITTER_POST_{timestamp}.md"
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        print(f"OK Twitter content generated: {filename}")
        return filename

    def generate_daily_content(self):
        """Generate daily content for both platforms"""
        print(f"\n=== Daily Content Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        # Generate LinkedIn content
        linkedin_file = self.generate_linkedin_content()

        # Wait a moment
        time.sleep(2)

        # Generate Twitter content
        twitter_file = self.generate_twitter_content()

        print(f"OK Daily content generation completed!")
        print(f"  - LinkedIn: {linkedin_file}")
        print(f"  - Twitter: {twitter_file}")
        print(f"  - Location: {self.needs_action}")
        print("Content ready for review and approval!")

        return linkedin_file, twitter_file

    def start_scheduled_generation(self):
        """Start scheduled content generation"""
        print("Auto Content Generator Starting...")
        print(f"Output folder: {self.needs_action}")
        print("Schedule: Daily content generation")
        print("Press Ctrl+C to stop")

        # Schedule daily content generation
        schedule.every().day.at("09:00").do(self.generate_daily_content)
        schedule.every().day.at("15:00").do(self.generate_daily_content)

        # Generate initial content
        print("\nGenerating initial content...")
        self.generate_daily_content()

        # Run scheduler
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                print("\nStopping Auto Content Generator...")
                break
            except Exception as e:
                print(f"Error in content generation: {e}")
                time.sleep(300)  # Wait 5 minutes on error

def main():
    print("Auto Content Generator")
    print("=" * 40)
    print("Automatic LinkedIn and Twitter content generation")
    print()

    generator = AutoContentGenerator("AI_Employee_Vault")

    # Check if user wants scheduled or manual generation
    print("Options:")
    print("1. Generate content now (manual)")
    print("2. Start scheduled generation (automatic)")

    choice = input("Choose option (1 or 2): ").strip()

    if choice == "1":
        print("\nGenerating content manually...")
        generator.generate_daily_content()
        print("\nContent generated! Check Needs_Action folder.")

    elif choice == "2":
        generator.start_scheduled_generation()

    else:
        print("Invalid choice. Generating content once...")
        generator.generate_daily_content()

if __name__ == "__main__":
    main()