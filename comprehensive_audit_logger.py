#!/usr/bin/env python3
"""
Comprehensive Audit Logging System - Gold Tier Requirement
Tracks all system activities, decisions, and changes for compliance and analysis
Provides detailed audit trails for business operations and AI decision-making
"""

import asyncio
import json
import logging
import sys
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3
import threading
from contextlib import contextmanager

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

class AuditEventType(Enum):
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    USER_ACTION = "user_action"
    AI_DECISION = "ai_decision"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    EMAIL_SENT = "email_sent"
    EMAIL_RECEIVED = "email_received"
    SOCIAL_MEDIA_POST = "social_media_post"
    FINANCIAL_TRANSACTION = "financial_transaction"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    WORKFLOW_EXECUTED = "workflow_executed"
    ERROR_OCCURRED = "error_occurred"
    SECURITY_EVENT = "security_event"
    CONFIGURATION_CHANGE = "configuration_change"
    BACKUP_CREATED = "backup_created"
    RECOVERY_PERFORMED = "recovery_performed"

class AuditLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AuditEvent:
    id: str
    timestamp: str
    event_type: AuditEventType
    level: AuditLevel
    component: str
    user_id: Optional[str]
    session_id: Optional[str]
    action: str
    description: str
    data_before: Optional[Dict]
    data_after: Optional[Dict]
    metadata: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    error_message: Optional[str]
    duration_ms: Optional[float]
    checksum: str

class ComprehensiveAuditLogger:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "Config" / "audit_config.json"
        self.logs_path = self.vault_path / "Logs" / "Audit"
        self.db_path = self.logs_path / "audit.db"

        # Create directories
        for path in [self.config_path.parent, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'audit_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

        # Initialize database
        self.init_database()

        # Thread safety
        self.lock = threading.Lock()

        # Session tracking
        self.current_session_id = str(uuid.uuid4())
        self.session_start_time = datetime.now()

        # Audit statistics
        self.stats = {
            "total_events": 0,
            "events_by_type": {},
            "events_by_component": {},
            "errors_logged": 0,
            "session_count": 0
        }

        # Start audit session
        self.log_audit_event(
            event_type=AuditEventType.SYSTEM_START,
            component="audit_system",
            action="system_startup",
            description="Comprehensive Audit Logging System started",
            success=True
        )

    def load_config(self) -> Dict:
        """Load audit logging configuration"""
        default_config = {
            "enabled": True,
            "log_levels": ["info", "warning", "error", "critical"],
            "retention_days": 365,
            "max_log_file_size_mb": 100,
            "enable_database_logging": True,
            "enable_file_logging": True,
            "enable_real_time_monitoring": True,
            "sensitive_data_fields": [
                "password", "token", "api_key", "secret", "private_key"
            ],
            "audit_components": [
                "email_system",
                "social_media",
                "accounting_system",
                "task_management",
                "cross_domain_integration",
                "ralph_loop",
                "error_recovery",
                "user_interface"
            ],
            "compliance_settings": {
                "gdpr_compliance": True,
                "data_anonymization": True,
                "audit_trail_integrity": True,
                "tamper_detection": True
            },
            "alert_thresholds": {
                "error_rate_per_hour": 50,
                "failed_login_attempts": 5,
                "data_access_anomalies": 10,
                "system_performance_degradation": 20
            },
            "export_formats": ["json", "csv", "xml"],
            "backup_settings": {
                "auto_backup": True,
                "backup_frequency_hours": 24,
                "backup_retention_days": 90
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

    def init_database(self):
        """Initialize SQLite database for audit logs"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        level TEXT NOT NULL,
                        component TEXT NOT NULL,
                        user_id TEXT,
                        session_id TEXT,
                        action TEXT NOT NULL,
                        description TEXT NOT NULL,
                        data_before TEXT,
                        data_after TEXT,
                        metadata TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        duration_ms REAL,
                        checksum TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_event_type ON audit_events(event_type)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_component ON audit_events(component)
                ''')

                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_session_id ON audit_events(session_id)
                ''')

                conn.commit()

            self.logger.info("[SUCCESS] Audit database initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize audit database: {e}")

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def log_audit_event(
        self,
        event_type: AuditEventType,
        component: str,
        action: str,
        description: str,
        success: bool = True,
        level: AuditLevel = AuditLevel.INFO,
        user_id: Optional[str] = None,
        data_before: Optional[Dict] = None,
        data_after: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Log an audit event"""

        if not self.config.get("enabled", True):
            return ""

        try:
            with self.lock:
                # Create audit event
                event_id = str(uuid.uuid4())
                timestamp = datetime.now().isoformat()

                # Sanitize sensitive data
                if data_before:
                    data_before = self.sanitize_sensitive_data(data_before)
                if data_after:
                    data_after = self.sanitize_sensitive_data(data_after)
                if metadata:
                    metadata = self.sanitize_sensitive_data(metadata)

                # Create event object
                audit_event = AuditEvent(
                    id=event_id,
                    timestamp=timestamp,
                    event_type=event_type,
                    level=level,
                    component=component,
                    user_id=user_id,
                    session_id=self.current_session_id,
                    action=action,
                    description=description,
                    data_before=data_before,
                    data_after=data_after,
                    metadata=metadata or {},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=success,
                    error_message=error_message,
                    duration_ms=duration_ms,
                    checksum=self.calculate_checksum(event_id, timestamp, action, description)
                )

                # Store in database
                if self.config.get("enable_database_logging", True):
                    self.store_in_database(audit_event)

                # Store in file
                if self.config.get("enable_file_logging", True):
                    self.store_in_file(audit_event)

                # Update statistics
                self.update_statistics(audit_event)

                # Check for alerts
                self.check_alert_conditions(audit_event)

                return event_id

        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            return ""

    def sanitize_sensitive_data(self, data: Dict) -> Dict:
        """Remove or mask sensitive data fields"""
        if not isinstance(data, dict):
            return data

        sanitized = data.copy()
        sensitive_fields = self.config.get("sensitive_data_fields", [])

        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***REDACTED***"

        return sanitized

    def calculate_checksum(self, event_id: str, timestamp: str, action: str, description: str) -> str:
        """Calculate checksum for tamper detection"""
        content = f"{event_id}{timestamp}{action}{description}"
        return hashlib.sha256(content.encode()).hexdigest()

    def store_in_database(self, event: AuditEvent):
        """Store audit event in database"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO audit_events (
                        id, timestamp, event_type, level, component, user_id, session_id,
                        action, description, data_before, data_after, metadata,
                        ip_address, user_agent, success, error_message, duration_ms, checksum
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.id,
                    event.timestamp,
                    event.event_type.value,
                    event.level.value,
                    event.component,
                    event.user_id,
                    event.session_id,
                    event.action,
                    event.description,
                    json.dumps(event.data_before) if event.data_before else None,
                    json.dumps(event.data_after) if event.data_after else None,
                    json.dumps(event.metadata),
                    event.ip_address,
                    event.user_agent,
                    event.success,
                    event.error_message,
                    event.duration_ms,
                    event.checksum
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to store audit event in database: {e}")

    def store_in_file(self, event: AuditEvent):
        """Store audit event in file"""
        try:
            # Create daily log file
            log_date = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_path / f"audit_{log_date}.json"

            # Load existing events
            events = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        events = json.load(f)
                except:
                    events = []

            # Add new event
            events.append(asdict(event))

            # Save events
            with open(log_file, 'w') as f:
                json.dump(events, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to store audit event in file: {e}")

    def update_statistics(self, event: AuditEvent):
        """Update audit statistics"""
        try:
            self.stats["total_events"] += 1

            # Count by event type
            event_type = event.event_type.value
            self.stats["events_by_type"][event_type] = self.stats["events_by_type"].get(event_type, 0) + 1

            # Count by component
            component = event.component
            self.stats["events_by_component"][component] = self.stats["events_by_component"].get(component, 0) + 1

            # Count errors
            if not event.success or event.level in [AuditLevel.ERROR, AuditLevel.CRITICAL]:
                self.stats["errors_logged"] += 1

        except Exception as e:
            self.logger.error(f"Failed to update statistics: {e}")

    def check_alert_conditions(self, event: AuditEvent):
        """Check if event triggers any alert conditions"""
        try:
            thresholds = self.config.get("alert_thresholds", {})

            # Check error rate
            if not event.success and thresholds.get("error_rate_per_hour"):
                recent_errors = self.get_recent_error_count(hours=1)
                if recent_errors >= thresholds["error_rate_per_hour"]:
                    self.create_alert("high_error_rate", f"Error rate exceeded: {recent_errors} errors in last hour")

            # Check for security events
            if event.event_type == AuditEventType.SECURITY_EVENT:
                self.create_alert("security_event", f"Security event detected: {event.description}")

        except Exception as e:
            self.logger.error(f"Failed to check alert conditions: {e}")

    def get_recent_error_count(self, hours: int = 1) -> int:
        """Get count of recent errors"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

            with self.get_db_connection() as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM audit_events
                    WHERE timestamp >= ? AND success = 0
                ''', (cutoff_time,))
                return cursor.fetchone()[0]

        except Exception as e:
            self.logger.error(f"Failed to get recent error count: {e}")
            return 0

    def create_alert(self, alert_type: str, message: str):
        """Create system alert"""
        try:
            alert_file = self.vault_path / "Needs_Action" / f"AUDIT_ALERT_{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            alert_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: audit_alert
priority: high
created_by: audit_system
---

# Audit System Alert: {alert_type.replace('_', ' ').title()}

**Alert Type:** {alert_type}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Message:** {message}

## Action Required
- Investigate the alert condition
- Take appropriate corrective action
- Review audit logs for additional context

---
*Generated automatically by Comprehensive Audit Logging System*
"""

            alert_file.write_text(content, encoding='utf-8')
            self.logger.warning(f"[ALERT] Audit alert created: {alert_type}")

        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")

    def query_audit_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        component: Optional[str] = None,
        user_id: Optional[str] = None,
        success: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query audit events with filters"""
        try:
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)

            if component:
                query += " AND component = ?"
                params.append(component)

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if success is not None:
                query += " AND success = ?"
                params.append(success)

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            with self.get_db_connection() as conn:
                cursor = conn.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.logger.error(f"Failed to query audit events: {e}")
            return []

    def export_audit_logs(
        self,
        format_type: str = "json",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        output_file: Optional[str] = None
    ) -> Optional[str]:
        """Export audit logs in specified format"""
        try:
            # Query events
            events = self.query_audit_events(
                start_date=start_date,
                end_date=end_date,
                limit=10000  # Large limit for export
            )

            if not events:
                return None

            # Generate filename if not provided
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = str(self.logs_path / f"audit_export_{timestamp}.{format_type}")

            # Export based on format
            if format_type == "json":
                with open(output_file, 'w') as f:
                    json.dump(events, f, indent=2, default=str)

            elif format_type == "csv":
                import csv
                with open(output_file, 'w', newline='') as f:
                    if events:
                        writer = csv.DictWriter(f, fieldnames=events[0].keys())
                        writer.writeheader()
                        writer.writerows(events)

            elif format_type == "xml":
                import xml.etree.ElementTree as ET
                root = ET.Element("audit_events")
                for event in events:
                    event_elem = ET.SubElement(root, "event")
                    for key, value in event.items():
                        elem = ET.SubElement(event_elem, key)
                        elem.text = str(value) if value is not None else ""

                tree = ET.ElementTree(root)
                tree.write(output_file, encoding='utf-8', xml_declaration=True)

            self.logger.info(f"[SUCCESS] Audit logs exported to {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Failed to export audit logs: {e}")
            return None

    def verify_audit_integrity(self) -> Dict[str, Any]:
        """Verify integrity of audit logs"""
        try:
            integrity_report = {
                "total_events_checked": 0,
                "checksum_failures": 0,
                "tampered_events": [],
                "integrity_status": "unknown",
                "last_check": datetime.now().isoformat()
            }

            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT id, timestamp, action, description, checksum FROM audit_events")

                for row in cursor.fetchall():
                    integrity_report["total_events_checked"] += 1

                    # Recalculate checksum
                    expected_checksum = self.calculate_checksum(row[0], row[1], row[2], row[3])

                    if expected_checksum != row[4]:
                        integrity_report["checksum_failures"] += 1
                        integrity_report["tampered_events"].append({
                            "event_id": row[0],
                            "timestamp": row[1],
                            "expected_checksum": expected_checksum,
                            "actual_checksum": row[4]
                        })

            # Determine integrity status
            if integrity_report["checksum_failures"] == 0:
                integrity_report["integrity_status"] = "intact"
            elif integrity_report["checksum_failures"] < 5:
                integrity_report["integrity_status"] = "minor_issues"
            else:
                integrity_report["integrity_status"] = "compromised"

            return integrity_report

        except Exception as e:
            self.logger.error(f"Failed to verify audit integrity: {e}")
            return {"integrity_status": "error", "error": str(e)}

    def cleanup_old_logs(self):
        """Clean up old audit logs based on retention policy"""
        try:
            retention_days = self.config.get("retention_days", 365)
            cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()

            # Clean database
            with self.get_db_connection() as conn:
                cursor = conn.execute("DELETE FROM audit_events WHERE timestamp < ?", (cutoff_date,))
                deleted_count = cursor.rowcount
                conn.commit()

            # Clean log files
            cutoff_file_date = datetime.now() - timedelta(days=retention_days)
            for log_file in self.logs_path.glob("audit_*.json"):
                try:
                    file_date_str = log_file.stem.split("_")[1]  # Extract date from filename
                    file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                    if file_date < cutoff_file_date:
                        log_file.unlink()
                except:
                    continue

            self.logger.info(f"[CLEANUP] Cleaned up {deleted_count} old audit records")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")

    def get_audit_statistics(self) -> Dict[str, Any]:
        """Get comprehensive audit statistics"""
        try:
            stats = self.stats.copy()

            # Add database statistics
            with self.get_db_connection() as conn:
                # Total events in database
                cursor = conn.execute("SELECT COUNT(*) FROM audit_events")
                stats["total_events_in_db"] = cursor.fetchone()[0]

                # Events by day (last 7 days)
                stats["events_by_day"] = {}
                for i in range(7):
                    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM audit_events WHERE date(timestamp) = ?",
                        (date,)
                    )
                    stats["events_by_day"][date] = cursor.fetchone()[0]

                # Success rate
                cursor = conn.execute("SELECT COUNT(*) FROM audit_events WHERE success = 1")
                successful_events = cursor.fetchone()[0]
                if stats["total_events_in_db"] > 0:
                    stats["success_rate"] = (successful_events / stats["total_events_in_db"]) * 100
                else:
                    stats["success_rate"] = 100

            # Session information
            stats["current_session_id"] = self.current_session_id
            stats["session_duration_minutes"] = (datetime.now() - self.session_start_time).total_seconds() / 60

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get audit statistics: {e}")
            return self.stats

    def close_audit_session(self):
        """Close current audit session"""
        try:
            self.log_audit_event(
                event_type=AuditEventType.SYSTEM_STOP,
                component="audit_system",
                action="system_shutdown",
                description="Comprehensive Audit Logging System stopped",
                success=True,
                metadata={
                    "session_duration_minutes": (datetime.now() - self.session_start_time).total_seconds() / 60,
                    "total_events_logged": self.stats["total_events"]
                }
            )

            self.logger.info("[SESSION] Audit session closed")

        except Exception as e:
            self.logger.error(f"Failed to close audit session: {e}")

# Convenience functions for common audit events
def log_user_action(audit_logger, user_id: str, action: str, description: str, success: bool = True):
    """Log user action"""
    return audit_logger.log_audit_event(
        event_type=AuditEventType.USER_ACTION,
        component="user_interface",
        action=action,
        description=description,
        success=success,
        user_id=user_id
    )

def log_ai_decision(audit_logger, component: str, decision: str, reasoning: str, confidence: float):
    """Log AI decision"""
    return audit_logger.log_audit_event(
        event_type=AuditEventType.AI_DECISION,
        component=component,
        action="ai_decision",
        description=f"AI Decision: {decision}",
        success=True,
        metadata={
            "reasoning": reasoning,
            "confidence": confidence,
            "decision_type": "automated"
        }
    )

def log_data_access(audit_logger, component: str, data_type: str, access_type: str, user_id: str = None):
    """Log data access"""
    return audit_logger.log_audit_event(
        event_type=AuditEventType.DATA_ACCESS,
        component=component,
        action=f"data_{access_type}",
        description=f"Accessed {data_type} data",
        success=True,
        user_id=user_id,
        metadata={"data_type": data_type, "access_type": access_type}
    )

async def main():
    """Main function for testing audit logging system"""
    vault_path = "AI_Employee_Vault"
    audit_logger = ComprehensiveAuditLogger(vault_path)

    print("[AUDIT] Comprehensive Audit Logging System - Gold Tier")
    print("=" * 60)

    # Show statistics
    stats = audit_logger.get_audit_statistics()
    print(f"\n[STATS] Audit Statistics:")
    print(f"- Total Events: {stats['total_events']}")
    print(f"- Events in Database: {stats.get('total_events_in_db', 0)}")
    print(f"- Success Rate: {stats.get('success_rate', 0):.1f}%")
    print(f"- Current Session: {stats['current_session_id'][:8]}...")

    # Test logging various event types
    print(f"\n[TEST] Testing audit logging...")

    # Test user action
    log_user_action(audit_logger, "test_user", "login", "User logged into system")

    # Test AI decision
    log_ai_decision(audit_logger, "ralph_loop", "create_task", "Task creation needed based on email analysis", 0.85)

    # Test data access
    log_data_access(audit_logger, "email_system", "emails", "read", "test_user")

    # Test error logging
    audit_logger.log_audit_event(
        event_type=AuditEventType.ERROR_OCCURRED,
        component="social_media",
        action="post_creation",
        description="Failed to post to social media",
        success=False,
        level=AuditLevel.ERROR,
        error_message="API rate limit exceeded"
    )

    # Verify integrity
    print(f"\n[VERIFY] Verifying audit integrity...")
    integrity_report = audit_logger.verify_audit_integrity()
    print(f"- Integrity Status: {integrity_report['integrity_status']}")
    print(f"- Events Checked: {integrity_report['total_events_checked']}")
    print(f"- Checksum Failures: {integrity_report['checksum_failures']}")

    # Export logs
    print(f"\n[EXPORT] Exporting audit logs...")
    export_file = audit_logger.export_audit_logs("json")
    if export_file:
        print(f"- Exported to: {export_file}")

    print(f"\n[SUCCESS] Audit logging system operational!")
    print("- All events are being logged and tracked")
    print("- Integrity verification active")
    print("- Export capabilities available")

    # Close session
    audit_logger.close_audit_session()

if __name__ == "__main__":
    asyncio.run(main())