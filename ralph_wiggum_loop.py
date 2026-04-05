#!/usr/bin/env python3
"""
Ralph Wiggum Autonomous Loop - Gold Tier Requirement
Simple, continuous autonomous agent that manages business operations
Named after Ralph Wiggum for its simple but effective approach
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import subprocess
import random

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

class RalphWiggumLoop:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "Config" / "ralph_config.json"
        self.logs_path = self.vault_path / "Logs"
        self.state_path = self.vault_path / "State"

        # Create directories
        for path in [self.config_path.parent, self.logs_path, self.state_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'ralph_loop.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

        # State management
        self.state_file = self.state_path / "ralph_state.json"
        self.state = self.load_state()

        # Loop control
        self.running = False
        self.loop_count = 0
        self.last_actions = []

        # Simple decision rules (Ralph-like simplicity)
        self.decision_rules = {
            "email_check": self.check_emails,
            "social_media_post": self.handle_social_media,
            "task_management": self.manage_tasks,
            "financial_check": self.check_finances,
            "health_monitor": self.monitor_system_health,
            "content_generation": self.generate_content,
            "client_followup": self.follow_up_clients,
            "daily_briefing": self.create_daily_briefing
        }

        # Ralph's simple phrases for logging
        self.ralph_phrases = [
            "I'm helping!",
            "Me fail English? That's unpossible!",
            "I bent my Wookiee!",
            "Hi Super Nintendo Chalmers!",
            "I'm a brick!",
            "My cat's breath smells like cat food!",
            "I'm learnding!",
            "That's where I saw the leprechaun!"
        ]

    def load_config(self) -> Dict:
        """Load Ralph's configuration"""
        default_config = {
            "loop_interval_seconds": 300,  # 5 minutes
            "max_actions_per_loop": 3,
            "working_hours": {
                "start": "08:00",
                "end": "18:00"
            },
            "enabled_modules": [
                "email_check",
                "social_media_post",
                "task_management",
                "financial_check",
                "health_monitor",
                "content_generation",
                "client_followup",
                "daily_briefing"
            ],
            "action_probabilities": {
                "email_check": 0.8,
                "social_media_post": 0.3,
                "task_management": 0.9,
                "financial_check": 0.4,
                "health_monitor": 0.6,
                "content_generation": 0.2,
                "client_followup": 0.5,
                "daily_briefing": 0.1
            },
            "ralph_mode": True,  # Enable Ralph-like logging
            "auto_approve_safe_actions": True,
            "max_daily_social_posts": 3,
            "max_daily_emails": 10,
            "use_playwright_posting": True,  # Enable direct Playwright posting
            "playwright_mcp_url": "http://localhost:8808",  # Playwright MCP server URL
            "linkedin_automation_enabled": True,  # Enable LinkedIn automation
            "social_media_platforms": ["linkedin"],  # Supported platforms
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
        """Save configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def load_state(self) -> Dict:
        """Load Ralph's state"""
        default_state = {
            "last_run": None,
            "total_loops": 0,
            "actions_today": {},
            "last_daily_briefing": None,
            "last_social_post": None,
            "last_email_check": None,
            "errors_today": 0,
            "successful_actions_today": 0
        }

        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                # Reset daily counters if it's a new day
                if state.get('last_run'):
                    last_run_date = datetime.fromisoformat(state['last_run']).date()
                    if last_run_date != datetime.now().date():
                        state['actions_today'] = {}
                        state['errors_today'] = 0
                        state['successful_actions_today'] = 0
                return state
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")
                return default_state
        else:
            return default_state

    def save_state(self):
        """Save Ralph's state"""
        try:
            self.state['last_run'] = datetime.now().isoformat()
            self.state['total_loops'] = self.loop_count

            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")

    def ralph_log(self, message: str, level: str = "info"):
        """Log message with Ralph's personality"""
        if self.config.get("ralph_mode", True):
            ralph_phrase = random.choice(self.ralph_phrases)
            full_message = f"[Ralph]: {ralph_phrase} - {message}"
        else:
            full_message = message

        if level == "info":
            self.logger.info(full_message)
        elif level == "error":
            self.logger.error(full_message)
        elif level == "warning":
            self.logger.warning(full_message)

    def is_working_hours(self) -> bool:
        """Check if it's during working hours"""
        now = datetime.now()
        start_time = datetime.strptime(self.config["working_hours"]["start"], "%H:%M").time()
        end_time = datetime.strptime(self.config["working_hours"]["end"], "%H:%M").time()

        return start_time <= now.time() <= end_time

    async def run_autonomous_loop(self):
        """Main autonomous loop - Ralph's continuous operation"""
        self.running = True
        self.ralph_log("Starting autonomous loop! I'm gonna be the best AI employee!")

        while self.running:
            try:
                self.loop_count += 1
                loop_start = datetime.now()

                self.ralph_log(f"Loop #{self.loop_count} starting - I'm working hard!")

                # Decide what actions to take this loop
                actions_to_take = self.decide_actions()

                # Execute actions
                for action in actions_to_take:
                    try:
                        await self.execute_action(action)
                        self.state['successful_actions_today'] += 1
                    except Exception as e:
                        self.ralph_log(f"Action {action} failed: {e}", "error")
                        self.state['errors_today'] += 1

                # Update state
                self.save_state()

                # Log loop completion
                loop_duration = (datetime.now() - loop_start).total_seconds()
                self.ralph_log(f"Loop #{self.loop_count} completed in {loop_duration:.1f}s - I did good!")

                # Wait for next loop
                await asyncio.sleep(self.config["loop_interval_seconds"])

            except KeyboardInterrupt:
                self.ralph_log("Stopping loop - Bye bye!")
                break
            except Exception as e:
                self.ralph_log(f"Loop error: {e}", "error")
                self.state['errors_today'] += 1
                await asyncio.sleep(60)  # Wait a minute before retrying

        self.running = False

    def decide_actions(self) -> List[str]:
        """Decide what actions to take this loop (Ralph's simple decision making)"""
        actions = []

        # Simple probability-based decisions
        for module, probability in self.config["action_probabilities"].items():
            if module not in self.config["enabled_modules"]:
                continue

            # Check daily limits
            if self.check_daily_limits(module):
                continue

            # Simple random decision (Ralph-like)
            if random.random() < probability:
                actions.append(module)

        # Limit actions per loop
        max_actions = self.config["max_actions_per_loop"]
        if len(actions) > max_actions:
            actions = random.sample(actions, max_actions)

        # Always check emails if it's been a while
        if "email_check" not in actions and self.should_force_email_check():
            actions.append("email_check")

        # Always do daily briefing if it's morning and not done today
        if self.should_do_daily_briefing():
            actions.append("daily_briefing")

        return actions

    def check_daily_limits(self, action: str) -> bool:
        """Check if daily limits are reached for an action"""
        today = datetime.now().date().isoformat()
        action_count = self.state["actions_today"].get(f"{action}_{today}", 0)

        limits = {
            "social_media_post": self.config["max_daily_social_posts"],
            "email_check": self.config["max_daily_emails"]
        }

        limit = limits.get(action, 999)  # No limit for most actions
        return action_count >= limit

    def should_force_email_check(self) -> bool:
        """Check if we should force an email check"""
        if not self.state.get("last_email_check"):
            return True

        last_check = datetime.fromisoformat(self.state["last_email_check"])
        return (datetime.now() - last_check).total_seconds() > 1800  # 30 minutes

    def should_do_daily_briefing(self) -> bool:
        """Check if we should do daily briefing"""
        now = datetime.now()

        # Only in morning hours
        if now.hour < 8 or now.hour > 10:
            return False

        # Check if already done today
        if self.state.get("last_daily_briefing"):
            last_briefing = datetime.fromisoformat(self.state["last_daily_briefing"])
            if last_briefing.date() == now.date():
                return False

        return True

    async def execute_action(self, action: str):
        """Execute a specific action"""
        self.ralph_log(f"Executing action: {action}")

        if action in self.decision_rules:
            await self.decision_rules[action]()

            # Update action count
            today = datetime.now().date().isoformat()
            action_key = f"{action}_{today}"
            self.state["actions_today"][action_key] = self.state["actions_today"].get(action_key, 0) + 1

        else:
            self.ralph_log(f"Unknown action: {action}", "warning")

    async def check_emails(self):
        """Check and process emails"""
        try:
            self.ralph_log("Checking emails - I love mail!")

            # Simulate email checking (in real implementation, would use email MCP server)
            unread_count = random.randint(0, 5)

            if unread_count > 0:
                self.ralph_log(f"Found {unread_count} unread emails - I'll help!")

                # Create tasks for email responses
                for i in range(min(unread_count, 3)):  # Limit to 3 emails per check
                    await self.create_email_response_task(f"email_{i+1}")

            self.state["last_email_check"] = datetime.now().isoformat()

        except Exception as e:
            self.ralph_log(f"Email check failed: {e}", "error")

    async def handle_social_media(self):
        """Handle social media posting with Playwright integration"""
        try:
            self.ralph_log("Time for social media - I'm gonna be famous!")

            # Check if we should use direct Playwright posting or approval workflow
            use_playwright = self.config.get("use_playwright_posting", False)

            if use_playwright:
                # Direct Playwright posting
                await self.post_via_playwright()
            else:
                # Traditional approval workflow
                await self.create_social_media_approval_workflow()

            self.state["last_social_post"] = datetime.now().isoformat()

        except Exception as e:
            self.ralph_log(f"Social media handling failed: {e}", "error")

    async def post_via_playwright(self):
        """Post directly to LinkedIn using Playwright automation"""
        try:
            self.ralph_log("Using Playwright automation for LinkedIn posting!")

            # Simple content ideas for Ralph
            content_ideas = [
                "🚀 Exciting developments in AI automation are transforming how businesses operate!\n\nKey benefits we're seeing:\n✅ Real-time performance tracking\n✅ Streamlined workflow processes\n✅ Enhanced productivity metrics\n\nThe future of business efficiency is here. AI employees are not replacing humans - they're amplifying our capabilities!\n\n#AIAutomation #BusinessEfficiency #Innovation #Productivity",

                "💡 Just completed another successful automation workflow!\n\nToday's achievements:\n✅ Processed client communications\n✅ Generated business insights\n✅ Optimized task management\n\nAutomation isn't about replacing human creativity - it's about freeing us to focus on what matters most: strategic growth and innovation.\n\n#Automation #BusinessGrowth #Efficiency #Innovation",

                "📈 Reflecting on the power of AI-driven business operations!\n\nWhat we've learned:\n✅ Consistency drives results\n✅ Automation enables scalability\n✅ Human oversight ensures quality\n\nThe best AI systems don't work alone - they work alongside humans to create something greater than the sum of their parts.\n\n#AIBusiness #Productivity #Innovation #TeamWork"
            ]

            content = random.choice(content_ideas)

            # Import and use LinkedIn automation
            try:
                import sys
                sys.path.append('.')
                from linkedin_automation_demo import LinkedInAutomation

                # Create automation instance
                linkedin = LinkedInAutomation()

                # Execute posting workflow
                self.ralph_log("Starting LinkedIn automation workflow...")
                results = linkedin.create_linkedin_post(content)

                # Check results
                success_count = sum(1 for step, result in results if result and not result.get('isError'))
                total_steps = len(results)

                if success_count >= 5:  # Minimum successful steps
                    self.ralph_log(f"LinkedIn post successful! ({success_count}/{total_steps} steps)", "success")

                    # Log the successful post
                    await self.log_successful_post(content, "linkedin_playwright")
                else:
                    self.ralph_log(f"LinkedIn automation partially failed: {success_count}/{total_steps} steps", "warning")
                    # Fall back to approval workflow
                    await self.create_social_media_approval_workflow()

            except ImportError:
                self.ralph_log("Playwright automation not available, using approval workflow", "warning")
                await self.create_social_media_approval_workflow()

        except Exception as e:
            self.ralph_log(f"Playwright posting failed: {e}", "error")
            # Fall back to approval workflow
            await self.create_social_media_approval_workflow()

    async def create_social_media_approval_workflow(self):
        """Create social media approval request (traditional workflow)"""
        # Simple content ideas
        content_ideas = [
            "Working hard on exciting projects! 🚀",
            "Another productive day in the books! 📈",
            "Innovation never stops! 💡",
            "Building the future, one task at a time! 🔧",
            "Grateful for another day of growth! 🌱"
        ]

        content = random.choice(content_ideas)

        # Create approval request for social media post
        await self.create_social_media_approval(content)

    async def log_successful_post(self, content: str, method: str):
        """Log successful social media post"""
        log_file = self.vault_path / "Archive" / f"LINKEDIN_POST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        log_content = f"""---
type: linkedin_post_completed
timestamp: {datetime.now().isoformat()}
method: {method}
created_by: ralph_loop
auto_posted: true
---

# LinkedIn Post - Successfully Posted

**Posted:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Method:** {method}
**Created by:** Ralph Wiggum Autonomous Loop

## Content Posted:
```
{content}
```

## Status:
✅ Successfully posted to LinkedIn via Playwright automation

---
*Posted automatically by Ralph Wiggum Loop*
"""

        log_file.write_text(log_content, encoding='utf-8')
        self.ralph_log(f"Logged successful post: {log_file.name}")

    async def manage_tasks(self):
        """Manage and organize tasks"""
        try:
            self.ralph_log("Managing tasks - I'm organized!")

            # Check for overdue tasks
            tasks_path = self.vault_path / "Tasks" / "tasks.json"
            if tasks_path.exists():
                with open(tasks_path, 'r') as f:
                    tasks = json.load(f)

                overdue_count = 0
                now = datetime.now()

                for task in tasks:
                    if task.get('due_date') and task.get('status') != 'completed':
                        due_date = datetime.fromisoformat(task['due_date'])
                        if due_date < now:
                            overdue_count += 1

                if overdue_count > 0:
                    self.ralph_log(f"Found {overdue_count} overdue tasks - I'll make a note!")
                    await self.create_overdue_task_alert(overdue_count)

        except Exception as e:
            self.ralph_log(f"Task management failed: {e}", "error")

    async def check_finances(self):
        """Check financial status"""
        try:
            self.ralph_log("Checking money stuff - I can count!")

            # Simulate financial check
            outstanding_invoices = random.randint(0, 3)

            if outstanding_invoices > 0:
                self.ralph_log(f"Found {outstanding_invoices} outstanding invoices - Money is important!")
                await self.create_invoice_followup_task(outstanding_invoices)

        except Exception as e:
            self.ralph_log(f"Financial check failed: {e}", "error")

    async def monitor_system_health(self):
        """Monitor system health"""
        try:
            self.ralph_log("Checking if everything is working - I'm a good helper!")

            # Simple health checks
            health_issues = []

            # Check disk space
            vault_size = sum(f.stat().st_size for f in self.vault_path.rglob('*') if f.is_file())
            if vault_size > 100 * 1024 * 1024:  # 100MB
                health_issues.append("Vault folder is getting large")

            # Check error rate
            if self.state.get('errors_today', 0) > 10:
                health_issues.append("High error rate today")

            if health_issues:
                self.ralph_log(f"Health issues found: {health_issues}", "warning")
                await self.create_health_alert(health_issues)

        except Exception as e:
            self.ralph_log(f"Health monitoring failed: {e}", "error")

    async def generate_content(self):
        """Generate content for various purposes"""
        try:
            self.ralph_log("Making content - I'm creative!")

            # Simple content generation
            content_types = ["blog_idea", "social_post", "email_template"]
            content_type = random.choice(content_types)

            await self.create_content_generation_task(content_type)

        except Exception as e:
            self.ralph_log(f"Content generation failed: {e}", "error")

    async def follow_up_clients(self):
        """Follow up with clients"""
        try:
            self.ralph_log("Following up with friends - I mean clients!")

            # Create client follow-up tasks
            await self.create_client_followup_task()

        except Exception as e:
            self.ralph_log(f"Client follow-up failed: {e}", "error")

    async def create_daily_briefing(self):
        """Create daily briefing"""
        try:
            self.ralph_log("Making daily report - I'm important!")

            # Run daily briefing script
            briefing_script = self.vault_path.parent / "ceo_briefing_system.py"
            if briefing_script.exists():
                subprocess.run([sys.executable, str(briefing_script)],
                             capture_output=True, text=True)

            self.state["last_daily_briefing"] = datetime.now().isoformat()

        except Exception as e:
            self.ralph_log(f"Daily briefing failed: {e}", "error")

    # Helper methods for creating tasks and alerts
    async def create_email_response_task(self, email_id: str):
        """Create task for email response"""
        task_file = self.vault_path / "Needs_Action" / f"EMAIL_RESPONSE_{email_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""---
type: email_response
priority: medium
created_by: ralph_loop
---

# Email Response Required

**Email ID:** {email_id}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Review email content
- Draft appropriate response
- Send response

---
*Created automatically by Ralph Wiggum Loop*
"""

        task_file.write_text(content, encoding='utf-8')

    async def create_social_media_approval(self, content: str):
        """Create social media approval request"""
        approval_file = self.vault_path / "Needs_Action" / f"SOCIAL_APPROVAL_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        approval_file.parent.mkdir(parents=True, exist_ok=True)

        approval_content = f"""---
type: social_media_approval
priority: low
created_by: ralph_loop
---

# Social Media Post Approval

**Proposed Content:**
{content}

**Platform:** LinkedIn
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Approval Actions
- **To Approve:** Move this file to `/Approved/` folder
- **To Reject:** Move this file to `/Rejected/` folder

---
*Created automatically by Ralph Wiggum Loop*
"""

        approval_file.write_text(approval_content, encoding='utf-8')

    async def create_overdue_task_alert(self, count: int):
        """Create alert for overdue tasks"""
        alert_file = self.vault_path / "Needs_Action" / f"OVERDUE_TASKS_ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""---
type: task_alert
priority: high
created_by: ralph_loop
---

# Overdue Tasks Alert

**Count:** {count} overdue tasks
**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Review overdue tasks
- Update task priorities
- Complete or reschedule tasks

---
*Created automatically by Ralph Wiggum Loop*
"""

        alert_file.write_text(content, encoding='utf-8')

    async def create_invoice_followup_task(self, count: int):
        """Create task for invoice follow-up"""
        task_file = self.vault_path / "Needs_Action" / f"INVOICE_FOLLOWUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""---
type: financial_task
priority: high
created_by: ralph_loop
---

# Invoice Follow-up Required

**Outstanding Invoices:** {count}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Review outstanding invoices
- Send follow-up communications
- Update payment status

---
*Created automatically by Ralph Wiggum Loop*
"""

        task_file.write_text(content, encoding='utf-8')

    async def create_health_alert(self, issues: List[str]):
        """Create system health alert"""
        alert_file = self.vault_path / "Needs_Action" / f"HEALTH_ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        alert_file.parent.mkdir(parents=True, exist_ok=True)

        issues_text = '\n'.join([f"- {issue}" for issue in issues])

        content = f"""---
type: system_alert
priority: medium
created_by: ralph_loop
---

# System Health Alert

**Issues Detected:**
{issues_text}

**Detected:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Investigate health issues
- Take corrective actions
- Monitor system performance

---
*Created automatically by Ralph Wiggum Loop*
"""

        alert_file.write_text(content, encoding='utf-8')

    async def create_content_generation_task(self, content_type: str):
        """Create content generation task"""
        task_file = self.vault_path / "Needs_Action" / f"CONTENT_GEN_{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""---
type: content_creation
priority: low
created_by: ralph_loop
---

# Content Generation Task

**Content Type:** {content_type}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Generate {content_type} content
- Review and refine content
- Publish or schedule content

---
*Created automatically by Ralph Wiggum Loop*
"""

        task_file.write_text(content, encoding='utf-8')

    async def create_client_followup_task(self):
        """Create client follow-up task"""
        task_file = self.vault_path / "Needs_Action" / f"CLIENT_FOLLOWUP_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"""---
type: client_communication
priority: medium
created_by: ralph_loop
---

# Client Follow-up Task

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
- Review recent client interactions
- Identify clients needing follow-up
- Send appropriate follow-up communications

---
*Created automatically by Ralph Wiggum Loop*
"""

        task_file.write_text(content, encoding='utf-8')

    def stop_loop(self):
        """Stop the autonomous loop"""
        self.running = False
        self.ralph_log("Loop stopping - I did my best!")

    def get_status(self) -> Dict:
        """Get current status of Ralph's loop"""
        return {
            "running": self.running,
            "loop_count": self.loop_count,
            "total_loops": self.state.get("total_loops", 0),
            "successful_actions_today": self.state.get("successful_actions_today", 0),
            "errors_today": self.state.get("errors_today", 0),
            "last_run": self.state.get("last_run"),
            "actions_today": self.state.get("actions_today", {}),
            "uptime_hours": (datetime.now() - datetime.fromisoformat(self.state["last_run"])).total_seconds() / 3600 if self.state.get("last_run") else 0
        }

async def main():
    """Main function to run Ralph Wiggum Loop"""
    vault_path = "AI_Employee_Vault"
    ralph = RalphWiggumLoop(vault_path)

    print("[RALPH] Ralph Wiggum Autonomous Loop - Gold Tier")
    print("=" * 50)
    print("Hi everybody! I'm Ralph and I'm gonna help with business!")
    print()

    # Show current status
    status = ralph.get_status()
    print(f"[STATUS] Ralph's Status:")
    print(f"- Total loops completed: {status['total_loops']}")
    print(f"- Successful actions today: {status['successful_actions_today']}")
    print(f"- Errors today: {status['errors_today']}")
    print(f"- Last run: {status['last_run'] or 'Never'}")
    print()

    print("[START] Starting Ralph's autonomous loop...")
    print("Press Ctrl+C to stop Ralph")
    print()

    try:
        await ralph.run_autonomous_loop()
    except KeyboardInterrupt:
        print("\n[STOP] Ralph says goodbye!")
        ralph.stop_loop()
    except Exception as e:
        print(f"[ERROR] Ralph encountered an error: {e}")

if __name__ == "__main__":
    asyncio.run(main())