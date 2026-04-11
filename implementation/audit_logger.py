#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger - Track all AI Employee actions
"""

import json
from pathlib import Path
from datetime import datetime


class AuditLogger:
    """Centralized audit logging for all AI Employee actions"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def log_action(self, action_type, details, status="success"):
        """
        Log an action to the audit trail

        Args:
            action_type: Type of action (email_sent, whatsapp_sent, etc.)
            details: Dictionary with action details
            status: success, failed, pending
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "status": status,
            "details": details,
            "actor": "ai_employee"
        }

        # Daily log file
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_actions.json"

        try:
            # Read existing logs
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new log
            logs.append(log_entry)

            # Write back
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to log action: {e}")
            return False

    def get_today_logs(self):
        """Get today's logs"""
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_actions.json"

        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def get_logs_by_date(self, date_str):
        """Get logs for specific date (YYYY-MM-DD)"""
        log_file = self.logs_dir / f"{date_str}_actions.json"

        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def get_stats(self):
        """Get statistics from today's logs"""
        logs = self.get_today_logs()

        stats = {
            "total_actions": len(logs),
            "successful": len([l for l in logs if l["status"] == "success"]),
            "failed": len([l for l in logs if l["status"] == "failed"]),
            "by_type": {}
        }

        # Count by action type
        for log in logs:
            action_type = log["action_type"]
            if action_type not in stats["by_type"]:
                stats["by_type"][action_type] = 0
            stats["by_type"][action_type] += 1

        return stats


# Usage example
if __name__ == "__main__":
    import sys
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"

    logger = AuditLogger(vault_path)

    # Test log
    logger.log_action(
        "system_test",
        {"message": "Audit logging system initialized"},
        "success"
    )

    # Show stats
    stats = logger.get_stats()
    print(f"\n[AUDIT] Today's Statistics:")
    print(f"  Total Actions: {stats['total_actions']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  By Type: {stats['by_type']}")
