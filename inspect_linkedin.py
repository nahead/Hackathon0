#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Page Inspector - Find correct selectors
"""

import os
import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# Set UTF-8 encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

SESSION_FILE = Path(__file__).parent / ".linkedin_session" / "state.json"

print("="*70)
print("LINKEDIN PAGE INSPECTOR")
print("="*70)

with sync_playwright() as p:
    print("\n[STEP 1] Launching browser...")
    browser = p.chromium.launch(headless=False)

    # Load session
    storage_state = None
    if SESSION_FILE.exists():
        with open(SESSION_FILE, 'r') as f:
            storage_state = json.load(f)
        print("[OK] Session loaded")

    context = browser.new_context(storage_state=storage_state)
    page = context.new_page()

    print("\n[STEP 2] Navigating to LinkedIn feed...")
    page.goto("https://www.linkedin.com/feed/", wait_until="networkidle")
    time.sleep(3)

    print("\n[STEP 3] Taking screenshot...")
    page.screenshot(path="linkedin_inspect.png", full_page=True)
    print("[OK] Screenshot saved: linkedin_inspect.png")

    print("\n[STEP 4] Finding 'Start a post' elements...")

    # Get all elements that might be the "Start a post" button
    selectors_to_try = [
        'button:has-text("Start a post")',
        'div:has-text("Start a post")',
        '[aria-label*="Start a post"]',
        'button.share-box-feed-entry__trigger',
        'div.share-box-feed-entry__trigger',
        '.share-box-feed-entry',
        'button[class*="share"]',
        'div[class*="share-box"]',
    ]

    found_elements = []

    for selector in selectors_to_try:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"\n[FOUND] Selector: {selector}")
                print(f"  Count: {len(elements)}")

                for i, elem in enumerate(elements[:3]):  # Show first 3
                    try:
                        # Get element info
                        tag = elem.evaluate("el => el.tagName")
                        classes = elem.evaluate("el => el.className")
                        text = elem.evaluate("el => el.textContent")

                        print(f"  Element {i+1}:")
                        print(f"    Tag: {tag}")
                        print(f"    Classes: {classes[:100]}")
                        print(f"    Text: {text[:50]}")

                        found_elements.append({
                            'selector': selector,
                            'tag': tag,
                            'classes': classes,
                            'text': text
                        })
                    except:
                        pass
        except:
            pass

    # Save findings to file
    print("\n[STEP 5] Saving findings...")
    with open("linkedin_selectors.json", 'w') as f:
        json.dump(found_elements, f, indent=2)
    print("[OK] Findings saved: linkedin_selectors.json")

    # Try to highlight the element
    print("\n[STEP 6] Trying to highlight 'Start a post' button...")

    try:
        # Inject CSS to highlight elements
        page.evaluate("""
            () => {
                const elements = document.querySelectorAll('button, div');
                elements.forEach(el => {
                    const text = el.textContent || '';
                    if (text.includes('Start a post') || text.includes('Start')) {
                        el.style.border = '3px solid red';
                        el.style.backgroundColor = 'yellow';
                    }
                });
            }
        """)

        time.sleep(1)
        page.screenshot(path="linkedin_highlighted.png")
        print("[OK] Highlighted screenshot saved: linkedin_highlighted.png")

    except Exception as e:
        print(f"[ERROR] Could not highlight: {e}")

    print("\n[INFO] Browser will stay open for 30 seconds")
    print("[ACTION] Please look at the page and note the 'Start a post' button")
    time.sleep(30)

    browser.close()

print("\n" + "="*70)
print("INSPECTION COMPLETE")
print("="*70)
print("\nCheck these files:")
print("  1. linkedin_inspect.png - Full page screenshot")
print("  2. linkedin_highlighted.png - Highlighted elements")
print("  3. linkedin_selectors.json - Found selectors")
