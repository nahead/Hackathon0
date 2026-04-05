# Plan Creation Agent Skill
# Creates structured Plan.md files for multi-step task execution

## Skill Description
Analyzes tasks in /Needs_Action folder and creates detailed execution plans with checkboxes and human approval workflows.

## Implementation

```python
# plan_creation_skill.py
import os
import json
from pathlib import Path
from datetime import datetime
import re

class PlanCreationSkill:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'

        # Ensure directories exist
        self.plans.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)

    def analyze_and_create_plans(self):
        """Analyze all items in Needs_Action and create execution plans"""
        created_plans = []

        try:
            # Get all action items
            action_files = list(self.needs_action.glob('*.md'))

            for action_file in action_files:
                try:
                    plan = self.create_plan_for_action(action_file)
                    if plan:
                        created_plans.append(plan)
                except Exception as e:
                    print(f"Error creating plan for {action_file}: {e}")

            return {
                "status": "success",
                "plans_created": len(created_plans),
                "plans": created_plans
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Plan creation failed: {e}"
            }

    def create_plan_for_action(self, action_file: Path):
        """Create a detailed plan for a specific action item"""
        try:
            # Read the action file
            content = action_file.read_text(encoding='utf-8')

            # Parse frontmatter
            frontmatter, body = self.parse_frontmatter(content)

            # Determine action type and create appropriate plan
            action_type = frontmatter.get('type', 'unknown')

            if action_type == 'email':
                plan = self.create_email_plan(frontmatter, body, action_file)
            elif action_type == 'whatsapp_urgent':
                plan = self.create_whatsapp_plan(frontmatter, body, action_file)
            elif action_type == 'file_drop':
                plan = self.create_file_processing_plan(frontmatter, body, action_file)
            else:
                plan = self.create_generic_plan(frontmatter, body, action_file)

            if plan:
                # Save the plan
                plan_file = self.save_plan(plan, action_file)
                return {
                    "action_file": str(action_file),
                    "plan_file": str(plan_file),
                    "plan_type": action_type,
                    "requires_approval": plan.get('requires_approval', False)
                }

        except Exception as e:
            print(f"Error creating plan for {action_file}: {e}")
            return None

    def create_email_plan(self, frontmatter: dict, body: str, action_file: Path):
        """Create plan for email processing"""
        sender = frontmatter.get('from', 'Unknown')
        subject = frontmatter.get('subject', 'No Subject')

        # Analyze email content to determine response type
        requires_approval = self.requires_human_approval(sender, subject, body)

        plan = {
            'title': f'Process Email: {subject}',
            'type': 'email_processing',
            'priority': frontmatter.get('priority', 'normal'),
            'requires_approval': requires_approval,
            'estimated_time': '5-10 minutes',
            'steps': [
                {
                    'step': 1,
                    'action': 'Read and analyze email content',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 2,
                    'action': 'Determine appropriate response type',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 3,
                    'action': 'Draft response email' if requires_approval else 'Send response email',
                    'status': 'pending',
                    'requires_approval': requires_approval,
                    'ai_enhanced': True
                },
                {
                    'step': 4,
                    'action': 'Update contact records if needed',
                    'status': 'pending',
                    'ai_enhanced': False
                },
                {
                    'step': 5,
                    'action': 'Archive email and move to Done',
                    'status': 'pending',
                    'ai_enhanced': False
                }
            ],
            'context': {
                'sender': sender,
                'subject': subject,
                'original_file': str(action_file)
            }
        }

        return plan

    def create_whatsapp_plan(self, frontmatter: dict, body: str, action_file: Path):
        """Create plan for WhatsApp message processing"""
        contact = frontmatter.get('contact', 'Unknown')
        keywords = frontmatter.get('keywords_triggered', '').split(', ')

        plan = {
            'title': f'Respond to Urgent WhatsApp: {contact}',
            'type': 'whatsapp_processing',
            'priority': 'high',
            'requires_approval': True,  # WhatsApp always requires approval
            'estimated_time': '3-5 minutes',
            'steps': [
                {
                    'step': 1,
                    'action': 'Open WhatsApp and read full message context',
                    'status': 'pending',
                    'ai_enhanced': False
                },
                {
                    'step': 2,
                    'action': 'Analyze urgency and determine response priority',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 3,
                    'action': 'Draft appropriate response message',
                    'status': 'pending',
                    'requires_approval': True,
                    'ai_enhanced': True
                },
                {
                    'step': 4,
                    'action': 'Send response via WhatsApp',
                    'status': 'pending',
                    'requires_approval': True,
                    'ai_enhanced': False
                },
                {
                    'step': 5,
                    'action': 'Create follow-up task if needed',
                    'status': 'pending',
                    'ai_enhanced': True
                }
            ],
            'context': {
                'contact': contact,
                'urgency_keywords': keywords,
                'original_file': str(action_file)
            }
        }

        return plan

    def create_file_processing_plan(self, frontmatter: dict, body: str, action_file: Path):
        """Create plan for file processing"""
        filename = frontmatter.get('original_name', 'Unknown file')
        file_size = frontmatter.get('size', 0)

        plan = {
            'title': f'Process File: {filename}',
            'type': 'file_processing',
            'priority': 'normal',
            'requires_approval': False,
            'estimated_time': '2-5 minutes',
            'steps': [
                {
                    'step': 1,
                    'action': 'Analyze file type and content',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 2,
                    'action': 'Determine processing requirements',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 3,
                    'action': 'Process file according to type',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 4,
                    'action': 'Store processed file in appropriate location',
                    'status': 'pending',
                    'ai_enhanced': False
                },
                {
                    'step': 5,
                    'action': 'Create summary and move to Done',
                    'status': 'pending',
                    'ai_enhanced': True
                }
            ],
            'context': {
                'filename': filename,
                'file_size': file_size,
                'original_file': str(action_file)
            }
        }

        return plan

    def create_generic_plan(self, frontmatter: dict, body: str, action_file: Path):
        """Create generic plan for unknown action types"""
        plan = {
            'title': f'Process Action: {action_file.stem}',
            'type': 'generic_processing',
            'priority': frontmatter.get('priority', 'normal'),
            'requires_approval': True,  # Generic actions require approval
            'estimated_time': '5-15 minutes',
            'steps': [
                {
                    'step': 1,
                    'action': 'Analyze action requirements',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 2,
                    'action': 'Research best approach',
                    'status': 'pending',
                    'ai_enhanced': True
                },
                {
                    'step': 3,
                    'action': 'Create detailed execution strategy',
                    'status': 'pending',
                    'requires_approval': True,
                    'ai_enhanced': True
                },
                {
                    'step': 4,
                    'action': 'Execute approved strategy',
                    'status': 'pending',
                    'requires_approval': True,
                    'ai_enhanced': True
                },
                {
                    'step': 5,
                    'action': 'Verify completion and document results',
                    'status': 'pending',
                    'ai_enhanced': True
                }
            ],
            'context': {
                'original_file': str(action_file),
                'action_type': frontmatter.get('type', 'unknown')
            }
        }

        return plan

    def requires_human_approval(self, sender: str, subject: str, body: str) -> bool:
        """Determine if email requires human approval"""
        # Check for sensitive keywords
        sensitive_keywords = [
            'payment', 'invoice', 'contract', 'legal', 'urgent',
            'confidential', 'meeting', 'call', 'complaint', 'refund'
        ]

        text_to_check = f"{sender} {subject} {body}".lower()

        # Check if sender is unknown (not in approved contacts)
        known_domains = ['gmail.com', 'company.com']  # Add your trusted domains
        sender_domain = sender.split('@')[-1] if '@' in sender else ''

        if sender_domain not in known_domains:
            return True

        # Check for sensitive content
        if any(keyword in text_to_check for keyword in sensitive_keywords):
            return True

        return False

    def save_plan(self, plan: dict, action_file: Path):
        """Save plan to Plans folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_filename = f"PLAN_{action_file.stem}_{timestamp}.md"
        plan_file = self.plans / plan_filename

        # Create plan content
        plan_content = f"""---
title: {plan['title']}
type: {plan['type']}
priority: {plan['priority']}
requires_approval: {plan['requires_approval']}
estimated_time: {plan['estimated_time']}
created: {datetime.now().isoformat()}
status: pending
original_action: {plan['context']['original_file']}
---

# {plan['title']}

## Plan Overview
**Type:** {plan['type']}
**Priority:** {plan['priority']}
**Estimated Time:** {plan['estimated_time']}
**Requires Approval:** {'Yes' if plan['requires_approval'] else 'No'}

## Execution Steps
"""

        for step in plan['steps']:
            status_icon = "⏳" if step['status'] == 'pending' else "✅"
            approval_note = " (REQUIRES APPROVAL)" if step.get('requires_approval') else ""
            ai_note = " [AI Enhanced]" if step.get('ai_enhanced') else ""

            plan_content += f"""
### Step {step['step']}: {step['action']}
- **Status:** {status_icon} {step['status']}{approval_note}
- **AI Enhanced:** {'Yes' if step.get('ai_enhanced') else 'No'}{ai_note}
"""

        plan_content += f"""

## Context Information
"""
        for key, value in plan['context'].items():
            plan_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"

        plan_content += f"""

## AI Instructions
This plan was automatically generated based on the action item analysis. Execute each step in order, ensuring approval steps are completed before proceeding. Update step status as you progress.

## Completion Criteria
- All steps marked as completed
- Original action file moved to /Done
- Results documented
- Any required approvals obtained
"""

        plan_file.write_text(plan_content, encoding='utf-8')

        # If plan requires approval, also create approval request
        if plan['requires_approval']:
            self.create_approval_request(plan, plan_file)

        return plan_file

    def create_approval_request(self, plan: dict, plan_file: Path):
        """Create approval request for plans requiring human oversight"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        approval_filename = f"APPROVAL_{plan_file.stem}_{timestamp}.md"
        approval_file = self.pending_approval / approval_filename

        approval_content = f"""---
type: plan_approval
plan_file: {plan_file}
priority: {plan['priority']}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Plan Approval Required

## Plan Details
**Title:** {plan['title']}
**Type:** {plan['type']}
**Priority:** {plan['priority']}
**Estimated Time:** {plan['estimated_time']}

## Steps Requiring Approval
"""

        approval_steps = [step for step in plan['steps'] if step.get('requires_approval')]
        for step in approval_steps:
            approval_content += f"- Step {step['step']}: {step['action']}\n"

        approval_content += f"""

## Context
Original action: {plan['context']['original_file']}

## Actions
- **To Approve:** Move this file to /Approved folder
- **To Reject:** Move this file to /Rejected folder
- **To Modify:** Edit the plan file directly, then approve

## AI Instructions
This plan contains steps that require human approval before execution. The plan will not proceed until approval is granted.
"""

        approval_file.write_text(approval_content, encoding='utf-8')

    def parse_frontmatter(self, content: str):
        """Parse YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}, content

        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return {}, content

            frontmatter_text = parts[1].strip()
            body = parts[2].strip()

            # Simple YAML parsing (for basic key: value pairs)
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

            return frontmatter, body

        except Exception as e:
            print(f"Error parsing frontmatter: {e}")
            return {}, content

def execute_plan_creation_skill(vault_path: str = None):
    """Execute the plan creation skill"""
    if not vault_path:
        vault_path = os.getenv('AI_EMPLOYEE_VAULT', './AI_Employee_Vault')

    skill = PlanCreationSkill(vault_path)
    result = skill.analyze_and_create_plans()

    return result

if __name__ == "__main__":
    result = execute_plan_creation_skill()
    print(json.dumps(result, indent=2))
```

## Skill Configuration

```json
{
  "name": "plan_creation",
  "description": "Analyze action items and create detailed execution plans",
  "command": "python plan_creation_skill.py",
  "parameters": {
    "vault_path": {
      "type": "string",
      "description": "Path to Obsidian vault",
      "default": "./AI_Employee_Vault"
    }
  }
}
```

## Usage in Claude Code

```
/plan_creation
```

This will analyze all items in /Needs_Action and create structured execution plans with human approval workflows where needed.