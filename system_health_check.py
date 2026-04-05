#!/usr/bin/env python3
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
