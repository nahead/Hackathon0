#!/usr/bin/env python3
"""
Cross-Domain Integration System - Gold Tier Requirement
Orchestrates communication between email, social media, accounting, and scheduling domains
Provides unified workflows that span multiple business functions
"""

import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

class DomainType(Enum):
    EMAIL = "email"
    SOCIAL_MEDIA = "social_media"
    ACCOUNTING = "accounting"
    SCHEDULING = "scheduling"
    CONTENT = "content"
    COMMUNICATION = "communication"

@dataclass
class CrossDomainEvent:
    """Event that can trigger actions across multiple domains"""
    event_id: str
    source_domain: DomainType
    target_domains: List[DomainType]
    event_type: str
    data: Dict[str, Any]
    timestamp: str
    priority: str = "medium"
    requires_approval: bool = False

@dataclass
class WorkflowStep:
    """Individual step in a cross-domain workflow"""
    step_id: str
    domain: DomainType
    action: str
    parameters: Dict[str, Any]
    depends_on: List[str] = None
    timeout_seconds: int = 300

@dataclass
class CrossDomainWorkflow:
    """Complete workflow spanning multiple domains"""
    workflow_id: str
    name: str
    description: str
    trigger_event: str
    steps: List[WorkflowStep]
    auto_execute: bool = False

class CrossDomainIntegrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "Config" / "cross_domain_config.json"
        self.workflows_path = self.vault_path / "Workflows"
        self.logs_path = self.vault_path / "Logs"

        # Create directories
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.workflows_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'cross_domain.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Domain connectors
        self.domain_connectors = {}
        self.event_queue = asyncio.Queue()
        self.active_workflows = {}

        # Load configuration
        self.config = self.load_config()

        # Initialize predefined workflows
        self.initialize_workflows()

    def load_config(self) -> Dict:
        """Load cross-domain integration configuration"""
        default_config = {
            "enabled_domains": [
                "email", "social_media", "accounting", "scheduling", "content"
            ],
            "workflow_timeout": 3600,
            "max_concurrent_workflows": 10,
            "auto_retry_failed_steps": True,
            "notification_settings": {
                "email_on_workflow_complete": True,
                "log_all_events": True
            },
            "domain_endpoints": {
                "email": "email_response_sender.py",
                "social_media": "auto_content_generator.py",
                "accounting": "odoo-mcp-server/odoo_mcp_server.py",
                "scheduling": "scheduling_system.py"
            }
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

    def initialize_workflows(self):
        """Initialize predefined cross-domain workflows"""

        # Workflow 1: New Client Onboarding
        client_onboarding = CrossDomainWorkflow(
            workflow_id="client_onboarding",
            name="New Client Onboarding",
            description="Complete client onboarding across all business domains",
            trigger_event="new_client_email",
            steps=[
                WorkflowStep(
                    step_id="create_client_record",
                    domain=DomainType.ACCOUNTING,
                    action="create_partner",
                    parameters={"extract_from_email": True}
                ),
                WorkflowStep(
                    step_id="send_welcome_email",
                    domain=DomainType.EMAIL,
                    action="send_template_email",
                    parameters={"template": "client_welcome"},
                    depends_on=["create_client_record"]
                ),
                WorkflowStep(
                    step_id="schedule_followup",
                    domain=DomainType.SCHEDULING,
                    action="create_task",
                    parameters={"task_type": "client_followup", "days_ahead": 3},
                    depends_on=["send_welcome_email"]
                ),
                WorkflowStep(
                    step_id="announce_new_client",
                    domain=DomainType.SOCIAL_MEDIA,
                    action="create_announcement_post",
                    parameters={"type": "new_client", "requires_approval": True},
                    depends_on=["create_client_record"]
                )
            ],
            auto_execute=False
        )

        # Workflow 2: Invoice Payment Received
        payment_received = CrossDomainWorkflow(
            workflow_id="payment_received",
            name="Invoice Payment Processing",
            description="Process received payments across all systems",
            trigger_event="payment_received",
            steps=[
                WorkflowStep(
                    step_id="update_invoice_status",
                    domain=DomainType.ACCOUNTING,
                    action="mark_invoice_paid",
                    parameters={"invoice_id": "{event.invoice_id}"}
                ),
                WorkflowStep(
                    step_id="send_payment_confirmation",
                    domain=DomainType.EMAIL,
                    action="send_template_email",
                    parameters={"template": "payment_confirmation"},
                    depends_on=["update_invoice_status"]
                ),
                WorkflowStep(
                    step_id="update_financial_dashboard",
                    domain=DomainType.CONTENT,
                    action="generate_financial_update",
                    parameters={"type": "payment_received"},
                    depends_on=["update_invoice_status"]
                )
            ],
            auto_execute=True
        )

        # Workflow 3: Weekly Business Review
        weekly_review = CrossDomainWorkflow(
            workflow_id="weekly_business_review",
            name="Weekly Business Review",
            description="Generate comprehensive weekly business review",
            trigger_event="weekly_review_scheduled",
            steps=[
                WorkflowStep(
                    step_id="gather_financial_data",
                    domain=DomainType.ACCOUNTING,
                    action="get_financial_summary",
                    parameters={"period": "week"}
                ),
                WorkflowStep(
                    step_id="gather_social_metrics",
                    domain=DomainType.SOCIAL_MEDIA,
                    action="get_engagement_metrics",
                    parameters={"period": "week"}
                ),
                WorkflowStep(
                    step_id="gather_email_stats",
                    domain=DomainType.EMAIL,
                    action="get_email_statistics",
                    parameters={"period": "week"}
                ),
                WorkflowStep(
                    step_id="generate_review_report",
                    domain=DomainType.CONTENT,
                    action="create_business_review",
                    parameters={"combine_all_data": True},
                    depends_on=["gather_financial_data", "gather_social_metrics", "gather_email_stats"]
                ),
                WorkflowStep(
                    step_id="schedule_ceo_briefing",
                    domain=DomainType.SCHEDULING,
                    action="create_briefing_task",
                    parameters={"priority": "high"},
                    depends_on=["generate_review_report"]
                )
            ],
            auto_execute=True
        )

        # Store workflows
        self.workflows = {
            "client_onboarding": client_onboarding,
            "payment_received": payment_received,
            "weekly_business_review": weekly_review
        }

        # Save workflows to disk
        self.save_workflows()

    def save_workflows(self):
        """Save workflows to disk"""
        try:
            workflows_file = self.workflows_path / "predefined_workflows.json"
            workflows_data = {}

            for workflow_id, workflow in self.workflows.items():
                workflows_data[workflow_id] = {
                    "workflow_id": workflow.workflow_id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "trigger_event": workflow.trigger_event,
                    "auto_execute": workflow.auto_execute,
                    "steps": [
                        {
                            "step_id": step.step_id,
                            "domain": step.domain.value,
                            "action": step.action,
                            "parameters": step.parameters,
                            "depends_on": step.depends_on or [],
                            "timeout_seconds": step.timeout_seconds
                        }
                        for step in workflow.steps
                    ]
                }

            with open(workflows_file, 'w') as f:
                json.dump(workflows_data, f, indent=2)

            self.logger.info(f"Saved {len(workflows_data)} workflows to {workflows_file}")

        except Exception as e:
            self.logger.error(f"Error saving workflows: {e}")

    async def register_domain_connector(self, domain: DomainType, connector: Callable):
        """Register a connector for a specific domain"""
        self.domain_connectors[domain] = connector
        self.logger.info(f"Registered connector for domain: {domain.value}")

    async def emit_event(self, event: CrossDomainEvent):
        """Emit an event that may trigger cross-domain workflows"""
        try:
            await self.event_queue.put(event)
            self.logger.info(f"Event emitted: {event.event_type} from {event.source_domain.value}")

            # Log event
            event_log = {
                "timestamp": event.timestamp,
                "event_id": event.event_id,
                "source_domain": event.source_domain.value,
                "event_type": event.event_type,
                "data": event.data
            }

            log_file = self.logs_path / f"events_{datetime.now().strftime('%Y-%m-%d')}.json"

            # Append to daily event log
            events = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        events = json.load(f)
                except:
                    events = []

            events.append(event_log)

            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error emitting event: {e}")

    async def process_events(self):
        """Process events and trigger appropriate workflows"""
        while True:
            try:
                event = await self.event_queue.get()

                # Find matching workflows
                matching_workflows = []
                for workflow in self.workflows.values():
                    if workflow.trigger_event == event.event_type:
                        matching_workflows.append(workflow)

                # Execute matching workflows
                for workflow in matching_workflows:
                    if workflow.auto_execute or not event.requires_approval:
                        await self.execute_workflow(workflow, event)
                    else:
                        await self.queue_workflow_for_approval(workflow, event)

            except Exception as e:
                self.logger.error(f"Error processing event: {e}")

    async def execute_workflow(self, workflow: CrossDomainWorkflow, trigger_event: CrossDomainEvent):
        """Execute a cross-domain workflow"""
        try:
            execution_id = f"{workflow.workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.logger.info(f"Starting workflow execution: {execution_id}")

            # Track workflow execution
            execution_context = {
                "execution_id": execution_id,
                "workflow": workflow,
                "trigger_event": trigger_event,
                "start_time": datetime.now().isoformat(),
                "completed_steps": [],
                "failed_steps": [],
                "status": "running"
            }

            self.active_workflows[execution_id] = execution_context

            # Execute steps in dependency order
            remaining_steps = workflow.steps.copy()
            completed_step_ids = set()

            while remaining_steps:
                # Find steps that can be executed (dependencies met)
                executable_steps = []
                for step in remaining_steps:
                    if not step.depends_on or all(dep in completed_step_ids for dep in step.depends_on):
                        executable_steps.append(step)

                if not executable_steps:
                    self.logger.error(f"Workflow {execution_id} has circular dependencies or missing steps")
                    break

                # Execute steps in parallel where possible
                tasks = []
                for step in executable_steps:
                    task = asyncio.create_task(self.execute_workflow_step(step, execution_context))
                    tasks.append((step, task))

                # Wait for completion
                for step, task in tasks:
                    try:
                        result = await asyncio.wait_for(task, timeout=step.timeout_seconds)
                        if result:
                            completed_step_ids.add(step.step_id)
                            execution_context["completed_steps"].append({
                                "step_id": step.step_id,
                                "result": result,
                                "timestamp": datetime.now().isoformat()
                            })
                        else:
                            execution_context["failed_steps"].append({
                                "step_id": step.step_id,
                                "error": "Step returned False",
                                "timestamp": datetime.now().isoformat()
                            })
                    except asyncio.TimeoutError:
                        execution_context["failed_steps"].append({
                            "step_id": step.step_id,
                            "error": f"Timeout after {step.timeout_seconds} seconds",
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        execution_context["failed_steps"].append({
                            "step_id": step.step_id,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        })

                # Remove completed/failed steps
                remaining_steps = [s for s in remaining_steps if s not in executable_steps]

            # Update final status
            execution_context["end_time"] = datetime.now().isoformat()
            execution_context["status"] = "completed" if not execution_context["failed_steps"] else "failed"

            # Save execution log
            await self.save_workflow_execution(execution_context)

            self.logger.info(f"Workflow {execution_id} completed with status: {execution_context['status']}")

        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow.workflow_id}: {e}")

    async def execute_workflow_step(self, step: WorkflowStep, execution_context: Dict) -> bool:
        """Execute a single workflow step"""
        try:
            self.logger.info(f"Executing step: {step.step_id} in domain {step.domain.value}")

            # Get domain connector
            if step.domain not in self.domain_connectors:
                self.logger.error(f"No connector registered for domain: {step.domain.value}")
                return False

            connector = self.domain_connectors[step.domain]

            # Execute the action
            result = await connector(step.action, step.parameters, execution_context)

            return result is not False

        except Exception as e:
            self.logger.error(f"Error executing step {step.step_id}: {e}")
            return False

    async def queue_workflow_for_approval(self, workflow: CrossDomainWorkflow, event: CrossDomainEvent):
        """Queue workflow for human approval"""
        try:
            approval_request = {
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.name,
                "trigger_event": event.event_type,
                "event_data": event.data,
                "timestamp": datetime.now().isoformat(),
                "status": "pending_approval"
            }

            approval_file = self.vault_path / "Needs_Action" / f"WORKFLOW_APPROVAL_{workflow.workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            approval_file.parent.mkdir(parents=True, exist_ok=True)

            approval_content = f"""---
type: workflow_approval
workflow_id: {workflow.workflow_id}
priority: high
requires_approval: true
---

# Workflow Approval Required: {workflow.name}

## Trigger Event
- **Type:** {event.event_type}
- **Source:** {event.source_domain.value}
- **Time:** {event.timestamp}

## Event Data
```json
{json.dumps(event.data, indent=2)}
```

## Workflow Description
{workflow.description}

## Planned Steps
{chr(10).join([f"1. **{step.domain.value.title()}:** {step.action}" for step in workflow.steps])}

## Approval Actions
- **To Approve:** Move this file to `/Approved/` folder
- **To Reject:** Move this file to `/Rejected/` folder with comments

---
*Generated by Cross-Domain Integration System*
"""

            approval_file.write_text(approval_content, encoding='utf-8')
            self.logger.info(f"Workflow approval request created: {approval_file}")

        except Exception as e:
            self.logger.error(f"Error creating approval request: {e}")

    async def save_workflow_execution(self, execution_context: Dict):
        """Save workflow execution log"""
        try:
            log_file = self.logs_path / f"workflow_executions_{datetime.now().strftime('%Y-%m')}.json"

            executions = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        executions = json.load(f)
                except:
                    executions = []

            # Convert workflow object to dict for JSON serialization
            execution_log = execution_context.copy()
            execution_log["workflow"] = {
                "workflow_id": execution_context["workflow"].workflow_id,
                "name": execution_context["workflow"].name,
                "description": execution_context["workflow"].description
            }
            execution_log["trigger_event"] = asdict(execution_context["trigger_event"])

            executions.append(execution_log)

            with open(log_file, 'w') as f:
                json.dump(executions, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving workflow execution: {e}")

    def get_workflow_statistics(self) -> Dict:
        """Get workflow execution statistics"""
        try:
            stats = {
                "total_workflows": len(self.workflows),
                "active_executions": len(self.active_workflows),
                "recent_executions": [],
                "success_rate": 0,
                "most_used_workflows": {}
            }

            # Read recent execution logs
            log_files = list(self.logs_path.glob("workflow_executions_*.json"))

            all_executions = []
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        executions = json.load(f)
                        all_executions.extend(executions)
                except:
                    continue

            if all_executions:
                # Calculate success rate
                successful = sum(1 for ex in all_executions if ex.get("status") == "completed")
                stats["success_rate"] = (successful / len(all_executions)) * 100

                # Get recent executions
                stats["recent_executions"] = sorted(
                    all_executions,
                    key=lambda x: x.get("start_time", ""),
                    reverse=True
                )[:10]

                # Count workflow usage
                workflow_counts = {}
                for execution in all_executions:
                    workflow_id = execution.get("workflow", {}).get("workflow_id", "unknown")
                    workflow_counts[workflow_id] = workflow_counts.get(workflow_id, 0) + 1

                stats["most_used_workflows"] = dict(sorted(
                    workflow_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])

            return stats

        except Exception as e:
            self.logger.error(f"Error getting workflow statistics: {e}")
            return {}

async def main():
    """Main function for testing cross-domain integration"""
    vault_path = "AI_Employee_Vault"
    integrator = CrossDomainIntegrator(vault_path)

    print("[CROSS-DOMAIN] Cross-Domain Integration System - Gold Tier")
    print("=" * 50)

    # Display available workflows
    print(f"\n[WORKFLOWS] Available Workflows ({len(integrator.workflows)}):")
    for workflow_id, workflow in integrator.workflows.items():
        print(f"- {workflow.name}: {workflow.description}")

    # Display statistics
    stats = integrator.get_workflow_statistics()
    print(f"\n[STATS] Statistics:")
    print(f"- Total Workflows: {stats['total_workflows']}")
    print(f"- Active Executions: {stats['active_executions']}")
    print(f"- Success Rate: {stats['success_rate']:.1f}%")

    # Test event emission
    test_event = CrossDomainEvent(
        event_id="test_001",
        source_domain=DomainType.EMAIL,
        target_domains=[DomainType.ACCOUNTING, DomainType.SOCIAL_MEDIA],
        event_type="new_client_email",
        data={"client_name": "Test Client", "email": "test@example.com"},
        timestamp=datetime.now().isoformat(),
        requires_approval=True
    )

    await integrator.emit_event(test_event)
    print(f"\n[SUCCESS] Test event emitted: {test_event.event_type}")

    print("\n[READY] Cross-Domain Integration System ready!")
    print("- Workflows are configured and ready")
    print("- Event processing system active")
    print("- Check AI_Employee_Vault/Workflows/ for workflow definitions")
    print("- Check AI_Employee_Vault/Logs/ for execution logs")

if __name__ == "__main__":
    asyncio.run(main())