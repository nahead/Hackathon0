#!/usr/bin/env python3
"""
Email Detection Demo - Fixed Version
Loads .env file before running watcher
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables FIRST
load_dotenv()

print("="*60)
print("EMAIL DETECTION DEMO")
print("="*60)

# Verify credentials are loaded
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')

print(f"\nEmail: {smtp_user}")
print(f"Password: {'*' * len(smtp_pass) if smtp_pass else 'NOT LOADED'}")

if not smtp_pass:
    print("\n[ERROR] .env file not loaded properly")
    print("Please check .env file exists in current directory")
    sys.exit(1)

print("\n" + "="*60)
print("Starting email detection...")
print("This will check for unread emails and create approval files")
print("="*60)

input("\nPress Enter to start...")

try:
    from simple_gmail_watcher import SimpleGmailWatcher

    watcher = SimpleGmailWatcher('AI_Employee_Vault')

    # Connect
    print("\n[1/3] Connecting to Gmail...")
    mail = watcher.connect_to_gmail()
    if not mail:
        print("[ERROR] Failed to connect")
        sys.exit(1)

    # Check emails
    print("[2/3] Checking for unread emails...")
    watcher.check_new_emails(mail)

    # Close
    print("[3/3] Closing connection...")
    mail.close()
    mail.logout()

    print("\n" + "="*60)
    print("DETECTION COMPLETE!")
    print("="*60)

    # Check results
    needs_action = Path('AI_Employee_Vault/Needs_Action')
    files = list(needs_action.glob('EMAIL_*.md'))

    if files:
        print(f"\n[SUCCESS] Found {len(files)} email approval file(s)")
        print("\nMost recent files:")
        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"  - {f.name}")

        print(f"\n[INFO] Check folder: AI_Employee_Vault/Needs_Action/")
        print("[INFO] Review files to see suggested responses")
    else:
        print("\n[INFO] No new unread emails detected")
        print("(All emails may already be read or processed)")

    print("\n" + "="*60)
    print("What you can do now:")
    print("="*60)
    print("1. Review approval files:")
    print("   ls AI_Employee_Vault/Needs_Action/")
    print("\n2. Read a specific file:")
    print("   cat AI_Employee_Vault/Needs_Action/EMAIL_TEST_*.md")
    print("\n3. For continuous monitoring (Ctrl+C to stop):")
    print("   python simple_gmail_watcher.py")
    print("\n4. Deploy to Railway for 24/7 operation:")
    print("   See RAILWAY_SIMPLE_GUIDE.md")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n[CANCELLED] Stopped by user")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
