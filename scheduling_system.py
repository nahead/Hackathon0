#!/usr/bin/env python3
"""
Scheduling System - Silver Tier Requirement
Cross-platform scheduling for automated daily/weekly tasks
Supports Windows Task Scheduler and Unix cron
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import platform

class SchedulingSystem:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.schedules_path = self.vault_path / "Schedules"
        self.logs_path = self.vault_path / "Logs"
        self.system = platform.system().lower()

        # Create directories
        self.schedules_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Define scheduled tasks
        self.scheduled_tasks = {
            "daily_briefing": {
                "name": "Daily Business Briefing",
                "script": "daily_briefing.py",
                "schedule": "daily",
                "time": "08:00",
                "description": "Generate daily business summary and task overview"
            },
            "weekly_audit": {
                "name": "Weekly Business Audit",
                "script": "weekly_audit.py",
                "schedule": "weekly",
                "day": "sunday",
                "time": "20:00",
                "description": "Comprehensive weekly business analysis and CEO briefing"
            },
            "content_generation": {
                "name": "Social Media Content Generation",
                "script": "auto_content_generator.py",
                "schedule": "daily",
                "time": "09:00",
                "description": "Generate and schedule social media content"
            },
            "email_processing": {
                "name": "Email Processing and Responses",
                "script": "email_response_sender.py",
                "schedule": "hourly",
                "description": "Process incoming emails and generate responses"
            },
            "system_health_check": {
                "name": "System Health Check",
                "script": "system_health_check.py",
                "schedule": "daily",
                "time": "07:00",
                "description": "Check system status and component health"
            }
        }

    def create_windows_task(self, task_id: str, task_config: Dict) -> bool:
        """Create Windows Task Scheduler task"""
        try:
            task_name = f"AIEmployee_{task_id}"
            script_path = Path(__file__).parent / task_config['script']
            python_exe = sys.executable

            # Build schtasks command
            cmd = [
                "schtasks", "/create",
                "/tn", task_name,
                "/tr", f'"{python_exe}" "{script_path}"',
                "/sc", self._get_windows_schedule(task_config),
                "/f"  # Force overwrite if exists
            ]

            # Add time specification
            if 'time' in task_config:
                cmd.extend(["/st", task_config['time']])

            # Add day specification for weekly tasks
            if task_config.get('schedule') == 'weekly' and 'day' in task_config:
                cmd.extend(["/d", task_config['day'].upper()])

            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"[SUCCESS] Created Windows task: {task_name}")
                return True
            else:
                print(f"[ERROR] Failed to create Windows task: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error creating Windows task for {task_id}: {e}")
            return False

    def create_cron_job(self, task_id: str, task_config: Dict) -> bool:
        """Create Unix cron job"""
        try:
            script_path = Path(__file__).parent / task_config['script']
            python_exe = sys.executable

            # Generate cron expression
            cron_expr = self._get_cron_expression(task_config)
            cron_command = f"{python_exe} {script_path}"
            cron_line = f"{cron_expr} {cron_command} # AIEmployee_{task_id}\n"

            # Read existing crontab
            try:
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                existing_crontab = result.stdout if result.returncode == 0 else ""
            except:
                existing_crontab = ""

            # Remove existing entry for this task
            lines = existing_crontab.split('\n')
            filtered_lines = [line for line in lines if f"# AIEmployee_{task_id}" not in line]

            # Add new entry
            filtered_lines.append(cron_line.strip())
            new_crontab = '\n'.join(line for line in filtered_lines if line.strip())

            # Write new crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            if process.returncode == 0:
                print(f"[SUCCESS] Created cron job: {task_id}")
                return True
            else:
                print(f"[ERROR] Failed to create cron job for {task_id}")
                return False

        except Exception as e:
            print(f"Error creating cron job for {task_id}: {e}")
            return False

    def _get_windows_schedule(self, task_config: Dict) -> str:
        """Convert task config to Windows schedule format"""
        schedule = task_config.get('schedule', 'daily')

        if schedule == 'hourly':
            return 'hourly'
        elif schedule == 'daily':
            return 'daily'
        elif schedule == 'weekly':
            return 'weekly'
        else:
            return 'daily'

    def _get_cron_expression(self, task_config: Dict) -> str:
        """Convert task config to cron expression"""
        schedule = task_config.get('schedule', 'daily')
        time_str = task_config.get('time', '08:00')

        # Parse time
        try:
            hour, minute = map(int, time_str.split(':'))
        except:
            hour, minute = 8, 0

        if schedule == 'hourly':
            return f"0 * * * *"
        elif schedule == 'daily':
            return f"{minute} {hour} * * *"
        elif schedule == 'weekly':
            day = task_config.get('day', 'sunday')
            day_num = {
                'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
                'thursday': 4, 'friday': 5, 'saturday': 6
            }.get(day.lower(), 0)
            return f"{minute} {hour} * * {day_num}"
        else:
            return f"{minute} {hour} * * *"

    def install_all_schedules(self) -> Dict[str, bool]:
        """Install all scheduled tasks"""
        results = {}

        print(f"Installing schedules for {self.system} system...")

        for task_id, task_config in self.scheduled_tasks.items():
            print(f"\nInstalling: {task_config['name']}")

            if self.system == 'windows':
                success = self.create_windows_task(task_id, task_config)
            else:
                success = self.create_cron_job(task_id, task_config)

            results[task_id] = success

        return results

    def remove_all_schedules(self) -> Dict[str, bool]:
        """Remove all scheduled tasks"""
        results = {}

        print(f"Removing schedules from {self.system} system...")

        for task_id, task_config in self.scheduled_tasks.items():
            print(f"\nRemoving: {task_config['name']}")

            if self.system == 'windows':
                success = self.remove_windows_task(task_id)
            else:
                success = self.remove_cron_job(task_id)

            results[task_id] = success

        return results

    def remove_windows_task(self, task_id: str) -> bool:
        """Remove Windows Task Scheduler task"""
        try:
            task_name = f"AIEmployee_{task_id}"
            cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"[SUCCESS] Removed Windows task: {task_name}")
                return True
            else:
                print(f"[ERROR] Failed to remove Windows task: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error removing Windows task for {task_id}: {e}")
            return False

    def remove_cron_job(self, task_id: str) -> bool:
        """Remove Unix cron job"""
        try:
            # Read existing crontab
            try:
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                existing_crontab = result.stdout if result.returncode == 0 else ""
            except:
                existing_crontab = ""

            # Remove entry for this task
            lines = existing_crontab.split('\n')
            filtered_lines = [line for line in lines if f"# AIEmployee_{task_id}" not in line]
            new_crontab = '\n'.join(line for line in filtered_lines if line.strip())

            # Write new crontab
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_crontab)

            if process.returncode == 0:
                print(f"[SUCCESS] Removed cron job: {task_id}")
                return True
            else:
                print(f"[ERROR] Failed to remove cron job for {task_id}")
                return False

        except Exception as e:
            print(f"Error removing cron job for {task_id}: {e}")
            return False

    def list_scheduled_tasks(self):
        """List all configured scheduled tasks"""
        print("\n[TASKS] Configured Scheduled Tasks:")
        print("=" * 50)

        for task_id, config in self.scheduled_tasks.items():
            schedule_desc = self._format_schedule_description(config)
            print(f"\n[TASK] {config['name']}")
            print(f"   ID: {task_id}")
            print(f"   Script: {config['script']}")
            print(f"   Schedule: {schedule_desc}")
            print(f"   Description: {config['description']}")

    def _format_schedule_description(self, config: Dict) -> str:
        """Format schedule for human reading"""
        schedule = config.get('schedule', 'daily')
        time_str = config.get('time', 'N/A')

        if schedule == 'hourly':
            return "Every hour"
        elif schedule == 'daily':
            return f"Daily at {time_str}"
        elif schedule == 'weekly':
            day = config.get('day', 'Sunday')
            return f"Weekly on {day.title()} at {time_str}"
        else:
            return f"{schedule.title()}"

    def create_schedule_config_file(self):
        """Create configuration file for schedules"""
        config_path = self.schedules_path / "schedule_config.json"

        config_data = {
            "system_info": {
                "platform": self.system,
                "python_executable": sys.executable,
                "vault_path": str(self.vault_path),
                "created": datetime.now().isoformat()
            },
            "scheduled_tasks": self.scheduled_tasks,
            "settings": {
                "enable_logging": True,
                "log_retention_days": 30,
                "error_notification": True,
                "health_check_enabled": True
            }
        }

        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        print(f"[SUCCESS] Created schedule configuration: {config_path}")

    def create_task_scripts(self):
        """Create placeholder scripts for scheduled tasks"""
        scripts_to_create = [
            ("daily_briefing.py", self._get_daily_briefing_script()),
            ("weekly_audit.py", self._get_weekly_audit_script()),
            ("system_health_check.py", self._get_health_check_script())
        ]

        for script_name, script_content in scripts_to_create:
            script_path = Path(__file__).parent / script_name
            if script_path.exists():
                script_path.write_text(script_content, encoding='utf-8')
                print(f"[SUCCESS] Created script: {script_name}")

    def _get_daily_briefing_script(self) -> str:
        """Generate daily briefing script content"""
        return '''#!/usr/bin/env python3
"""
Daily Business Briefing - Scheduled Task
Generates daily summary of business activities
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

def generate_daily_briefing():
    """Generate daily business briefing"""
    vault_path = Path("AI_Employee_Vault")
    briefing_path = vault_path / "Briefings" / f"Daily_{datetime.now().strftime('%Y-%m-%d')}.md"
    briefing_path.parent.mkdir(parents=True, exist_ok=True)

    briefing_content = f"""# Daily Business Briefing - {datetime.now().strftime('%Y-%m-%d')}

## 📊 Today's Overview
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Status: Automated daily briefing

## 📧 Email Summary
- Pending emails: [To be implemented]
- Responses sent: [To be implemented]

## 📱 Social Media Activity
- Posts scheduled: [To be implemented]
- Engagement metrics: [To be implemented]

## 💼 Business Tasks
- Completed today: [To be implemented]
- Pending tasks: [To be implemented]

## 🎯 Today's Priorities
1. Process pending emails
2. Review social media engagement
3. Update project status
4. Prepare tomorrow's content

---
*Generated automatically by AI Employee System*
"""

    briefing_path.write_text(briefing_content, encoding='utf-8')
    print(f"[SUCCESS] Daily briefing generated: {briefing_path}")

if __name__ == "__main__":
    try:
        generate_daily_briefing()
    except Exception as e:
        print(f"[ERROR] Error generating daily briefing: {e}")
        sys.exit(1)
'''

    def _get_weekly_audit_script(self) -> str:
        """Generate weekly audit script content"""
        return '''#!/usr/bin/env python3
"""
Weekly Business Audit - Scheduled Task
Comprehensive weekly business analysis and CEO briefing
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

def generate_weekly_audit():
    """Generate comprehensive weekly business audit"""
    vault_path = Path("AI_Employee_Vault")
    audit_path = vault_path / "Briefings" / f"Weekly_Audit_{datetime.now().strftime('%Y-W%U')}.md"
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    week_start = datetime.now() - timedelta(days=7)
    week_end = datetime.now()

    audit_content = f"""# Weekly Business Audit - Week {datetime.now().strftime('%U, %Y')}

## 📅 Period: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}

## 🎯 Executive Summary
This week's performance analysis and key insights.

## 💰 Financial Overview
- Revenue this week: [To be implemented]
- Expenses tracked: [To be implemented]
- Outstanding invoices: [To be implemented]

## 📈 Business Metrics
- Tasks completed: [To be implemented]
- Client interactions: [To be implemented]
- Social media engagement: [To be implemented]

## 🚧 Bottlenecks Identified
- [To be implemented with actual analysis]

## 💡 Proactive Suggestions
- [To be implemented with AI recommendations]

## 📋 Next Week's Priorities
1. Follow up on outstanding items
2. Optimize identified bottlenecks
3. Implement suggested improvements
4. Prepare monthly review

## 🔍 Detailed Analysis
### Email Performance
- Total emails processed: [To be implemented]
- Average response time: [To be implemented]

### Social Media Performance
- Posts published: [To be implemented]
- Engagement rate: [To be implemented]

### Task Management
- Tasks created: [To be implemented]
- Tasks completed: [To be implemented]
- Completion rate: [To be implemented]

---
*Generated automatically by AI Employee System - Weekly Audit*
"""

    audit_path.write_text(audit_content, encoding='utf-8')
    print(f"[SUCCESS] Weekly audit generated: {audit_path}")

if __name__ == "__main__":
    try:
        generate_weekly_audit()
    except Exception as e:
        print(f"[ERROR] Error generating weekly audit: {e}")
        sys.exit(1)
'''

    def _get_health_check_script(self) -> str:
        """Generate system health check script content"""
        return '''#!/usr/bin/env python3
"""
System Health Check - Scheduled Task
Monitor system components and report status
"""

import sys
import psutil
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

def perform_health_check():
    """Perform comprehensive system health check"""
    vault_path = Path("AI_Employee_Vault")
    health_path = vault_path / "Logs" / f"Health_Check_{datetime.now().strftime('%Y-%m-%d')}.json"
    health_path.parent.mkdir(parents=True, exist_ok=True)

    # Gather system metrics
    health_data = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:').percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        },
        "vault_status": {
            "vault_exists": vault_path.exists(),
            "folders_present": {
                "Done": (vault_path / "Done").exists(),
                "Plans": (vault_path / "Plans").exists(),
                "Needs_Action": (vault_path / "Needs_Action").exists(),
                "Logs": (vault_path / "Logs").exists()
            }
        },
        "processes": {
            "python_processes": len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]),
            "total_processes": len(list(psutil.process_iter()))
        },
        "status": "healthy"
    }

    # Determine overall health
    if health_data["system"]["cpu_percent"] > 90:
        health_data["status"] = "warning"
        health_data["warnings"] = health_data.get("warnings", [])
        health_data["warnings"].append("High CPU usage")

    if health_data["system"]["memory_percent"] > 90:
        health_data["status"] = "warning"
        health_data["warnings"] = health_data.get("warnings", [])
        health_data["warnings"].append("High memory usage")

    # Save health data
    with open(health_path, 'w') as f:
        json.dump(health_data, f, indent=2)

    print(f"[SUCCESS] Health check completed: {health_data['status']}")

    if health_data["status"] == "warning":
        print("[WARNING] Warnings detected:")
        for warning in health_data.get("warnings", []):
            print(f"   - {warning}")

if __name__ == "__main__":
    try:
        perform_health_check()
    except Exception as e:
        print(f"[ERROR] Error performing health check: {e}")
        sys.exit(1)
'''

def main():
    vault_path = "AI_Employee_Vault"
    scheduler = SchedulingSystem(vault_path)

    print("[SCHEDULE] AI Employee Scheduling System")
    print("=" * 50)

    # Show current configuration
    scheduler.list_scheduled_tasks()

    print(f"\n[SYSTEM] Detected system: {scheduler.system.title()}")

    # Create configuration and scripts
    scheduler.create_schedule_config_file()
    scheduler.create_task_scripts()

    # Ask user what to do
    print("\n[ACTIONS] Available Actions:")
    print("1. Install all scheduled tasks")
    print("2. Remove all scheduled tasks")
    print("3. List current tasks")
    print("4. Exit")

    try:
        choice = input("\nSelect action (1-4): ").strip()

        if choice == "1":
            print("\n🚀 Installing scheduled tasks...")
            results = scheduler.install_all_schedules()

            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            print(f"\n📊 Installation Results: {success_count}/{total_count} successful")

            if success_count == total_count:
                print("[SUCCESS] All scheduled tasks installed successfully!")
                print("\n[NEXT] Next Steps:")
                print("- Tasks will run automatically according to their schedules")
                print("- Check logs in AI_Employee_Vault/Logs/ for execution results")
                print("- Review generated briefings in AI_Employee_Vault/Briefings/")
            else:
                print("[WARNING] Some tasks failed to install. Check error messages above.")

        elif choice == "2":
            print("\n🗑️  Removing scheduled tasks...")
            results = scheduler.remove_all_schedules()

            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)

            print(f"\n📊 Removal Results: {success_count}/{total_count} successful")

        elif choice == "3":
            scheduler.list_scheduled_tasks()

        elif choice == "4":
            print("[EXIT] Goodbye!")

        else:
            print("[ERROR] Invalid choice")

    except KeyboardInterrupt:
        print("\n[EXIT] Goodbye!")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    main()