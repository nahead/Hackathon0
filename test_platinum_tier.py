#!/usr/bin/env python3
"""
Platinum Tier Testing Suite
Tests all Platinum Tier requirements
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

load_dotenv()

class PlatinumTierTester:
    """Test Platinum Tier requirements"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.project_root = Path(__file__).parent

    def test(self, name, condition, details=""):
        """Record test result"""
        status = "PASS" if condition else "FAIL"
        self.results.append({
            'name': name,
            'status': status,
            'details': details
        })

        if condition:
            self.passed += 1
            print(f"[{status}] {name}")
        else:
            self.failed += 1
            print(f"[{status}] {name}")

        if details:
            print(f"       {details}")

    def test_1_gold_tier_complete(self):
        """Test 1: Gold Tier must be complete"""
        print("\n[TEST 1] Gold Tier Complete")

        gold_complete = (self.project_root / "GOLD_TIER_COMPLETE.md").exists()
        self.test(
            "Gold Tier completion verified",
            gold_complete,
            "GOLD_TIER_COMPLETE.md exists"
        )

    def test_2_cloud_deployment_script(self):
        """Test 2: Cloud deployment script exists"""
        print("\n[TEST 2] Cloud Deployment Script")

        deploy_script = self.project_root / "cloud_deployment" / "render_deploy.py"
        exists = deploy_script.exists()

        if exists:
            content = deploy_script.read_text(encoding='utf-8')
            has_health = "health" in content.lower()
            has_recovery = "recovery" in content.lower()

            self.test(
                "Cloud deployment script with health monitoring",
                has_health and has_recovery,
                f"Script: {deploy_script.name}"
            )
        else:
            self.test("Cloud deployment script", False, "Script not found")

    def test_3_orchestrator(self):
        """Test 3: Orchestrator for 24/7 operation"""
        print("\n[TEST 3] Orchestrator")

        orchestrator = self.project_root / "orchestrator.py"
        exists = orchestrator.exists()

        self.test(
            "Orchestrator script",
            exists,
            f"Orchestrator: {'Found' if exists else 'Not found'}"
        )

    def test_4_vault_sync_config(self):
        """Test 4: Vault sync configuration"""
        print("\n[TEST 4] Vault Sync Configuration")

        gitignore = self.project_root / ".gitignore"

        if gitignore.exists():
            content = gitignore.read_text(encoding='utf-8')
            has_env = ".env" in content
            has_secrets = "credentials" in content.lower() or "secrets" in content.lower()

            self.test(
                "Vault sync security (.gitignore)",
                has_env,
                "Secrets excluded from sync"
            )
        else:
            self.test("Vault sync security", False, ".gitignore not found")

    def test_5_work_zone_separation(self):
        """Test 5: Work-zone separation (Cloud vs Local)"""
        print("\n[TEST 5] Work-Zone Separation")

        vault = self.project_root / "AI_Employee_Vault"

        folders = [
            "Needs_Action",
            "Pending_Approval",
            "Approved",
            "In_Progress",
            "Done"
        ]

        all_exist = all((vault / folder).exists() for folder in folders)

        self.test(
            "Work-zone folder structure",
            all_exist,
            f"Folders: {', '.join(folders)}"
        )

    def test_6_health_monitoring(self):
        """Test 6: Health monitoring system"""
        print("\n[TEST 6] Health Monitoring")

        deploy_script = self.project_root / "cloud_deployment" / "render_deploy.py"

        if deploy_script.exists():
            content = deploy_script.read_text(encoding='utf-8')
            has_health_check = "health_check" in content

            self.test(
                "Health monitoring implemented",
                has_health_check,
                "Health check method found"
            )
        else:
            self.test("Health monitoring", False, "Deployment script not found")

    def test_7_deployment_docs(self):
        """Test 7: Deployment documentation"""
        print("\n[TEST 7] Deployment Documentation")

        deployment_md = self.project_root / "DEPLOYMENT.md"
        exists = deployment_md.exists()

        if exists:
            content = deployment_md.read_text(encoding='utf-8')
            has_render = "render" in content.lower()
            has_cloud = "cloud" in content.lower()

            self.test(
                "Deployment documentation",
                has_render or has_cloud,
                "DEPLOYMENT.md with cloud instructions"
            )
        else:
            self.test("Deployment documentation", False, "DEPLOYMENT.md not found")

    def run_all_tests(self):
        """Run all Platinum Tier tests"""
        print("="*70)
        print("PLATINUM TIER TESTING SUITE")
        print("="*70)
        print(f"\nProject: {self.project_root}")

        self.test_1_gold_tier_complete()
        self.test_2_cloud_deployment_script()
        self.test_3_orchestrator()
        self.test_4_vault_sync_config()
        self.test_5_work_zone_separation()
        self.test_6_health_monitoring()
        self.test_7_deployment_docs()

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"PASSED: {self.passed}")
        print(f"FAILED: {self.failed}")
        print(f"TOTAL:  {self.passed + self.failed}")

        percentage = (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0
        print(f"\nSUCCESS RATE: {percentage:.1f}%")

        if self.failed == 0:
            print("\n[SUCCESS] All Platinum Tier tests passed!")
        else:
            print(f"\n[WARNING] {self.failed} test(s) failed")

        return self.failed == 0

def main():
    """Main entry point"""
    tester = PlatinumTierTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
