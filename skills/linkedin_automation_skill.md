# LinkedIn Business Automation Agent Skill
# Automates LinkedIn posting for business development and lead generation

## Skill Description
Automatically post business content on LinkedIn to generate sales leads and maintain professional presence.

## Implementation

```python
# linkedin_automation_skill.py
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime
import random

class LinkedInAutomationSkill:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.session_path = Path(session_path)

        # Business post templates
        self.post_templates = [
            "🚀 Excited to share insights about {topic}. What's your experience with {question}?",
            "💡 Just learned something valuable about {topic}. Key takeaway: {insight}",
            "🎯 Working on {project}. The biggest challenge? {challenge}. How do you handle this?",
            "📈 Seeing great results with {strategy}. Anyone else trying similar approaches?",
            "🤝 Looking to connect with professionals in {industry}. What trends are you seeing?"
        ]

    def create_business_post(self, topic: str = None, industry: str = None):
        """Create and post business content on LinkedIn"""
        try:
            # Read business context from vault
            business_context = self.get_business_context()

            if not topic:
                topic = business_context.get('current_focus', 'AI automation')

            if not industry:
                industry = business_context.get('industry', 'technology')

            # Generate post content
            template = random.choice(self.post_templates)
            post_content = self.generate_post_content(template, topic, industry)

            # Post to LinkedIn
            result = self.post_to_linkedin(post_content)

            # Log the activity
            self.log_linkedin_activity(post_content, result)

            return result

        except Exception as e:
            return {
                "status": "error",
                "message": f"LinkedIn posting failed: {e}"
            }

    def get_business_context(self):
        """Read business context from vault files"""
        context = {}

        try:
            # Read Company Handbook
            handbook_path = self.vault_path / 'Company_Handbook.md'
            if handbook_path.exists():
                handbook_content = handbook_path.read_text(encoding='utf-8')
                # Extract key business info (simplified)
                if 'industry:' in handbook_content.lower():
                    lines = handbook_content.split('\n')
                    for line in lines:
                        if 'industry:' in line.lower():
                            context['industry'] = line.split(':')[1].strip()
                            break

            # Read current business goals
            goals_path = self.vault_path / 'Business_Goals.md'
            if goals_path.exists():
                goals_content = goals_path.read_text(encoding='utf-8')
                # Extract current focus
                if 'current focus' in goals_content.lower():
                    context['current_focus'] = 'business automation'

        except Exception as e:
            print(f"Error reading business context: {e}")

        return context

    def generate_post_content(self, template: str, topic: str, industry: str):
        """Generate engaging LinkedIn post content"""

        # Content variations based on topic
        content_map = {
            'AI automation': {
                'question': 'implementing AI in your workflows',
                'insight': 'AI can handle 80% of routine tasks, freeing time for strategy',
                'project': 'AI employee automation systems',
                'challenge': 'balancing automation with human oversight',
                'strategy': 'gradual AI integration'
            },
            'business automation': {
                'question': 'automating your business processes',
                'insight': 'automation ROI shows up in weeks, not months',
                'project': 'end-to-end business automation',
                'challenge': 'choosing the right processes to automate first',
                'strategy': 'process mapping before automation'
            }
        }

        content_vars = content_map.get(topic, content_map['AI automation'])

        # Fill template with relevant content
        post_content = template.format(
            topic=topic,
            industry=industry,
            **content_vars
        )

        # Add relevant hashtags
        hashtags = f"\n\n#{topic.replace(' ', '')} #business #automation #productivity #linkedin"

        return post_content + hashtags

    def post_to_linkedin(self, content: str):
        """Post content to LinkedIn using Playwright"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/feed/', timeout=30000)

                # Wait for LinkedIn to load
                page.wait_for_selector('[data-testid="share-box-feed-entry"]', timeout=20000)

                # Click on "Start a post" button
                page.click('[data-testid="share-box-feed-entry"]')

                # Wait for post editor
                page.wait_for_selector('[data-testid="share-creation-state-editor"]', timeout=10000)

                # Type the content
                editor = page.locator('[data-testid="share-creation-state-editor"]')
                editor.fill(content)

                # Wait a moment for content to be processed
                page.wait_for_timeout(2000)

                # Click Post button
                page.click('[data-testid="share-creation-state-submit-button"]')

                # Wait for post to be published
                page.wait_for_timeout(3000)

                browser.close()

                return {
                    "status": "success",
                    "message": "LinkedIn post published successfully",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to post to LinkedIn: {e}"
            }

    def log_linkedin_activity(self, content: str, result: dict):
        """Log LinkedIn activity to vault"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            log_content = f"""---
type: linkedin_post
timestamp: {datetime.now().isoformat()}
status: {result['status']}
---

## LinkedIn Business Post

**Status:** {result['status']}
**Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### Content Posted:
{content}

### Result:
{result.get('message', 'No message')}

### Business Impact:
- Professional presence maintained
- Potential lead generation
- Industry engagement
- Brand visibility increased
"""

            log_path = self.done / f'LINKEDIN_POST_{timestamp}.md'
            log_path.write_text(log_content, encoding='utf-8')

        except Exception as e:
            print(f"Error logging LinkedIn activity: {e}")

def execute_linkedin_automation_skill(vault_path: str = None, session_path: str = None, topic: str = None):
    """Execute LinkedIn business automation skill"""
    if not vault_path:
        vault_path = os.getenv('AI_EMPLOYEE_VAULT', './AI_Employee_Vault')

    if not session_path:
        session_path = os.getenv('LINKEDIN_SESSION_PATH', './.linkedin_session')

    skill = LinkedInAutomationSkill(vault_path, session_path)
    result = skill.create_business_post(topic=topic)

    return result

if __name__ == "__main__":
    result = execute_linkedin_automation_skill()
    print(json.dumps(result, indent=2))
```

## Skill Configuration

```json
{
  "name": "linkedin_automation",
  "description": "Automatically post business content on LinkedIn for lead generation",
  "command": "python linkedin_automation_skill.py",
  "parameters": {
    "vault_path": {
      "type": "string",
      "description": "Path to Obsidian vault",
      "default": "./AI_Employee_Vault"
    },
    "session_path": {
      "type": "string",
      "description": "Path to LinkedIn session data",
      "default": "./.linkedin_session"
    },
    "topic": {
      "type": "string",
      "description": "Topic for the LinkedIn post",
      "default": "AI automation"
    }
  }
}
```

## Usage in Claude Code

```
/linkedin_automation topic="business automation"
```

This will create and post engaging business content on LinkedIn to generate leads and maintain professional presence.