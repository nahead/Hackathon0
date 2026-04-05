#!/usr/bin/env python3
"""
AI Employee Live Monitor
Real-time monitoring of your Platinum Tier AI Employee system
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
import os

class AIEmployeeMonitor:
    """Real-time monitor for AI Employee system"""

    def __init__(self):
        self.railway_url = "https://ai-employee-railway-production.up.railway.app"
        self.vault_path = Path("AI_Employee_Vault_Sync")
        self.last_check = {}

    def check_railway_status(self):
        """Check Railway deployment status"""
        try:
            response = requests.get(f"{self.railway_url}/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def check_vault_changes(self):
        """Monitor vault for new files"""
        changes = []

        vault_dirs = [
            "Cloud_Drafts",
            "Pending_Approval",
            "Approved",
            "Signals/Local",
            "Reports/Cloud",
            "Processed"
        ]

        for dir_name in vault_dirs:
            dir_path = self.vault_path / dir_name
            if dir_path.exists():
                for file_path in dir_path.glob("*.json"):
                    file_key = str(file_path)
                    file_mtime = file_path.stat().st_mtime

                    if file_key not in self.last_check or self.last_check[file_key] < file_mtime:
                        self.last_check[file_key] = file_mtime
                        changes.append({
                            "type": "new_file",
                            "directory": dir_name,
                            "file": file_path.name,
                            "timestamp": datetime.fromtimestamp(file_mtime).isoformat()
                        })

        return changes

    def display_status(self, railway_status, vault_changes):
        """Display current system status"""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=" * 70)
        print(f"[*] AI EMPLOYEE LIVE MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)

        # Railway Status
        print("\n[*] CLOUD STATUS (Railway)")
        print("-" * 30)

        if railway_status.get("status") == "healthy":
            print("[+] System: ONLINE")
            services = railway_status.get("services", {})
            for service, status in services.items():
                print(f"[+] {service.replace('_', ' ').title()}: {status.upper()}")
        else:
            print(f"[!] System: {railway_status.get('status', 'UNKNOWN').upper()}")

        # Vault Activity
        print("\n[*] VAULT ACTIVITY")
        print("-" * 30)

        if vault_changes:
            print(f"[+] {len(vault_changes)} new activities detected:")
            for change in vault_changes[-5:]:  # Show last 5
                timestamp = change['timestamp'][:19].replace('T', ' ')
                print(f"  {timestamp} | {change['directory']} | {change['file']}")
        else:
            print("[*] No new activity")

        # Instructions
        print("\n[*] MONITORING ACTIVE")
        print("-" * 30)
        print("Send a test email to see your AI Employee in action!")
        print("Press Ctrl+C to stop monitoring")

    def run_monitor(self, interval=30):
        """Run continuous monitoring"""
        print("[*] Starting AI Employee Live Monitor...")
        print(f"[*] Monitoring interval: {interval} seconds")
        print("[*] Press Ctrl+C to stop\n")

        try:
            while True:
                # Check Railway status
                railway_status = self.check_railway_status()

                # Check vault changes
                vault_changes = self.check_vault_changes()

                # Display status
                self.display_status(railway_status, vault_changes)

                # Wait for next check
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n[*] Monitoring stopped by user")
            print("[+] AI Employee continues running 24/7 in the cloud!")

def main():
    """Main monitoring function"""
    monitor = AIEmployeeMonitor()

    print("=" * 70)
    print("[*] AI EMPLOYEE PLATINUM TIER MONITOR")
    print("=" * 70)
    print("\nThis monitor shows real-time activity from your AI Employee:")
    print("- Cloud agent status (Railway)")
    print("- Gmail monitoring activity")
    print("- Vault file changes")
    print("- Draft creation and processing")

    input("\nPress Enter to start monitoring...")

    monitor.run_monitor()

if __name__ == "__main__":
    main()