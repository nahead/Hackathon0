#!/usr/bin/env python3
"""
Test LinkedIn Content Creation
Tests content generation for LinkedIn posts
"""

import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_linkedin_content():
    """Generate LinkedIn post content"""
    print("[TEST] Testing LinkedIn Content Generation...")

    # Sample business context
    business_context = {
        "company": "AI Employee Solutions",
        "industry": "AI Automation",
        "recent_achievement": "Completed Platinum tier hackathon with 100% requirements",
        "target_audience": "Business owners and developers"
    }

    # Generate content
    content_templates = [
        {
            "type": "achievement",
            "content": f"""Exciting milestone achieved!

We've just completed our AI Employee system with 100% of all hackathon requirements met - Bronze, Silver, Gold, and Platinum tiers!

Key achievements:
- 24/7 cloud deployment
- 15 agent skills implemented
- Real-time email monitoring
- Human-in-the-loop approval workflow

This autonomous system can now handle business operations around the clock.

#AI #Automation #Innovation #TechAchievement

What's your biggest automation challenge? Let's discuss in the comments!
"""
        },
        {
            "type": "educational",
            "content": f"""Did you know?

An AI Employee can work 8,760 hours per year vs a human's 2,000 hours.

That's a 4.4x productivity multiplier!

Cost per task drops from ~$5 to ~$0.50 - an 85-90% cost saving.

This is why autonomous AI systems are transforming business operations in 2026.

#AIEmployee #BusinessAutomation #Productivity

Are you leveraging AI in your business? Share your experience!
"""
        },
        {
            "type": "technical",
            "content": f"""Tech Stack Spotlight

Building an autonomous AI Employee requires:

- Claude Code - Reasoning engine
- Obsidian - Knowledge base
- Git - Offline coordination
- MCP Servers - External actions
- Cloud Deployment - 24/7 operation

The result? A system that monitors emails, creates drafts, and handles approvals autonomously.

#TechStack #AIEngineering #CloudComputing

What's your favorite AI tool? Drop it below!
"""
        }
    ]

    print("\n[CONTENT] Generated LinkedIn Content:\n")

    for i, template in enumerate(content_templates, 1):
        print(f"{'='*60}")
        print(f"POST {i}: {template['type'].upper()}")
        print(f"{'='*60}")
        print(template['content'])
        print()

    return content_templates

def create_approval_file(content_templates):
    """Create approval files for LinkedIn posts"""
    print("[TEST] Creating Approval Files...")

    vault_path = Path("AI_Employee_Vault/Pending_Approval")
    vault_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    for i, template in enumerate(content_templates, 1):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}_{i}.md"
        filepath = vault_path / filename

        approval_content = f"""---
type: linkedin_post
post_type: {template['type']}
created: {datetime.now().isoformat()}
status: pending
---

## LinkedIn Post Content

```
{template['content']}
```

## Post Details
- Type: {template['type']}
- Character Count: {len(template['content'])}
- Hashtags: {len([tag for tag in template['content'].split() if tag.startswith('#')])}

## To Approve
Move this file to AI_Employee_Vault/Approved/ folder.

## To Reject
Move this file to AI_Employee_Vault/Rejected/ folder or delete it.

## To Edit
Modify the content above and keep in Pending_Approval for review.
"""

        filepath.write_text(approval_content, encoding='utf-8')
        created_files.append(filename)
        print(f"[OK] Created: {filename}")

    return created_files

def show_usage_instructions():
    """Show how to use the generated content"""
    print("\n" + "="*60)
    print("[LIST] NEXT STEPS")
    print("="*60)
    print("""
1. Review the generated content above
2. Check approval files in: AI_Employee_Vault/Pending_Approval/
3. To approve a post:
   - Move the file to: AI_Employee_Vault/Approved/
4. To test posting:
   - Run: python test_linkedin_poster.py
5. To use with Claude Code:
   - Use the linkedin-manager skill
   - Point Claude to the approval files

TIP: You can edit the content in the approval files before approving!
""")

if __name__ == "__main__":
    print("=" * 60)
    print("LINKEDIN CONTENT CREATION TEST")
    print("=" * 60)

    # Generate content
    content_templates = generate_linkedin_content()

    # Create approval files
    created_files = create_approval_file(content_templates)

    # Show instructions
    show_usage_instructions()

    print("\n" + "=" * 60)
    print(f"[OK] CONTENT GENERATION COMPLETE")
    print(f"   Created {len(created_files)} approval files")
    print("=" * 60)
