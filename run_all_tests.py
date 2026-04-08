#!/usr/bin/env python3
"""
Master Test Runner - Run All Local Tests
Tests the complete workflow: Email Detection → Email Sending → LinkedIn Content → LinkedIn Posting
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def check_environment():
    """Check if required environment variables are set"""
    print_header("CHECKING ENVIRONMENT")

    required = {
        'SMTP_USER': 'Gmail address',
        'SMTP_PASS': 'Gmail app password',
    }

    optional = {
        'RESEND_API_KEY': 'Resend API key (for email sending)',
        'LINKEDIN_ACCESS_TOKEN': 'LinkedIn API token (for posting)',
        'LINKEDIN_PERSON_URN': 'LinkedIn person URN (for posting)',
    }

    print("Required Variables:")
    all_set = True
    for var, desc in required.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {desc}")
        else:
            print(f"  ❌ {var}: {desc} - NOT SET")
            all_set = False

    print("\nOptional Variables:")
    for var, desc in optional.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {desc}")
        else:
            print(f"  ⚠️  {var}: {desc} - NOT SET (optional)")

    if not all_set:
        print("\n❌ Missing required environment variables!")
        print("\nSet them with:")
        print("  export SMTP_USER='your-email@gmail.com'")
        print("  export SMTP_PASS='your-app-password'")
        print("\nFor Gmail App Password:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Generate new app password")
        print("  3. Use that password (not your regular Gmail password)")
        return False

    return True

def run_test(script_name, description):
    """Run a test script"""
    print_header(description)

    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        print(f"❌ Test script not found: {script_name}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False

def show_summary(results):
    """Show test summary"""
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {test_name}")

    print(f"\nTotal: {total} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False

def main():
    """Main test runner"""
    print("=" * 70)
    print("  AI EMPLOYEE - LOCAL TEST SUITE")
    print("=" * 70)

    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please set required variables.")
        return 1

    # Run tests
    results = {}

    print("\n" + "=" * 70)
    print("  STARTING TESTS")
    print("=" * 70)

    # Test 1: Email Detection
    results['Email Detection'] = run_test(
        'test_email_detection.py',
        'TEST 1: EMAIL DETECTION'
    )

    # Test 2: Email Sending
    results['Email Sending'] = run_test(
        'test_email_sender.py',
        'TEST 2: EMAIL SENDING'
    )

    # Test 3: LinkedIn Content Creation
    results['LinkedIn Content'] = run_test(
        'test_linkedin_content.py',
        'TEST 3: LINKEDIN CONTENT CREATION'
    )

    # Test 4: LinkedIn Posting (dry run)
    print("\nℹ️  Setting DRY_RUN=true for LinkedIn posting test")
    os.environ['DRY_RUN'] = 'true'
    results['LinkedIn Posting'] = run_test(
        'test_linkedin_poster.py',
        'TEST 4: LINKEDIN POSTING (DRY RUN)'
    )

    # Show summary
    all_passed = show_summary(results)

    # Show next steps
    print_header("NEXT STEPS")
    print("""
1. Review the test results above
2. Check AI_Employee_Vault/Pending_Approval/ for generated content
3. To approve content:
   - Move files from Pending_Approval/ to Approved/
4. To post to LinkedIn for real:
   - Set LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN
   - Run: DRY_RUN=false python test_linkedin_poster.py

For cloud deployment:
   - The system is already running at: https://ai-employee-cloud.onrender.com
   - Check live logs at: https://ai-employee-cloud.onrender.com
""")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
