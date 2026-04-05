#!/usr/bin/env python3
"""
Error Recovery & Graceful Degradation System - Gold Tier Requirement
Ensures AI Employee system remains operational even when components fail
Implements fallback mechanisms and automatic recovery procedures
"""

import asyncio
import json
import logging
import sys
import traceback
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
import subprocess
import psutil

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

class ComponentStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComponentHealth:
    name: str
    status: ComponentStatus
    last_check: str
    error_count: int
    last_error: Optional[str]
    uptime_percentage: float
    response_time_ms: float

@dataclass
class ErrorEvent:
    timestamp: str
    component: str
    error_type: str
    severity: ErrorSeverity
    message: str
    stack_trace: Optional[str]
    recovery_attempted: bool
    recovery_successful: bool

class ErrorRecoverySystem:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "Config" / "error_recovery_config.json"
        self.logs_path = self.vault_path / "Logs"
        self.health_path = self.vault_path / "Health"

        # Create directories
        for path in [self.config_path.parent, self.logs_path, self.health_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'error_recovery.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

        # Component registry
        self.components = {}
        self.component_health = {}
        self.error_history = []
        self.recovery_strategies = {}
        self.fallback_handlers = {}

        # System state
        self.system_degraded = False
        self.critical_components_down = []
        self.monitoring_active = False

        # Initialize components and strategies
        self.initialize_components()
        self.initialize_recovery_strategies()
        self.initialize_fallback_handlers()

    def load_config(self) -> Dict:
        """Load error recovery configuration"""
        default_config = {
            "monitoring_interval_seconds": 60,
            "health_check_timeout_seconds": 30,
            "max_recovery_attempts": 3,
            "recovery_cooldown_minutes": 5,
            "critical_components": [
                "email_system",
                "task_management",
                "vault_storage"
            ],
            "component_definitions": {
                "email_system": {
                    "health_check_method": "check_email_connection",
                    "recovery_method": "restart_email_service",
                    "fallback_method": "email_fallback_mode",
                    "timeout_seconds": 10
                },
                "social_media": {
                    "health_check_method": "check_social_media_apis",
                    "recovery_method": "reconnect_social_apis",
                    "fallback_method": "social_media_offline_mode",
                    "timeout_seconds": 15
                },
                "accounting_system": {
                    "health_check_method": "check_odoo_connection",
                    "recovery_method": "restart_odoo_connection",
                    "fallback_method": "accounting_offline_mode",
                    "timeout_seconds": 20
                },
                "task_management": {
                    "health_check_method": "check_task_system",
                    "recovery_method": "restart_task_system",
                    "fallback_method": "basic_task_mode",
                    "timeout_seconds": 5
                },
                "vault_storage": {
                    "health_check_method": "check_vault_access",
                    "recovery_method": "repair_vault_permissions",
                    "fallback_method": "temporary_storage_mode",
                    "timeout_seconds": 5
                },
                "cross_domain_integration": {
                    "health_check_method": "check_integration_system",
                    "recovery_method": "restart_integration_system",
                    "fallback_method": "manual_workflow_mode",
                    "timeout_seconds": 10
                },
                "ralph_loop": {
                    "health_check_method": "check_ralph_loop",
                    "recovery_method": "restart_ralph_loop",
                    "fallback_method": "manual_monitoring_mode",
                    "timeout_seconds": 5
                }
            },
            "error_thresholds": {
                "error_rate_per_hour": 10,
                "consecutive_failures": 5,
                "response_time_ms": 5000
            },
            "notification_settings": {
                "email_on_critical_error": True,
                "create_task_on_failure": True,
                "log_all_errors": True
            },
            "degradation_levels": {
                "level_1": {
                    "description": "Minor degradation - non-critical features disabled",
                    "disabled_features": ["social_media_auto_post", "content_generation"]
                },
                "level_2": {
                    "description": "Moderate degradation - automation reduced",
                    "disabled_features": ["cross_domain_workflows", "ralph_loop", "auto_scheduling"]
                },
                "level_3": {
                    "description": "Severe degradation - manual mode only",
                    "disabled_features": ["all_automation", "mcp_servers"]
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
        """Save configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def initialize_components(self):
        """Initialize component registry"""
        for component_name, component_config in self.config["component_definitions"].items():
            self.components[component_name] = component_config
            self.component_health[component_name] = ComponentHealth(
                name=component_name,
                status=ComponentStatus.UNKNOWN,
                last_check=datetime.now().isoformat(),
                error_count=0,
                last_error=None,
                uptime_percentage=100.0,
                response_time_ms=0.0
            )

    def initialize_recovery_strategies(self):
        """Initialize recovery strategies for each component"""
        self.recovery_strategies = {
            "email_system": self.recover_email_system,
            "social_media": self.recover_social_media,
            "accounting_system": self.recover_accounting_system,
            "task_management": self.recover_task_management,
            "vault_storage": self.recover_vault_storage,
            "cross_domain_integration": self.recover_cross_domain_integration,
            "ralph_loop": self.recover_ralph_loop
        }

    def initialize_fallback_handlers(self):
        """Initialize fallback handlers for graceful degradation"""
        self.fallback_handlers = {
            "email_system": self.email_fallback_mode,
            "social_media": self.social_media_offline_mode,
            "accounting_system": self.accounting_offline_mode,
            "task_management": self.basic_task_mode,
            "vault_storage": self.temporary_storage_mode,
            "cross_domain_integration": self.manual_workflow_mode,
            "ralph_loop": self.manual_monitoring_mode
        }

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self.monitoring_active = True
        self.logger.info("[MONITOR] Error Recovery System - Starting health monitoring")

        while self.monitoring_active:
            try:
                await self.perform_health_checks()
                await self.analyze_system_health()
                await self.save_health_report()

                await asyncio.sleep(self.config["monitoring_interval_seconds"])

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def perform_health_checks(self):
        """Perform health checks on all components"""
        for component_name in self.components.keys():
            try:
                await self.check_component_health(component_name)
            except Exception as e:
                self.logger.error(f"Health check failed for {component_name}: {e}")
                await self.record_error(component_name, "health_check_failure", ErrorSeverity.MEDIUM, str(e))

    async def check_component_health(self, component_name: str) -> ComponentHealth:
        """Check health of a specific component"""
        start_time = time.time()

        try:
            component_config = self.components[component_name]
            health_check_method = component_config["health_check_method"]

            # Perform health check
            if hasattr(self, health_check_method):
                health_check = getattr(self, health_check_method)
                is_healthy = await health_check()
            else:
                # Default health check
                is_healthy = await self.default_health_check(component_name)

            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Update component health
            health = self.component_health[component_name]
            health.last_check = datetime.now().isoformat()
            health.response_time_ms = response_time

            if is_healthy:
                if health.status == ComponentStatus.FAILED:
                    self.logger.info(f"✅ Component {component_name} recovered")
                health.status = ComponentStatus.HEALTHY
            else:
                health.error_count += 1
                health.status = ComponentStatus.FAILED
                await self.handle_component_failure(component_name)

            return health

        except Exception as e:
            health = self.component_health[component_name]
            health.error_count += 1
            health.last_error = str(e)
            health.status = ComponentStatus.FAILED
            await self.record_error(component_name, "health_check_exception", ErrorSeverity.HIGH, str(e))
            return health

    async def handle_component_failure(self, component_name: str):
        """Handle component failure with recovery attempts"""
        self.logger.warning(f"[WARNING] Component failure detected: {component_name}")

        # Check if component is critical
        if component_name in self.config["critical_components"]:
            self.critical_components_down.append(component_name)
            await self.escalate_critical_failure(component_name)

        # Attempt recovery
        recovery_successful = await self.attempt_recovery(component_name)

        if not recovery_successful:
            # Enable fallback mode
            await self.enable_fallback_mode(component_name)

    async def attempt_recovery(self, component_name: str) -> bool:
        """Attempt to recover a failed component"""
        max_attempts = self.config["max_recovery_attempts"]

        for attempt in range(1, max_attempts + 1):
            self.logger.info(f"[RECOVERY] Recovery attempt {attempt}/{max_attempts} for {component_name}")

            try:
                # Update status to recovering
                self.component_health[component_name].status = ComponentStatus.RECOVERING

                # Execute recovery strategy
                if component_name in self.recovery_strategies:
                    recovery_method = self.recovery_strategies[component_name]
                    success = await recovery_method()

                    if success:
                        self.logger.info(f"[SUCCESS] Recovery successful for {component_name}")
                        await self.record_error(component_name, "recovery_successful", ErrorSeverity.LOW, f"Recovered after {attempt} attempts")
                        return True

                # Wait before next attempt
                if attempt < max_attempts:
                    cooldown = self.config["recovery_cooldown_minutes"] * 60
                    await asyncio.sleep(cooldown)

            except Exception as e:
                self.logger.error(f"Recovery attempt {attempt} failed for {component_name}: {e}")
                await self.record_error(component_name, "recovery_failure", ErrorSeverity.HIGH, str(e))

        self.logger.error(f"[ERROR] All recovery attempts failed for {component_name}")
        return False

    async def enable_fallback_mode(self, component_name: str):
        """Enable fallback mode for a component"""
        self.logger.info(f"[FALLBACK] Enabling fallback mode for {component_name}")

        try:
            if component_name in self.fallback_handlers:
                fallback_handler = self.fallback_handlers[component_name]
                await fallback_handler()

                self.component_health[component_name].status = ComponentStatus.DEGRADED
                self.logger.info(f"[SUCCESS] Fallback mode enabled for {component_name}")

        except Exception as e:
            self.logger.error(f"Failed to enable fallback mode for {component_name}: {e}")

    async def analyze_system_health(self):
        """Analyze overall system health and determine degradation level"""
        failed_components = [name for name, health in self.component_health.items()
                           if health.status == ComponentStatus.FAILED]

        degraded_components = [name for name, health in self.component_health.items()
                             if health.status == ComponentStatus.DEGRADED]

        critical_failures = [name for name in failed_components
                           if name in self.config["critical_components"]]

        # Determine system degradation level
        if critical_failures:
            await self.set_degradation_level("level_3")
        elif len(failed_components) > 2:
            await self.set_degradation_level("level_2")
        elif failed_components or degraded_components:
            await self.set_degradation_level("level_1")
        else:
            await self.clear_degradation()

    async def set_degradation_level(self, level: str):
        """Set system degradation level"""
        if not self.system_degraded or self.current_degradation_level != level:
            self.system_degraded = True
            self.current_degradation_level = level

            degradation_config = self.config["degradation_levels"][level]
            self.logger.warning(f"[CRITICAL] System degradation level set to {level}: {degradation_config['description']}")

            # Create degradation alert
            await self.create_degradation_alert(level, degradation_config)

    async def clear_degradation(self):
        """Clear system degradation when all components are healthy"""
        if self.system_degraded:
            self.system_degraded = False
            self.current_degradation_level = None
            self.critical_components_down.clear()
            self.logger.info("[SUCCESS] System degradation cleared - all components healthy")

    async def record_error(self, component: str, error_type: str, severity: ErrorSeverity, message: str, stack_trace: str = None):
        """Record an error event"""
        error_event = ErrorEvent(
            timestamp=datetime.now().isoformat(),
            component=component,
            error_type=error_type,
            severity=severity,
            message=message,
            stack_trace=stack_trace,
            recovery_attempted=False,
            recovery_successful=False
        )

        self.error_history.append(error_event)

        # Save error to log file
        await self.save_error_event(error_event)

        # Create task for critical errors
        if severity == ErrorSeverity.CRITICAL and self.config["notification_settings"]["create_task_on_failure"]:
            await self.create_error_task(error_event)

    async def save_error_event(self, error_event: ErrorEvent):
        """Save error event to file"""
        try:
            error_file = self.logs_path / f"errors_{datetime.now().strftime('%Y-%m')}.json"

            errors = []
            if error_file.exists():
                try:
                    with open(error_file, 'r') as f:
                        errors = json.load(f)
                except:
                    errors = []

            errors.append(asdict(error_event))

            with open(error_file, 'w') as f:
                json.dump(errors, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save error event: {e}")

    async def save_health_report(self):
        """Save current health report"""
        try:
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "system_degraded": self.system_degraded,
                "degradation_level": getattr(self, 'current_degradation_level', None),
                "critical_components_down": self.critical_components_down,
                "component_health": {
                    name: asdict(health) for name, health in self.component_health.items()
                }
            }

            health_file = self.health_path / f"health_report_{datetime.now().strftime('%Y-%m-%d')}.json"

            with open(health_file, 'w') as f:
                json.dump(health_report, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")

    # Component-specific health checks
    async def check_email_connection(self) -> bool:
        """Check email system health"""
        try:
            # Simulate email connection check
            return True  # In real implementation, would test SMTP/IMAP
        except:
            return False

    async def check_social_media_apis(self) -> bool:
        """Check social media API connections"""
        try:
            # Simulate API connection checks
            return True  # In real implementation, would test API endpoints
        except:
            return False

    async def check_odoo_connection(self) -> bool:
        """Check Odoo accounting system connection"""
        try:
            # Simulate Odoo connection check
            return True  # In real implementation, would test Odoo API
        except:
            return False

    async def check_task_system(self) -> bool:
        """Check task management system"""
        try:
            tasks_file = self.vault_path / "Tasks" / "tasks.json"
            return tasks_file.parent.exists()
        except:
            return False

    async def check_vault_access(self) -> bool:
        """Check vault storage access"""
        try:
            return self.vault_path.exists() and self.vault_path.is_dir()
        except:
            return False

    async def check_integration_system(self) -> bool:
        """Check cross-domain integration system"""
        try:
            # Simulate integration system check
            return True
        except:
            return False

    async def check_ralph_loop(self) -> bool:
        """Check Ralph Wiggum loop status"""
        try:
            state_file = self.vault_path / "State" / "ralph_state.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    state = json.load(f)
                last_run = state.get('last_run')
                if last_run:
                    last_run_time = datetime.fromisoformat(last_run)
                    return (datetime.now() - last_run_time).total_seconds() < 600  # 10 minutes
            return False
        except:
            return False

    async def default_health_check(self, component_name: str) -> bool:
        """Default health check for unknown components"""
        return True

    # Recovery methods
    async def recover_email_system(self) -> bool:
        """Recover email system"""
        try:
            self.logger.info("Attempting to recover email system...")
            # In real implementation, would restart email services
            await asyncio.sleep(2)  # Simulate recovery time
            return True
        except:
            return False

    async def recover_social_media(self) -> bool:
        """Recover social media connections"""
        try:
            self.logger.info("Attempting to recover social media connections...")
            await asyncio.sleep(3)
            return True
        except:
            return False

    async def recover_accounting_system(self) -> bool:
        """Recover accounting system"""
        try:
            self.logger.info("Attempting to recover accounting system...")
            await asyncio.sleep(5)
            return True
        except:
            return False

    async def recover_task_management(self) -> bool:
        """Recover task management system"""
        try:
            self.logger.info("Attempting to recover task management...")
            # Ensure task directories exist
            (self.vault_path / "Tasks").mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

    async def recover_vault_storage(self) -> bool:
        """Recover vault storage"""
        try:
            self.logger.info("Attempting to recover vault storage...")
            # Ensure vault directories exist
            self.vault_path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

    async def recover_cross_domain_integration(self) -> bool:
        """Recover cross-domain integration"""
        try:
            self.logger.info("Attempting to recover cross-domain integration...")
            await asyncio.sleep(2)
            return True
        except:
            return False

    async def recover_ralph_loop(self) -> bool:
        """Recover Ralph Wiggum loop"""
        try:
            self.logger.info("Attempting to recover Ralph loop...")
            # In real implementation, would restart Ralph process
            await asyncio.sleep(1)
            return True
        except:
            return False

    # Fallback modes
    async def email_fallback_mode(self):
        """Enable email fallback mode"""
        self.logger.info("📧 Email system in fallback mode - manual processing only")

    async def social_media_offline_mode(self):
        """Enable social media offline mode"""
        self.logger.info("📱 Social media in offline mode - posts queued for later")

    async def accounting_offline_mode(self):
        """Enable accounting offline mode"""
        self.logger.info("💰 Accounting system in offline mode - manual entry required")

    async def basic_task_mode(self):
        """Enable basic task mode"""
        self.logger.info("📋 Task system in basic mode - limited functionality")

    async def temporary_storage_mode(self):
        """Enable temporary storage mode"""
        self.logger.info("💾 Storage in temporary mode - using backup location")

    async def manual_workflow_mode(self):
        """Enable manual workflow mode"""
        self.logger.info("🔄 Workflows in manual mode - automation disabled")

    async def manual_monitoring_mode(self):
        """Enable manual monitoring mode"""
        self.logger.info("👁️ Monitoring in manual mode - Ralph loop disabled")

    # Alert and task creation
    async def create_degradation_alert(self, level: str, config: Dict):
        """Create system degradation alert"""
        try:
            alert_file = self.vault_path / "Needs_Action" / f"SYSTEM_DEGRADATION_{level}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            alert_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: system_alert
priority: critical
created_by: error_recovery_system
---

# System Degradation Alert - {level.upper()}

**Level:** {level}
**Description:** {config['description']}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Disabled Features
{chr(10).join([f"- {feature}" for feature in config['disabled_features']])}

## Failed Components
{chr(10).join([f"- {comp}" for comp in self.critical_components_down])}

## Action Required
- Investigate component failures
- Restore critical services
- Monitor system recovery

---
*Generated automatically by Error Recovery System*
"""

            alert_file.write_text(content, encoding='utf-8')

        except Exception as e:
            self.logger.error(f"Failed to create degradation alert: {e}")

    async def create_error_task(self, error_event: ErrorEvent):
        """Create task for critical error"""
        try:
            task_file = self.vault_path / "Needs_Action" / f"CRITICAL_ERROR_{error_event.component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            task_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: error_resolution
priority: critical
created_by: error_recovery_system
---

# Critical Error Resolution Required

**Component:** {error_event.component}
**Error Type:** {error_event.error_type}
**Severity:** {error_event.severity.value}
**Time:** {error_event.timestamp}

## Error Message
{error_event.message}

## Stack Trace
```
{error_event.stack_trace or 'No stack trace available'}
```

## Action Required
- Investigate root cause
- Implement fix
- Test component functionality
- Update error recovery procedures if needed

---
*Generated automatically by Error Recovery System*
"""

            task_file.write_text(content, encoding='utf-8')

        except Exception as e:
            self.logger.error(f"Failed to create error task: {e}")

    async def escalate_critical_failure(self, component_name: str):
        """Escalate critical component failure"""
        self.logger.critical(f"[CRITICAL] CRITICAL FAILURE: {component_name}")
        await self.record_error(component_name, "critical_failure", ErrorSeverity.CRITICAL, f"Critical component {component_name} has failed")

    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            "system_degraded": self.system_degraded,
            "degradation_level": getattr(self, 'current_degradation_level', None),
            "monitoring_active": self.monitoring_active,
            "critical_components_down": self.critical_components_down,
            "component_health": {
                name: {
                    "status": health.status.value,
                    "error_count": health.error_count,
                    "last_error": health.last_error,
                    "uptime_percentage": health.uptime_percentage,
                    "response_time_ms": health.response_time_ms
                }
                for name, health in self.component_health.items()
            },
            "recent_errors": len([e for e in self.error_history if
                                (datetime.now() - datetime.fromisoformat(e.timestamp)).total_seconds() < 3600])
        }

    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        self.logger.info("🛑 Error Recovery System - Monitoring stopped")

async def main():
    """Main function for testing error recovery system"""
    vault_path = "AI_Employee_Vault"
    recovery_system = ErrorRecoverySystem(vault_path)

    print("[ERROR RECOVERY] Error Recovery & Graceful Degradation System - Gold Tier")
    print("=" * 60)

    # Show system status
    status = recovery_system.get_system_status()
    print(f"\n[STATUS] System Status:")
    print(f"- System Degraded: {status['system_degraded']}")
    print(f"- Monitoring Active: {status['monitoring_active']}")
    print(f"- Components Monitored: {len(status['component_health'])}")

    print(f"\n[HEALTH] Component Health:")
    for name, health in status['component_health'].items():
        status_emoji = "[OK]" if health['status'] == 'healthy' else "[FAIL]" if health['status'] == 'failed' else "[WARN]"
        print(f"  {status_emoji} {name}: {health['status']}")

    print(f"\n[START] Starting health monitoring...")
    print("Press Ctrl+C to stop monitoring")

    try:
        await recovery_system.start_monitoring()
    except KeyboardInterrupt:
        print("\n[STOP] Stopping Error Recovery System...")
        recovery_system.stop_monitoring()
    except Exception as e:
        print(f"[ERROR] System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())