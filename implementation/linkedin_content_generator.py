#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Content Generator - Silver Tier Requirement
Automatically generates LinkedIn posts for business lead generation
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
PENDING_APPROVAL_FOLDER = VAULT_PATH / "Pending_Approval"
BUSINESS_GOALS_FILE = VAULT_PATH / "Business_Goals.md"

# Content templates for different post types
CONTENT_TEMPLATES = {
    "business_tip": [
        "💡 Business Tip: {tip}\n\nThis simple strategy has helped countless entrepreneurs scale their operations. What's your go-to business hack?\n\n#BusinessGrowth #Entrepreneurship #SmallBusiness",
        "🚀 Want to grow your business? Here's what works:\n\n{tip}\n\nImplement this today and watch your results improve. Drop a comment if you've tried this!\n\n#BusinessStrategy #Growth #Success",
        "📈 Quick win for business owners:\n\n{tip}\n\nThis approach has proven results. What strategies are working for you?\n\n#BusinessTips #Entrepreneur #Leadership"
    ],
    "industry_insight": [
        "🔍 Industry Insight:\n\n{insight}\n\nStaying ahead means adapting to change. How is your business preparing for the future?\n\n#Industry #Innovation #BusinessTrends",
        "📊 Market Update:\n\n{insight}\n\nUnderstanding these trends is crucial for staying competitive. What trends are you watching?\n\n#MarketTrends #Business #Strategy",
        "💼 Professional Insight:\n\n{insight}\n\nKnowledge is power in business. Share your thoughts below!\n\n#ProfessionalDevelopment #BusinessInsights #Growth"
    ],
    "value_content": [
        "📚 Free Resource Alert!\n\n{value}\n\nI'm sharing this because I believe in helping fellow entrepreneurs succeed. Save this post for later!\n\n#FreeResource #BusinessHelp #Entrepreneurship",
        "🎯 How to {value}\n\nStep-by-step guide:\n1. Start with clear goals\n2. Implement systematically\n3. Measure and adjust\n\nNeed help? Let's connect!\n\n#HowTo #BusinessGuide #Success",
        "✨ Pro Tip:\n\n{value}\n\nThis has saved me countless hours. Hope it helps you too!\n\n#ProTip #Productivity #Business"
    ],
    "achievement": [
        "🎉 Milestone Alert!\n\n{achievement}\n\nGrateful for this journey and everyone who supported along the way. Here's to continued growth!\n\n#Milestone #Success #Gratitude",
        "✅ Achievement Unlocked:\n\n{achievement}\n\nProof that consistency and dedication pay off. What goals are you working toward?\n\n#Achievement #BusinessSuccess #Growth",
        "🏆 Celebrating:\n\n{achievement}\n\nEvery win matters, big or small. Keep pushing forward!\n\n#Celebration #Success #Entrepreneurship"
    ],
    "engagement": [
        "❓ Question for my network:\n\n{question}\n\nI'd love to hear your perspectives. Drop your thoughts in the comments!\n\n#Networking #Discussion #Business",
        "🤔 Let's discuss:\n\n{question}\n\nYour insights could help someone else. Share your experience below!\n\n#Community #BusinessDiscussion #Learning",
        "💬 Quick poll:\n\n{question}\n\nComment your answer - curious to see what the consensus is!\n\n#Poll #Engagement #Business"
    ]
}

# Content ideas for each template type
CONTENT_IDEAS = {
    "business_tip": [
        "Focus on solving one problem exceptionally well before expanding",
        "Automate repetitive tasks to free up time for strategic thinking",
        "Build relationships before you need them - networking is a long game",
        "Track your metrics weekly, not monthly - faster feedback means faster growth",
        "Invest in systems, not just people - scalability comes from processes"
    ],
    "industry_insight": [
        "AI automation is no longer optional - businesses that adapt now will lead tomorrow",
        "Remote work has shifted from trend to standard - companies must optimize for distributed teams",
        "Customer experience is the new competitive advantage in saturated markets",
        "Data-driven decision making separates growing businesses from stagnant ones",
        "Sustainability isn't just ethics - it's becoming a business requirement"
    ],
    "value_content": [
        "improve your email response time by 80% with simple automation",
        "create a content calendar that actually gets followed",
        "build a lead generation system that works while you sleep",
        "optimize your LinkedIn profile for maximum visibility",
        "automate your business reporting and save 10 hours per week"
    ],
    "achievement": [
        "Just helped our 50th client automate their business operations!",
        "Reached 1,000 connections with amazing entrepreneurs and business leaders",
        "Successfully implemented AI automation that saved 20 hours per week",
        "Launched our new service and got 10 clients in the first week",
        "Hit our quarterly revenue goal 2 weeks early!"
    ],
    "engagement": [
        "What's the biggest challenge you're facing in your business right now?",
        "If you could automate one task in your business, what would it be?",
        "What's one business lesson you wish you learned earlier?",
        "How do you stay productive when motivation is low?",
        "What's your best advice for someone starting their first business?"
    ]
}

class LinkedInContentGenerator:
    """Generate LinkedIn content for business lead generation"""

    def __init__(self):
        self.vault_path = VAULT_PATH
        self.pending_folder = PENDING_APPROVAL_FOLDER
        self.pending_folder.mkdir(exist_ok=True)

    def read_business_goals(self):
        """Read business goals from vault"""
        if BUSINESS_GOALS_FILE.exists():
            return BUSINESS_GOALS_FILE.read_text(encoding='utf-8')
        return ""

    def generate_post(self, post_type):
        """Generate a single LinkedIn post"""
        template = random.choice(CONTENT_TEMPLATES[post_type])
        idea = random.choice(CONTENT_IDEAS[post_type])

        # Format the template with the idea
        if post_type == "business_tip":
            content = template.format(tip=idea)
        elif post_type == "industry_insight":
            content = template.format(insight=idea)
        elif post_type == "value_content":
            content = template.format(value=idea)
        elif post_type == "achievement":
            content = template.format(achievement=idea)
        elif post_type == "engagement":
            content = template.format(question=idea)

        return content

    def create_approval_file(self, content, post_type):
        """Create approval file for LinkedIn post"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_POST_{timestamp}_{post_type}.md"
        filepath = self.pending_folder / filename

        # Create frontmatter
        frontmatter = f"""---
type: linkedin_post
post_type: {post_type}
created: {datetime.now().isoformat()}
status: pending_approval
requires_approval: true
---

"""

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(content)

        print(f"[OK] Created: {filename}")
        return filepath

    def generate_daily_content(self):
        """Generate daily LinkedIn content based on day of week"""
        day_of_week = datetime.now().weekday()

        # Monday: Business tip
        # Tuesday: Industry insight
        # Wednesday: Value content
        # Thursday: Achievement
        # Friday: Engagement

        post_types = {
            0: "business_tip",      # Monday
            1: "industry_insight",  # Tuesday
            2: "value_content",     # Wednesday
            3: "achievement",       # Thursday
            4: "engagement",        # Friday
            5: "business_tip",      # Saturday
            6: "engagement"         # Sunday
        }

        post_type = post_types[day_of_week]
        print(f"[GENERATE] Creating {post_type} post for {datetime.now().strftime('%A')}")

        content = self.generate_post(post_type)
        filepath = self.create_approval_file(content, post_type)

        print(f"[CONTENT] Preview:\n{content[:150]}...")
        return filepath

    def generate_multiple_posts(self, count=3):
        """Generate multiple posts for approval"""
        print(f"[GENERATE] Creating {count} LinkedIn posts...")

        post_types = list(CONTENT_TEMPLATES.keys())
        generated = []

        for i in range(count):
            post_type = post_types[i % len(post_types)]
            content = self.generate_post(post_type)
            filepath = self.create_approval_file(content, post_type)
            generated.append(filepath)

        print(f"[OK] Generated {len(generated)} posts")
        return generated

def main():
    """Main entry point"""
    print("="*70)
    print("LINKEDIN CONTENT GENERATOR - SILVER TIER")
    print("="*70)

    generator = LinkedInContentGenerator()

    # Check command line arguments
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "daily":
            # Generate daily content
            generator.generate_daily_content()
        elif sys.argv[1] == "multiple":
            # Generate multiple posts
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            generator.generate_multiple_posts(count)
    else:
        # Default: generate daily content
        generator.generate_daily_content()

    print("\n" + "="*70)
    print("[DONE] Content generation complete")
    print("="*70)

if __name__ == "__main__":
    main()
