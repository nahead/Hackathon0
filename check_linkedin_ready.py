#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LinkedIn Posting - Dry Run
Shows what will happen without actually posting
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()

print("="*70)
print("LINKEDIN POSTING - PRE-FLIGHT CHECK")
print("="*70)

# Check credentials
email = os.getenv('LINKEDIN_EMAIL', '')
password = os.getenv('LINKEDIN_PASSWORD', '')

print("\n[CHECK 1] Credentials")
if email and email != 'your_linkedin_email@gmail.com':
    print(f"  ✅ Email: {email}")
else:
    print(f"  ❌ Email: Not configured")

if password and password != 'your_linkedin_password':
    print(f"  ✅ Password: {'*' * len(password)}")
else:
    print(f"  ❌ Password: Not configured")

# Check approved posts
vault_path = Path(__file__).parent / "AI_Employee_Vault"
approved_folder = vault_path / "Approved"

print("\n[CHECK 2] Approved Posts")
linkedin_posts = list(approved_folder.glob("LINKEDIN_POST_*.md"))

if linkedin_posts:
    print(f"  ✅ Found {len(linkedin_posts)} approved post(s)")
    for post in linkedin_posts:
        print(f"     - {post.name}")
else:
    print(f"  ❌ No approved posts found")

# Check browser
print("\n[CHECK 3] Browser")
try:
    from playwright.sync_api import sync_playwright
    print(f"  ✅ Playwright installed")
except:
    print(f"  ❌ Playwright not installed")

# Summary
print("\n" + "="*70)
print("READY TO POST?")
print("="*70)

if email and password and linkedin_posts and email != 'your_linkedin_email@gmail.com':
    print("\n✅ ALL CHECKS PASSED - Ready to post!")
    print("\nRun this command to post:")
    print("  python linkedin_playwright_poster.py")
    print("\nOr with visible browser:")
    print("  set HEADLESS=false")
    print("  python linkedin_playwright_poster.py")
else:
    print("\n❌ NOT READY - Fix the issues above first")

    if not email or email == 'your_linkedin_email@gmail.com':
        print("\n[TODO] Add LinkedIn email to .env file")

    if not password or password == 'your_linkedin_password':
        print("[TODO] Add LinkedIn password to .env file")

    if not linkedin_posts:
        print("[TODO] Generate and approve a LinkedIn post")
        print("       Run: python linkedin_content_generator.py daily")
        print("       Then move to Approved/ folder")

print("\n" + "="*70)
