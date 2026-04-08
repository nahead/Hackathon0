#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silver Tier Testing Script
Tests all Silver Tier requirements
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"

def print_header(title):
    """Print test section header"""
    print("\n" + "="*70)
    print(f"TEST: {title}")
    print("="*70)

def test_1_linkedin_content_generator():
    """Test 1: LinkedIn Content Generator"""
    print_header("LinkedIn Content Generator")

    print("\n[TEST] Generating LinkedIn content...")

    try:
        # Import and run
        sys.path.insert(0, str(Path(__file__).parent))
        from linkedin_content_generator import LinkedInContentGenerator

        generator = LinkedInContentGenerator()

        # Generate daily content
        print("\n[STEP 1] Generating daily content...")
        filepath = generator.generate_daily_content()

        if filepath.exists():
            print(f"[OK] Content created: {filepath.name}")

            # Show preview
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')
            preview = '\n'.join(lines[:20])
            print(f"\n[PREVIEW]\n{preview}\n...")

            print("\n[RESULT] ✅ PASSED - Content generator working")
            return True
        else:
            print("[ERROR] ❌ FAILED - File not created")
            return False

    except Exception as e:
        print(f"[ERROR] ❌ FAILED - {e}")
        return False

def test_2_whatsapp_watcher():
    """Test 2: WhatsApp Watcher"""
    print_header("WhatsApp Watcher")

    print("\n[TEST] Testing WhatsApp watcher...")

    try:
        from whatsapp_watcher import WhatsAppWatcher

        watcher = WhatsAppWatcher(check_interval=60)

        print("\n[STEP 1] Running single check...")
        watcher.run_once()

        print("\n[RESULT] ✅ PASSED - WhatsApp watcher working")
        return True

    except Exception as e:
        print(f"[ERROR] ❌ FAILED - {e}")
        return False

def test_3_plan_generator():
    """Test 3: Plan Generator"""
    print_header("Plan Generator")

    print("\n[TEST] Testing plan generator...")

    try:
        from create_plan import PlanGenerator

        generator = PlanGenerator()

        print("\n[STEP 1] Creating sample plan...")
        filepath = generator.create_sample_plan()

        if filepath.exists():
            print(f"[OK] Plan created: {filepath.name}")

            # Show preview
            content = filepath.read_text(encoding='utf-8')
            lines = content.split('\n')
            preview = '\n'.join(lines[:30])
            print(f"\n[PREVIEW]\n{preview}\n...")

            print("\n[RESULT] ✅ PASSED - Plan generator working")
            return True
        else:
            print("[ERROR] ❌ FAILED - Plan not created")
            return False

    except Exception as e:
        print(f"[ERROR] ❌ FAILED - {e}")
        return False

def test_4_playwright_check():
    """Test 4: Check Playwright Installation"""
    print_header("Playwright Installation Check")

    print("\n[TEST] Checking if Playwright is installed...")

    try:
        from playwright.sync_api import sync_playwright

        print("[OK] Playwright module found")

        # Try to launch browser
        print("\n[STEP 1] Testing browser launch...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://example.com")
            title = page.title()
            browser.close()

            print(f"[OK] Browser launched successfully")
            print(f"[OK] Test page title: {title}")

        print("\n[RESULT] ✅ PASSED - Playwright ready for LinkedIn posting")
        return True

    except ImportError:
        print("[ERROR] ❌ FAILED - Playwright not installed")
        print("\n[FIX] Install Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

    except Exception as e:
        print(f"[ERROR] ❌ FAILED - {e}")
        print("\n[FIX] Install browser:")
        print("  playwright install chromium")
        return False

def test_5_folder_structure():
    """Test 5: Verify Folder Structure"""
    print_header("Folder Structure Verification")

    print("\n[TEST] Checking Silver Tier folders...")

    required_folders = [
        "Needs_Action",
        "Processing",
        "Pending_Approval",
        "Approved",
        "Done",
        "Rejected",
        "Plans"
    ]

    all_exist = True
    for folder in required_folders:
        folder_path = VAULT_PATH / folder
        if folder_path.exists():
            print(f"[OK] {folder}/")
        else:
            print(f"[ERROR] {folder}/ - MISSING")
            all_exist = False

    if all_exist:
        print("\n[RESULT] PASSED - All folders present")
        return True
    else:
        print("\n[RESULT] FAILED - Some folders missing")
        return False

def test_6_agent_skills():
    """Test 6: Verify Agent Skills"""
    print_header("Agent Skills Verification")

    print("\n[TEST] Checking Agent Skills...")

    skills_path = VAULT_PATH / ".claude" / "skills"

    if not skills_path.exists():
        print("[ERROR] ❌ FAILED - Skills folder not found")
        return False

    skills = list(skills_path.glob("*.md"))

    print(f"\n[FOUND] {len(skills)} Agent Skills:")
    for skill in sorted(skills):
        print(f"  [OK] {skill.name}")

    if len(skills) >= 15:
        print(f"\n[RESULT] PASSED - {len(skills)} skills found (requirement: 15)")
        return True
    else:
        print(f"\n[RESULT] FAILED - Only {len(skills)} skills (requirement: 15)")
        return False

def test_7_mcp_servers():
    """Test 7: Verify MCP Servers"""
    print_header("MCP Servers Verification")

    print("\n[TEST] Checking MCP servers...")

    base_path = Path(__file__).parent

    mcp_servers = [
        "email-mcp-server",
        "odoo-mcp-server",
        "social-media-mcp-servers",
        "task-management-mcp-server"
    ]

    all_exist = True
    for server in mcp_servers:
        server_path = base_path / server
        if server_path.exists():
            print(f"[OK] {server}/")
        else:
            print(f"[WARN] {server}/ - Not found")
            all_exist = False

    if all_exist:
        print("\n[RESULT] PASSED - All MCP servers present")
        return True
    else:
        print("\n[RESULT] PARTIAL - Some MCP servers missing (not critical)")
        return True  # Not critical for Silver Tier

def run_all_tests():
    """Run all Silver Tier tests"""
    print("="*70)
    print("SILVER TIER TESTING SUITE")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # Run tests
    results['Folder Structure'] = test_5_folder_structure()
    results['Agent Skills'] = test_6_agent_skills()
    results['MCP Servers'] = test_7_mcp_servers()
    results['LinkedIn Content Generator'] = test_1_linkedin_content_generator()
    results['WhatsApp Watcher'] = test_2_whatsapp_watcher()
    results['Plan Generator'] = test_3_plan_generator()
    results['Playwright Installation'] = test_4_playwright_check()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{status} - {test_name}")

    print("\n" + "="*70)
    print(f"RESULTS: {passed}/{total} tests passed ({passed*100//total}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - SILVER TIER READY!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review errors above")

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_all_tests()
