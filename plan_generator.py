#!/usr/bin/env python3
"""
Plan Generation System - Silver Tier Requirement
Automatically creates Plan.md files when processing tasks from Needs_Action folder
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class PlanGenerator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.plans_path = self.vault_path / "Plans"
        self.done_path = self.vault_path / "Done"

        # Create directories if they don't exist
        self.plans_path.mkdir(parents=True, exist_ok=True)
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)

    def analyze_task_content(self, content: str, task_type: str) -> Dict:
        """Analyze task content and determine appropriate plan structure"""

        # Extract key information from content
        priority = "medium"
        if any(word in content.lower() for word in ["urgent", "asap", "critical", "emergency"]):
            priority = "high"
        elif any(word in content.lower() for word in ["later", "when possible", "low priority"]):
            priority = "low"

        # Determine complexity and steps needed
        complexity = "simple"
        estimated_time = "30 minutes"

        if task_type == "email":
            steps = self._generate_email_plan_steps(content)
            estimated_time = "15 minutes"
        elif task_type == "social_media":
            steps = self._generate_social_media_plan_steps(content)
            estimated_time = "20 minutes"
        elif task_type == "payment" or task_type == "invoice":
            steps = self._generate_financial_plan_steps(content)
            estimated_time = "45 minutes"
            complexity = "complex"
        elif task_type == "whatsapp":
            steps = self._generate_whatsapp_plan_steps(content)
            estimated_time = "10 minutes"
        else:
            steps = self._generate_generic_plan_steps(content)

        return {
            "priority": priority,
            "complexity": complexity,
            "estimated_time": estimated_time,
            "steps": steps,
            "requires_approval": self._requires_approval(task_type, content)
        }

    def _generate_email_plan_steps(self, content: str) -> List[Dict]:
        """Generate steps for email-related tasks"""
        steps = [
            {"task": "Analyze email content and context", "status": "pending", "estimated_time": "5 min"},
            {"task": "Draft appropriate response", "status": "pending", "estimated_time": "10 min"},
            {"task": "Review response for tone and accuracy", "status": "pending", "estimated_time": "3 min"},
            {"task": "Send response (requires approval)", "status": "pending", "estimated_time": "2 min"},
            {"task": "Log interaction in communication history", "status": "pending", "estimated_time": "2 min"}
        ]
        return steps

    def _generate_social_media_plan_steps(self, content: str) -> List[Dict]:
        """Generate steps for social media tasks"""
        steps = [
            {"task": "Research trending topics and hashtags", "status": "pending", "estimated_time": "5 min"},
            {"task": "Create engaging content draft", "status": "pending", "estimated_time": "10 min"},
            {"task": "Generate or select appropriate image", "status": "pending", "estimated_time": "5 min"},
            {"task": "Schedule post for optimal timing", "status": "pending", "estimated_time": "3 min"},
            {"task": "Monitor engagement and respond to comments", "status": "pending", "estimated_time": "ongoing"}
        ]
        return steps

    def _generate_financial_plan_steps(self, content: str) -> List[Dict]:
        """Generate steps for financial/payment tasks"""
        steps = [
            {"task": "Verify client/vendor information", "status": "pending", "estimated_time": "5 min"},
            {"task": "Calculate amounts and verify rates", "status": "pending", "estimated_time": "10 min"},
            {"task": "Generate invoice/payment document", "status": "pending", "estimated_time": "15 min"},
            {"task": "Review financial details for accuracy", "status": "pending", "estimated_time": "10 min"},
            {"task": "Send invoice/process payment (REQUIRES APPROVAL)", "status": "pending", "estimated_time": "5 min"},
            {"task": "Update accounting records", "status": "pending", "estimated_time": "5 min"},
            {"task": "Send confirmation to relevant parties", "status": "pending", "estimated_time": "3 min"}
        ]
        return steps

    def _generate_whatsapp_plan_steps(self, content: str) -> List[Dict]:
        """Generate steps for WhatsApp tasks"""
        steps = [
            {"task": "Analyze message context and urgency", "status": "pending", "estimated_time": "2 min"},
            {"task": "Craft appropriate response", "status": "pending", "estimated_time": "5 min"},
            {"task": "Send WhatsApp response", "status": "pending", "estimated_time": "1 min"},
            {"task": "Log conversation summary", "status": "pending", "estimated_time": "2 min"}
        ]
        return steps

    def _generate_generic_plan_steps(self, content: str) -> List[Dict]:
        """Generate generic steps for unknown task types"""
        steps = [
            {"task": "Analyze task requirements", "status": "pending", "estimated_time": "5 min"},
            {"task": "Research necessary information", "status": "pending", "estimated_time": "10 min"},
            {"task": "Execute primary task action", "status": "pending", "estimated_time": "15 min"},
            {"task": "Verify completion and quality", "status": "pending", "estimated_time": "5 min"},
            {"task": "Document results and next steps", "status": "pending", "estimated_time": "5 min"}
        ]
        return steps

    def _requires_approval(self, task_type: str, content: str) -> bool:
        """Determine if task requires human approval"""
        approval_keywords = ["payment", "invoice", "send", "post", "publish", "delete", "transfer"]
        high_value_indicators = ["$", "€", "£", "payment", "invoice", "contract"]

        if task_type in ["payment", "invoice", "financial"]:
            return True

        if any(keyword in content.lower() for keyword in approval_keywords):
            return True

        if any(indicator in content.lower() for indicator in high_value_indicators):
            return True

        return False

    def generate_plan_file(self, task_file: Path) -> Optional[Path]:
        """Generate a Plan.md file for a given task"""
        try:
            # Read task file
            task_content = task_file.read_text(encoding='utf-8')

            # Extract metadata if present
            metadata = {}
            if task_content.startswith('---'):
                parts = task_content.split('---', 2)
                if len(parts) >= 3:
                    # Parse YAML-like metadata
                    metadata_text = parts[1].strip()
                    for line in metadata_text.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metadata[key.strip()] = value.strip()
                    task_content = parts[2].strip()

            # Determine task type
            task_type = metadata.get('type', 'generic')
            if not task_type or task_type == 'generic':
                # Try to infer from filename
                filename = task_file.name.lower()
                if 'email' in filename:
                    task_type = 'email'
                elif 'whatsapp' in filename:
                    task_type = 'whatsapp'
                elif 'social' in filename or 'linkedin' in filename or 'facebook' in filename:
                    task_type = 'social_media'
                elif 'payment' in filename or 'invoice' in filename:
                    task_type = 'payment'

            # Analyze task and generate plan
            analysis = self.analyze_task_content(task_content, task_type)

            # Generate plan filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_filename = f"PLAN_{task_file.stem}_{timestamp}.md"
            plan_path = self.plans_path / plan_filename

            # Create plan content
            plan_content = self._create_plan_content(
                task_file.name,
                task_content,
                metadata,
                analysis
            )

            # Write plan file
            plan_path.write_text(plan_content, encoding='utf-8')

            print(f"Generated plan: {plan_path}")
            return plan_path

        except Exception as e:
            print(f"Error generating plan for {task_file}: {e}")
            return None

    def _create_plan_content(self, task_filename: str, task_content: str, metadata: Dict, analysis: Dict) -> str:
        """Create the actual plan content in markdown format"""

        timestamp = datetime.now().isoformat()

        # Create steps checklist
        steps_md = ""
        for i, step in enumerate(analysis['steps'], 1):
            status_icon = "⏳" if step['status'] == 'pending' else "✅"
            steps_md += f"- [ ] {status_icon} **Step {i}:** {step['task']} *(Est: {step['estimated_time']})*\n"

        # Create approval section if needed
        approval_section = ""
        if analysis['requires_approval']:
            approval_section = f"""
## 🔐 Approval Required

This task requires human approval before execution. Key actions that need approval:
- Any external communications (emails, messages, posts)
- Financial transactions or invoice generation
- Data modifications or deletions

**To approve:** Move this file to `/Approved/` folder after review.
**To reject:** Move this file to `/Rejected/` folder with comments.
"""

        plan_content = f"""---
type: execution_plan
source_task: {task_filename}
created: {timestamp}
priority: {analysis['priority']}
complexity: {analysis['complexity']}
estimated_time: {analysis['estimated_time']}
requires_approval: {analysis['requires_approval']}
status: pending
---

# 📋 Execution Plan: {task_filename}

## 📝 Original Task
```
{task_content[:500]}{'...' if len(task_content) > 500 else ''}
```

## 🎯 Objective
Process and complete the task according to established workflows and business rules.

## 📊 Task Analysis
- **Priority:** {analysis['priority'].upper()}
- **Complexity:** {analysis['complexity'].title()}
- **Estimated Time:** {analysis['estimated_time']}
- **Approval Required:** {'Yes' if analysis['requires_approval'] else 'No'}

## ✅ Execution Steps

{steps_md}

## 📈 Success Criteria
- [ ] All steps completed successfully
- [ ] Quality review passed
- [ ] Appropriate logging completed
- [ ] Follow-up actions identified (if any)

{approval_section}

## 📝 Notes
- Plan generated automatically by AI Employee System
- Review and modify steps as needed before execution
- Update step status as work progresses
- Move to `/Done/` when complete

## 🔄 Next Actions
1. Review plan for accuracy and completeness
2. Execute steps in order
3. Update status and log results
4. Archive completed plan

---
*Generated by Plan Generator v1.0 - {timestamp}*
"""

        return plan_content

    def process_needs_action_folder(self) -> List[Path]:
        """Process all tasks in Needs_Action folder and generate plans"""
        generated_plans = []

        if not self.needs_action_path.exists():
            print(f"Needs_Action folder not found: {self.needs_action_path}")
            return generated_plans

        # Find all task files
        task_files = list(self.needs_action_path.glob('*.md'))

        if not task_files:
            print("No tasks found in Needs_Action folder")
            return generated_plans

        print(f"Found {len(task_files)} tasks to process")

        for task_file in task_files:
            print(f"Processing task: {task_file.name}")

            # Check if plan already exists
            existing_plans = list(self.plans_path.glob(f"PLAN_{task_file.stem}_*.md"))
            if existing_plans:
                print(f"Plan already exists for {task_file.name}, skipping...")
                continue

            # Generate plan
            plan_path = self.generate_plan_file(task_file)
            if plan_path:
                generated_plans.append(plan_path)

        return generated_plans

    def start_monitoring(self):
        """Start monitoring Needs_Action folder for new tasks"""
        print("Starting Plan Generator monitoring...")
        print(f"Monitoring: {self.needs_action_path}")
        print(f"Plans will be saved to: {self.plans_path}")

        import time

        processed_files = set()

        while True:
            try:
                # Check for new files
                current_files = set(self.needs_action_path.glob('*.md'))
                new_files = current_files - processed_files

                if new_files:
                    print(f"Found {len(new_files)} new tasks")
                    for task_file in new_files:
                        plan_path = self.generate_plan_file(task_file)
                        if plan_path:
                            print(f"Generated plan: {plan_path.name}")

                    processed_files.update(new_files)

                time.sleep(30)  # Check every 30 seconds

            except KeyboardInterrupt:
                print("\nStopping Plan Generator...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)

def main():
    vault_path = "AI_Employee_Vault"
    generator = PlanGenerator(vault_path)

    print("Plan Generation System - Silver Tier")
    print("=" * 50)

    # Process existing tasks
    plans = generator.process_needs_action_folder()
    print(f"Generated {len(plans)} plans")

    # Start monitoring for new tasks
    generator.start_monitoring()

if __name__ == "__main__":
    main()