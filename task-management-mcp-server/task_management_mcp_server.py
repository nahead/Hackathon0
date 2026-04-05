#!/usr/bin/env python3
"""
Task Management MCP Server - Model Context Protocol Server for Task and Scheduling Operations
Provides Claude Code with task management and scheduling capabilities
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import uuid

class TaskManagementMCPServer:
    def __init__(self):
        self.vault_path = Path("AI_Employee_Vault")
        self.config_path = self.vault_path / "Config" / "task_management_config.json"
        self.logs_path = self.vault_path / "Logs"
        self.tasks_path = self.vault_path / "Tasks"
        self.schedules_path = self.vault_path / "Schedules"

        # Create directories
        for path in [self.config_path.parent, self.logs_path, self.tasks_path, self.schedules_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'task_management_mcp.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

        # Task storage
        self.tasks_file = self.tasks_path / "tasks.json"
        self.schedules_file = self.schedules_path / "schedules.json"

    def load_config(self) -> Dict:
        """Load task management configuration"""
        default_config = {
            "task_categories": [
                "email_response",
                "social_media",
                "accounting",
                "client_communication",
                "content_creation",
                "business_development",
                "administrative"
            ],
            "priority_levels": ["low", "medium", "high", "urgent"],
            "default_task_duration": 30,  # minutes
            "auto_schedule_tasks": True,
            "working_hours": {
                "start": "09:00",
                "end": "17:00",
                "timezone": "UTC"
            },
            "task_templates": {
                "client_followup": {
                    "title": "Follow up with {client_name}",
                    "description": "Follow up on previous communication with {client_name}",
                    "category": "client_communication",
                    "estimated_duration": 15,
                    "priority": "medium"
                },
                "invoice_generation": {
                    "title": "Generate invoice for {client_name}",
                    "description": "Create and send invoice for services provided to {client_name}",
                    "category": "accounting",
                    "estimated_duration": 20,
                    "priority": "high"
                },
                "content_creation": {
                    "title": "Create content for {platform}",
                    "description": "Develop engaging content for {platform} posting",
                    "category": "content_creation",
                    "estimated_duration": 45,
                    "priority": "medium"
                }
            },
            "recurring_schedules": {
                "daily_briefing": {
                    "title": "Generate Daily Business Briefing",
                    "frequency": "daily",
                    "time": "08:00",
                    "category": "administrative"
                },
                "weekly_audit": {
                    "title": "Conduct Weekly Business Audit",
                    "frequency": "weekly",
                    "day": "sunday",
                    "time": "20:00",
                    "category": "administrative"
                }
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
        """Save task management configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests for task management operations"""
        try:
            method = request.get('method')
            params = request.get('params', {})

            if method == 'task.create':
                return await self.create_task(params)
            elif method == 'task.update':
                return await self.update_task(params)
            elif method == 'task.complete':
                return await self.complete_task(params)
            elif method == 'task.delete':
                return await self.delete_task(params)
            elif method == 'task.list':
                return await self.list_tasks(params)
            elif method == 'task.get':
                return await self.get_task(params)
            elif method == 'task.create_from_template':
                return await self.create_task_from_template(params)
            elif method == 'schedule.create':
                return await self.create_schedule(params)
            elif method == 'schedule.list':
                return await self.list_schedules(params)
            elif method == 'schedule.delete':
                return await self.delete_schedule(params)
            elif method == 'task.get_statistics':
                return await self.get_task_statistics(params)
            elif method == 'task.create_briefing_task':
                return await self.create_briefing_task(params)
            else:
                return {
                    'error': f'Unknown method: {method}',
                    'available_methods': [
                        'task.create',
                        'task.update',
                        'task.complete',
                        'task.delete',
                        'task.list',
                        'task.get',
                        'task.create_from_template',
                        'schedule.create',
                        'schedule.list',
                        'schedule.delete',
                        'task.get_statistics',
                        'task.create_briefing_task'
                    ]
                }

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}

    async def create_task(self, params: Dict) -> Dict:
        """Create a new task"""
        try:
            title = params.get('title')
            description = params.get('description', '')
            category = params.get('category', 'administrative')
            priority = params.get('priority', 'medium')
            due_date = params.get('due_date')
            estimated_duration = params.get('estimated_duration', self.config['default_task_duration'])

            if not title:
                return {'error': 'title is required'}

            # Validate inputs
            if category not in self.config['task_categories']:
                return {'error': f'Invalid category. Must be one of: {self.config["task_categories"]}'}

            if priority not in self.config['priority_levels']:
                return {'error': f'Invalid priority. Must be one of: {self.config["priority_levels"]}'}

            # Create task
            task = {
                'id': str(uuid.uuid4()),
                'title': title,
                'description': description,
                'category': category,
                'priority': priority,
                'status': 'pending',
                'due_date': due_date,
                'estimated_duration': estimated_duration,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'completed_at': None
            }

            # Save task
            tasks = self.load_tasks()
            tasks.append(task)
            self.save_tasks(tasks)

            self.logger.info(f"Created task: {task['id']} - {title}")

            return {
                'success': True,
                'task_id': task['id'],
                'task': task
            }

        except Exception as e:
            return {'error': str(e)}

    async def update_task(self, params: Dict) -> Dict:
        """Update an existing task"""
        try:
            task_id = params.get('task_id')
            updates = params.get('updates', {})

            if not task_id:
                return {'error': 'task_id is required'}

            tasks = self.load_tasks()
            task_found = False

            for task in tasks:
                if task['id'] == task_id:
                    # Update allowed fields
                    allowed_fields = ['title', 'description', 'category', 'priority', 'due_date', 'estimated_duration', 'status']
                    for field, value in updates.items():
                        if field in allowed_fields:
                            task[field] = value

                    task['updated_at'] = datetime.now().isoformat()
                    task_found = True
                    break

            if not task_found:
                return {'error': f'Task {task_id} not found'}

            self.save_tasks(tasks)

            return {
                'success': True,
                'message': f'Task {task_id} updated successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    async def complete_task(self, params: Dict) -> Dict:
        """Mark a task as completed"""
        try:
            task_id = params.get('task_id')
            completion_notes = params.get('notes', '')

            if not task_id:
                return {'error': 'task_id is required'}

            tasks = self.load_tasks()
            task_found = False

            for task in tasks:
                if task['id'] == task_id:
                    task['status'] = 'completed'
                    task['completed_at'] = datetime.now().isoformat()
                    task['updated_at'] = datetime.now().isoformat()
                    if completion_notes:
                        task['completion_notes'] = completion_notes
                    task_found = True
                    break

            if not task_found:
                return {'error': f'Task {task_id} not found'}

            self.save_tasks(tasks)
            self.logger.info(f"Completed task: {task_id}")

            return {
                'success': True,
                'message': f'Task {task_id} marked as completed'
            }

        except Exception as e:
            return {'error': str(e)}

    async def delete_task(self, params: Dict) -> Dict:
        """Delete a task"""
        try:
            task_id = params.get('task_id')

            if not task_id:
                return {'error': 'task_id is required'}

            tasks = self.load_tasks()
            original_count = len(tasks)
            tasks = [task for task in tasks if task['id'] != task_id]

            if len(tasks) == original_count:
                return {'error': f'Task {task_id} not found'}

            self.save_tasks(tasks)
            self.logger.info(f"Deleted task: {task_id}")

            return {
                'success': True,
                'message': f'Task {task_id} deleted successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    async def list_tasks(self, params: Dict) -> Dict:
        """List tasks with optional filtering"""
        try:
            status = params.get('status')
            category = params.get('category')
            priority = params.get('priority')
            limit = params.get('limit', 50)

            tasks = self.load_tasks()

            # Apply filters
            if status:
                tasks = [task for task in tasks if task.get('status') == status]

            if category:
                tasks = [task for task in tasks if task.get('category') == category]

            if priority:
                tasks = [task for task in tasks if task.get('priority') == priority]

            # Sort by priority and due date
            priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
            tasks.sort(key=lambda x: (
                priority_order.get(x.get('priority', 'medium'), 2),
                x.get('due_date') or '9999-12-31',
                x.get('created_at')
            ))

            # Apply limit
            tasks = tasks[:limit]

            return {
                'success': True,
                'tasks': tasks,
                'count': len(tasks)
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_task(self, params: Dict) -> Dict:
        """Get a specific task by ID"""
        try:
            task_id = params.get('task_id')

            if not task_id:
                return {'error': 'task_id is required'}

            tasks = self.load_tasks()

            for task in tasks:
                if task['id'] == task_id:
                    return {
                        'success': True,
                        'task': task
                    }

            return {'error': f'Task {task_id} not found'}

        except Exception as e:
            return {'error': str(e)}

    async def create_task_from_template(self, params: Dict) -> Dict:
        """Create a task from a predefined template"""
        try:
            template_name = params.get('template')
            variables = params.get('variables', {})

            if not template_name:
                return {'error': 'template is required'}

            if template_name not in self.config['task_templates']:
                return {'error': f'Template {template_name} not found'}

            template = self.config['task_templates'][template_name]

            # Replace variables in template
            task_data = {}
            for key, value in template.items():
                if isinstance(value, str):
                    for var_name, var_value in variables.items():
                        value = value.replace(f'{{{var_name}}}', str(var_value))
                task_data[key] = value

            # Add any additional parameters
            for key, value in params.items():
                if key not in ['template', 'variables']:
                    task_data[key] = value

            return await self.create_task(task_data)

        except Exception as e:
            return {'error': str(e)}

    async def create_schedule(self, params: Dict) -> Dict:
        """Create a recurring schedule"""
        try:
            name = params.get('name')
            frequency = params.get('frequency')  # daily, weekly, monthly
            time = params.get('time')
            task_template = params.get('task_template', {})

            if not all([name, frequency, time]):
                return {'error': 'name, frequency, and time are required'}

            schedule = {
                'id': str(uuid.uuid4()),
                'name': name,
                'frequency': frequency,
                'time': time,
                'task_template': task_template,
                'created_at': datetime.now().isoformat(),
                'active': True
            }

            # Add day for weekly schedules
            if frequency == 'weekly':
                schedule['day'] = params.get('day', 'monday')

            schedules = self.load_schedules()
            schedules.append(schedule)
            self.save_schedules(schedules)

            return {
                'success': True,
                'schedule_id': schedule['id'],
                'schedule': schedule
            }

        except Exception as e:
            return {'error': str(e)}

    async def list_schedules(self, params: Dict) -> Dict:
        """List all schedules"""
        try:
            schedules = self.load_schedules()

            active_only = params.get('active_only', False)
            if active_only:
                schedules = [s for s in schedules if s.get('active', True)]

            return {
                'success': True,
                'schedules': schedules,
                'count': len(schedules)
            }

        except Exception as e:
            return {'error': str(e)}

    async def delete_schedule(self, params: Dict) -> Dict:
        """Delete a schedule"""
        try:
            schedule_id = params.get('schedule_id')

            if not schedule_id:
                return {'error': 'schedule_id is required'}

            schedules = self.load_schedules()
            original_count = len(schedules)
            schedules = [s for s in schedules if s['id'] != schedule_id]

            if len(schedules) == original_count:
                return {'error': f'Schedule {schedule_id} not found'}

            self.save_schedules(schedules)

            return {
                'success': True,
                'message': f'Schedule {schedule_id} deleted successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_task_statistics(self, params: Dict) -> Dict:
        """Get task statistics"""
        try:
            period = params.get('period', 'week')  # day, week, month

            tasks = self.load_tasks()

            # Calculate statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
            pending_tasks = len([t for t in tasks if t.get('status') == 'pending'])
            overdue_tasks = 0

            # Count overdue tasks
            now = datetime.now()
            for task in tasks:
                if task.get('due_date') and task.get('status') != 'completed':
                    due_date = datetime.fromisoformat(task['due_date'])
                    if due_date < now:
                        overdue_tasks += 1

            # Category breakdown
            category_stats = {}
            for task in tasks:
                category = task.get('category', 'unknown')
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'completed': 0}
                category_stats[category]['total'] += 1
                if task.get('status') == 'completed':
                    category_stats[category]['completed'] += 1

            # Calculate completion rate
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            statistics = {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round(completion_rate, 1),
                'category_breakdown': category_stats,
                'period': period
            }

            return {
                'success': True,
                'statistics': statistics
            }

        except Exception as e:
            return {'error': str(e)}

    async def create_briefing_task(self, params: Dict) -> Dict:
        """Create a briefing task for cross-domain workflows"""
        try:
            priority = params.get('priority', 'high')
            days_ahead = params.get('days_ahead', 0)

            due_date = None
            if days_ahead > 0:
                due_date = (datetime.now() + timedelta(days=days_ahead)).isoformat()

            task_data = {
                'title': 'CEO Briefing Preparation',
                'description': 'Prepare comprehensive CEO briefing with latest business metrics and insights',
                'category': 'administrative',
                'priority': priority,
                'due_date': due_date,
                'estimated_duration': 60
            }

            return await self.create_task(task_data)

        except Exception as e:
            return {'error': str(e)}

    def load_tasks(self) -> List[Dict]:
        """Load tasks from file"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading tasks: {e}")
            return []

    def save_tasks(self, tasks: List[Dict]):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, 'w') as f:
                json.dump(tasks, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving tasks: {e}")

    def load_schedules(self) -> List[Dict]:
        """Load schedules from file"""
        try:
            if self.schedules_file.exists():
                with open(self.schedules_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")
            return []

    def save_schedules(self, schedules: List[Dict]):
        """Save schedules to file"""
        try:
            with open(self.schedules_file, 'w') as f:
                json.dump(schedules, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")

# MCP Server Protocol Implementation
async def main():
    """Main MCP server loop"""
    server = TaskManagementMCPServer()

    print("[TASK MCP] Task Management MCP Server starting...")
    print("Available methods:")
    print("- task.create")
    print("- task.update")
    print("- task.complete")
    print("- task.delete")
    print("- task.list")
    print("- task.get")
    print("- task.create_from_template")
    print("- schedule.create")
    print("- schedule.list")
    print("- schedule.delete")
    print("- task.get_statistics")
    print("- task.create_briefing_task")

    # Simple JSON-RPC over stdin/stdout for MCP
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line.strip())
            response = await server.handle_request(request)

            # Add JSON-RPC envelope
            rpc_response = {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': response
            }

            print(json.dumps(rpc_response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': 'Parse error'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': request.get('id') if 'request' in locals() else None,
                'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Task Management MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)