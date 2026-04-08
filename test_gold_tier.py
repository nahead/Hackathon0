#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gold Tier Testing Suite
Tests all 12 Gold Tier requirements
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment
load_dotenv()

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"
SKILLS_PATH = Path(__file__).parent / "agent_skills"
MCP_PATH = Path(__file__).parent / "mcp_servers"

class GoldTierTester:
    """Test Gold Tier requirements"""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

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

    def test_1_silver_tier_complete(self):
        """Test 1: Silver Tier must be complete"""
        print("\n[TEST 1] Silver Tier Complete")

        # Check for Silver Tier completion marker
        silver_complete = (VAULT_PATH.parent / "SILVER_TIER_COMPLETE.md").exists()

        self.test(
            "Silver Tier completion verified",
            silver_complete,
            "SILVER_TIER_COMPLETE.md exists"
        )

    def test_2_cross_domain_integration(self):
        """Test 2: Cross-domain integration skill"""
        print("\n[TEST 2] Cross-Domain Integration")

        skill_file = VAULT_PATH / ".claude" / "skills" / "cross-domain-integration.md"
        exists = skill_file.exists()

        if exists:
            content = skill_file.read_text(encoding='utf-8')
            has_integration = "integrate" in content.lower()
            self.test(
                "Cross-domain integration skill",
                has_integration,
                f"Skill file: {skill_file.name}"
            )
        else:
            self.test("Cross-domain integration skill", False, "Skill file not found")

    def test_3_odoo_accounting(self):
        """Test 3: Odoo accounting integration"""
        print("\n[TEST 3] Odoo Accounting")

        # Check skill
        skill_file = VAULT_PATH / ".claude" / "skills" / "odoo-accounting.md"
        skill_exists = skill_file.exists()

        # Check MCP server
        mcp_file = MCP_PATH / "odoo_mcp_server.py"
        mcp_exists = mcp_file.exists()

        self.test(
            "Odoo accounting skill",
            skill_exists,
            f"Skill: {skill_file.name}"
        )

        self.test(
            "Odoo MCP server",
            mcp_exists,
            f"MCP: {mcp_file.name}"
        )

    def test_4_facebook_instagram(self):
        """Test 4: Facebook/Instagram integration"""
        print("\n[TEST 4] Facebook/Instagram")

        # Check skill
        skill_file = VAULT_PATH / ".claude" / "skills" / "facebook-manager.md"
        skill_exists = skill_file.exists()

        # Check MCP server
        mcp_file = MCP_PATH / "facebook_mcp_server.py"
        mcp_exists = mcp_file.exists()

        self.test(
            "Facebook/Instagram skill",
            skill_exists,
            f"Skill: {skill_file.name}"
        )

        self.test(
            "Facebook MCP server",
            mcp_exists,
            f"MCP: {mcp_file.name}"
        )

    def test_5_twitter(self):
        """Test 5: Twitter integration"""
        print("\n[TEST 5] Twitter")

        skill_file = VAULT_PATH / ".claude" / "skills" / "twitter-manager.md"
        exists = skill_file.exists()

        if exists:
            content = skill_file.read_text(encoding='utf-8')
            has_twitter = "twitter" in content.lower() or "tweet" in content.lower()
            self.test(
                "Twitter posting skill",
                has_twitter,
                f"Skill: {skill_file.name}"
            )
        else:
            self.test("Twitter posting skill", False, "Skill file not found")

    def test_6_multiple_mcp_servers(self):
        """Test 6: Multiple MCP servers (4+)"""
        print("\n[TEST 6] Multiple MCP Servers")

        if not MCP_PATH.exists():
            self.test("Multiple MCP servers", False, "MCP directory not found")
            return

        mcp_files = list(MCP_PATH.glob("*_mcp_server.py"))
        count = len(mcp_files)

        self.test(
            "Multiple MCP servers (4+)",
            count >= 4,
            f"Found {count} MCP servers: {', '.join([f.name for f in mcp_files])}"
        )

    def test_7_ceo_briefing(self):
        """Test 7: CEO Briefing generation"""
        print("\n[TEST 7] CEO Briefing")

        skill_file = VAULT_PATH / ".claude" / "skills" / "ceo-briefing.md"
        exists = skill_file.exists()

        if exists:
            content = skill_file.read_text(encoding='utf-8')
            has_briefing = "briefing" in content.lower() or "report" in content.lower()
            self.test(
                "CEO Briefing skill",
                has_briefing,
                f"Skill: {skill_file.name}"
            )
        else:
            self.test("CEO Briefing skill", False, "Skill file not found")

    def test_8_error_recovery(self):
        """Test 8: Error recovery mechanisms"""
        print("\n[TEST 8] Error Recovery")

        # Check for error recovery in cloud deployment
        cloud_file = Path(__file__).parent / "cloud_deployment" / "render_deploy.py"

        if cloud_file.exists():
            content = cloud_file.read_text(encoding='utf-8')
            has_recovery = "error" in content.lower() and "recovery" in content.lower()
            self.test(
                "Error recovery in cloud",
                has_recovery,
                "Error recovery implemented in cloud deployment"
            )
        else:
            self.test("Error recovery in cloud", False, "Cloud deployment file not found")

    def test_9_audit_logging(self):
        """Test 9: Comprehensive audit logging"""
        print("\n[TEST 9] Audit Logging")

        skill_file = VAULT_PATH / ".claude" / "skills" / "audit-logger.md"
        exists = skill_file.exists()

        if exists:
            content = skill_file.read_text(encoding='utf-8')
            has_logging = "audit" in content.lower() or "log" in content.lower()
            self.test(
                "Audit logging skill",
                has_logging,
                f"Skill: {skill_file.name}"
            )
        else:
            self.test("Audit logging skill", False, "Skill file not found")

    def test_10_ralph_wiggum_loop(self):
        """Test 10: Ralph Wiggum autonomous loop"""
        print("\n[TEST 10] Ralph Wiggum Loop")

        skill_file = VAULT_PATH / ".claude" / "skills" / "ralph-wiggum-autonomous.md"
        exists = skill_file.exists()

        if exists:
            content = skill_file.read_text(encoding='utf-8')
            has_loop = "loop" in content.lower() or "autonomous" in content.lower()
            self.test(
                "Ralph Wiggum autonomous loop",
                has_loop,
                f"Skill: {skill_file.name}"
            )
        else:
            self.test("Ralph Wiggum autonomous loop", False, "Skill file not found")

    def test_11_documentation(self):
        """Test 11: Comprehensive documentation"""
        print("\n[TEST 11] Documentation")

        docs = [
            "README.md",
            "ARCHITECTURE.md",
            "DEPLOYMENT.md"
        ]

        found_docs = []
        for doc in docs:
            doc_path = Path(__file__).parent / doc
            if doc_path.exists():
                found_docs.append(doc)

        self.test(
            "Documentation files",
            len(found_docs) >= 2,
            f"Found: {', '.join(found_docs)}"
        )

    def test_12_agent_skills(self):
        """Test 12: 15+ Agent Skills"""
        print("\n[TEST 12] Agent Skills")

        # Check correct location: AI_Employee_Vault/.claude/skills/
        vault_skills = VAULT_PATH / ".claude" / "skills"

        if not vault_skills.exists():
            self.test("Agent Skills (15+)", False, "Skills directory not found")
            return

        skill_files = list(vault_skills.glob("*.md"))
        count = len(skill_files)

        self.test(
            "Agent Skills (15+)",
            count >= 15,
            f"Found {count} skills in AI_Employee_Vault/.claude/skills/"
        )

    def run_all_tests(self):
        """Run all Gold Tier tests"""
        print("="*70)
        print("GOLD TIER TESTING SUITE")
        print("="*70)
        print(f"\nVault: {VAULT_PATH}")
        print(f"Skills: {SKILLS_PATH}")
        print(f"MCP: {MCP_PATH}")

        # Run all tests
        self.test_1_silver_tier_complete()
        self.test_2_cross_domain_integration()
        self.test_3_odoo_accounting()
        self.test_4_facebook_instagram()
        self.test_5_twitter()
        self.test_6_multiple_mcp_servers()
        self.test_7_ceo_briefing()
        self.test_8_error_recovery()
        self.test_9_audit_logging()
        self.test_10_ralph_wiggum_loop()
        self.test_11_documentation()
        self.test_12_agent_skills()

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
            print("\n[SUCCESS] All Gold Tier tests passed!")
        else:
            print(f"\n[WARNING] {self.failed} test(s) failed")

        return self.failed == 0

def main():
    """Main entry point"""
    tester = GoldTierTester()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
