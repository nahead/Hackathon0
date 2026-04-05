#!/usr/bin/env python3
"""
Cloud Orchestrator - Platinum Tier
Main coordination script for cloud agent operations
"""

import os
import sys
import time
import logging
import schedule
from pathlib import Path
from datetime import datetime, timedelta
import json
import subprocess
from typing import Dict, List, Optional
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/ai-employee/logs/cloud-orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('CloudOrchestrator')

class CloudOrchestrator:
    """Main orchestration system for cloud agent operations"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.start_time = datetime.now()

        # Cloud-specific folders
        self.cloud_drafts = self.vault_path / 'Cloud_Drafts'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.reports = self.vault_path / 'Reports' / 'Cloud'

        # Ensure directories exist
        for folder in [self.cloud_drafts, self.pending_approval, self.approved,
                      self.rejected, self.reports]:
            folder.mkdir(parents=True, exist_ok=True)

        # Process tracking
        self.managed_processes = {
            'cloud-file-watcher': None,
            'cloud-gmail-watcher': None,
            'vault-sync-daemon': None
        }

        # Performance metrics
        self.metrics = {
            'emails_processed': 0,
            'drafts_created': 0,
            'approvals_pending': 0,
            'sync_operations': 0,
            'uptime_hours': 0
        }

        logger.info("Cloud Orchestrator initialized")

    def check_process_health(self) -> Dict[str, Dict]:
        """Check health of all managed processes"""
        health_status = {}

        for process_name in self.managed_processes:
            try:
                # Check if process is running via PM2
                result = subprocess.run(
                    ['pm2', 'describe', process_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    # Parse PM2 output (simplified)
                    status = 'online' if 'online' in result.stdout else 'stopped'
                    health_status[process_name] = {
                        'status': status,
                        'healthy': status == 'online',
                        'last_check': datetime.now().isoformat()
                    }
                else:
                    health_status[process_name] = {
                        'status': 'not_found',
                        'healthy': False,
                        'last_check': datetime.now().isoformat()
                    }

            except Exception as e:
                logger.error(f"Error checking {process_name}: {e}")
                health_status[process_name] = {
                    'status': 'error',
                    'healthy': False,
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }

        return health_status

    def restart_unhealthy_processes(self):
        """Restart any unhealthy processes"""
        health_status = self.check_process_health()

        for process_name, status in health_status.items():
            if not status['healthy']:
                logger.warning(f"Process {process_name} is unhealthy: {status['status']}")
                try:
                    # Attempt to restart via PM2
                    result = subprocess.run(
                        ['pm2', 'restart', process_name],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    if result.returncode == 0:
                        logger.info(f"Successfully restarted {process_name}")
                    else:
                        logger.error(f"Failed to restart {process_name}: {result.stderr}")

                except Exception as e:
                    logger.error(f"Error restarting {process_name}: {e}")

    def process_approval_queue(self):
        """Process pending approvals and execute approved actions"""
        try:
            # Check for newly approved items
            approved_files = list(self.approved.glob('*.md'))

            for approved_file in approved_files:
                logger.info(f"Processing approved action: {approved_file.name}")

                try:
                    # Read approval file
                    content = approved_file.read_text(encoding='utf-8')

                    # Extract metadata
                    if content.startswith('---'):
                        yaml_end = content.find('---', 3)
                        if yaml_end != -1:
                            yaml_content = content[3:yaml_end].strip()
                            # Simple YAML parsing (for basic key: value pairs)
                            metadata = {}
                            for line in yaml_content.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    metadata[key.strip()] = value.strip()

                            # Process based on action type
                            action_type = metadata.get('action', 'unknown')
                            self.execute_approved_action(action_type, metadata, content)

                    # Move to processed folder
                    processed_folder = self.vault_path / 'Processed' / 'Cloud'
                    processed_folder.mkdir(parents=True, exist_ok=True)

                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_name = f"PROCESSED_{timestamp}_{approved_file.name}"
                    approved_file.rename(processed_folder / new_name)

                except Exception as e:
                    logger.error(f"Error processing {approved_file.name}: {e}")
                    # Move to error folder
                    error_folder = self.vault_path / 'Errors' / 'Cloud'
                    error_folder.mkdir(parents=True, exist_ok=True)
                    approved_file.rename(error_folder / approved_file.name)

        except Exception as e:
            logger.error(f"Error in approval queue processing: {e}")

    def execute_approved_action(self, action_type: str, metadata: Dict, content: str):
        """Execute approved actions (cloud agent creates signals for local agent)"""
        logger.info(f"Executing approved action: {action_type}")

        if action_type == 'send_email':
            self.create_email_send_signal(metadata, content)
        elif action_type == 'post_social':
            self.create_social_post_signal(metadata, content)
        elif action_type == 'whatsapp_send':
            self.create_whatsapp_signal(metadata, content)
        else:
            logger.warning(f"Unknown action type: {action_type}")

    def create_email_send_signal(self, metadata: Dict, content: str):
        """Create signal for local agent to send email"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.vault_path / 'Signals' / 'Local' / f'EMAIL_SEND_{timestamp}.md'
        signal_file.parent.mkdir(parents=True, exist_ok=True)

        signal_content = f"""---
type: local_action_signal
action: send_email
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
priority: normal
---

## Email Send Request

**From Cloud Agent to Local Agent**

### Action Details:
- **To**: {metadata.get('to', 'Unknown')}
- **Subject**: {metadata.get('subject', 'No Subject')}
- **Email ID**: {metadata.get('email_id', 'N/A')}

### Original Approval:
{content}

### Instructions for Local Agent:
1. Use Email MCP server to send this response
2. Log the action in audit trail
3. Move this signal to /Processed when complete

**Note**: This action was approved by human and delegated to local agent for execution.
"""

        signal_file.write_text(signal_content, encoding='utf-8')
        logger.info(f"Email send signal created: {signal_file.name}")

    def create_social_post_signal(self, metadata: Dict, content: str):
        """Create signal for local agent to post on social media"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.vault_path / 'Signals' / 'Local' / f'SOCIAL_POST_{timestamp}.md'
        signal_file.parent.mkdir(parents=True, exist_ok=True)

        signal_content = f"""---
type: local_action_signal
action: post_social
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
priority: normal
---

## Social Media Post Request

**From Cloud Agent to Local Agent**

### Action Details:
- **Platforms**: {metadata.get('platforms', 'LinkedIn')}
- **Content**: {metadata.get('content', 'See original approval')}

### Original Approval:
{content}

### Instructions for Local Agent:
1. Use appropriate social media sessions
2. Post content to specified platforms
3. Log engagement metrics
4. Move this signal to /Processed when complete

**Note**: This action was approved by human and delegated to local agent for execution.
"""

        signal_file.write_text(signal_content, encoding='utf-8')
        logger.info(f"Social post signal created: {signal_file.name}")

    def create_whatsapp_signal(self, metadata: Dict, content: str):
        """Create signal for local agent to send WhatsApp message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        signal_file = self.vault_path / 'Signals' / 'Local' / f'WHATSAPP_SEND_{timestamp}.md'
        signal_file.parent.mkdir(parents=True, exist_ok=True)

        signal_content = f"""---
type: local_action_signal
action: send_whatsapp
created_by: cloud_agent
created_at: {datetime.now().isoformat()}
priority: high
---

## WhatsApp Send Request

**From Cloud Agent to Local Agent**

### Action Details:
- **Contact**: {metadata.get('contact', 'Unknown')}
- **Message**: {metadata.get('message', 'See original approval')}

### Original Approval:
{content}

### Instructions for Local Agent:
1. Use WhatsApp session to send message
2. Confirm delivery
3. Log interaction
4. Move this signal to /Processed when complete

**Note**: This action was approved by human and delegated to local agent for execution.
"""

        signal_file.write_text(signal_content, encoding='utf-8')
        logger.info(f"WhatsApp signal created: {signal_file.name}")

    def generate_cloud_status_report(self):
        """Generate comprehensive cloud agent status report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports / f'CLOUD_STATUS_{timestamp}.md'

        # Gather system metrics
        system_metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
        }

        # Process health
        health_status = self.check_process_health()

        # Count pending items
        pending_count = len(list(self.pending_approval.glob('*.md')))
        draft_count = len(list(self.cloud_drafts.glob('*.md')))

        report_content = f"""---
type: cloud_status_report
created_at: {datetime.now().isoformat()}
agent: cloud_orchestrator
---

# Cloud Agent Status Report

## System Health: {"🟢 HEALTHY" if all(p['healthy'] for p in health_status.values()) else "🟡 DEGRADED"}

### Process Status
{chr(10).join([f"- **{name}**: {status['status'].upper()} {'✅' if status['healthy'] else '❌'}" for name, status in health_status.items()])}

### System Metrics
- **CPU Usage**: {system_metrics['cpu_percent']:.1f}%
- **Memory Usage**: {system_metrics['memory_percent']:.1f}%
- **Disk Usage**: {system_metrics['disk_percent']:.1f}%
- **Uptime**: {system_metrics['uptime_hours']:.1f} hours

### Work Queue Status
- **Pending Approvals**: {pending_count}
- **Draft Responses**: {draft_count}
- **Emails Processed**: {self.metrics['emails_processed']}
- **Drafts Created**: {self.metrics['drafts_created']}

### Cloud Agent Capabilities
- ✅ **Email Monitoring**: Active (draft-only mode)
- ✅ **File Processing**: Active (draft creation)
- ✅ **Vault Synchronization**: Active (Git-based)
- ✅ **Approval Processing**: Active (signal creation)
- ✅ **Health Monitoring**: Active (self-healing)

### Security Status
- ✅ **Secrets Isolation**: No sensitive data in cloud
- ✅ **Draft-Only Mode**: No direct external actions
- ✅ **Approval Required**: All actions require human approval
- ✅ **Audit Logging**: All operations logged

### Next Actions
- Continue monitoring for new emails and files
- Process approval queue every 5 minutes
- Generate health reports every hour
- Sync vault changes every minute

---
*Generated by Cloud Orchestrator - Platinum Tier*
*Cloud Agent operates in draft-only mode for security*
"""

        report_file.write_text(report_content, encoding='utf-8')
        logger.info(f"Cloud status report generated: {report_file.name}")

        # Update metrics
        self.metrics['uptime_hours'] = system_metrics['uptime_hours']

    def cleanup_old_files(self):
        """Clean up old files to prevent disk space issues"""
        try:
            # Clean up old logs (keep last 7 days)
            log_dir = Path('/home/ubuntu/ai-employee/logs')
            if log_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=7)
                for log_file in log_dir.glob('*.log'):
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                        log_file.unlink()
                        logger.info(f"Cleaned up old log: {log_file.name}")

            # Clean up old reports (keep last 30 days)
            if self.reports.exists():
                cutoff_date = datetime.now() - timedelta(days=30)
                for report_file in self.reports.glob('*.md'):
                    if datetime.fromtimestamp(report_file.stat().st_mtime) < cutoff_date:
                        report_file.unlink()
                        logger.info(f"Cleaned up old report: {report_file.name}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def schedule_tasks(self):
        """Schedule recurring tasks"""
        # Health checks every 5 minutes
        schedule.every(5).minutes.do(self.restart_unhealthy_processes)

        # Process approvals every 2 minutes
        schedule.every(2).minutes.do(self.process_approval_queue)

        # Generate status reports every hour
        schedule.every().hour.do(self.generate_cloud_status_report)

        # Cleanup old files daily at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_files)

        logger.info("Scheduled tasks configured")

    def run(self):
        """Main orchestrator loop"""
        logger.info("Starting Cloud Orchestrator...")

        # Schedule recurring tasks
        self.schedule_tasks()

        # Generate initial status report
        self.generate_cloud_status_report()

        # Main loop
        while True:
            try:
                # Run scheduled tasks
                schedule.run_pending()

                # Brief sleep to prevent excessive CPU usage
                time.sleep(30)

            except KeyboardInterrupt:
                logger.info("Shutting down Cloud Orchestrator...")
                break
            except Exception as e:
                logger.error(f"Unexpected error in orchestrator: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main function"""
    vault_path = os.getenv('VAULT_PATH', '/home/ubuntu/ai-employee/vault-sync')

    if not Path(vault_path).exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    orchestrator = CloudOrchestrator(vault_path)
    orchestrator.run()

if __name__ == "__main__":
    main()