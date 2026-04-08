#!/usr/bin/env python3
"""Quick test to check if browser opens"""

from playwright.sync_api import sync_playwright

print("[TEST] Trying to launch browser...")

try:
    with sync_playwright() as p:
        print("[STEP 1] Launching Chromium...")
        browser = p.chromium.launch(headless=False)

        print("[STEP 2] Creating new page...")
        page = browser.new_page()

        print("[STEP 3] Navigating to example.com...")
        page.goto("https://example.com")

        print("[STEP 4] Getting page title...")
        title = page.title()
        print(f"[OK] Page title: {title}")

        print("[STEP 5] Taking screenshot...")
        page.screenshot(path="test_browser.png")
        print("[OK] Screenshot saved: test_browser.png")

        import time
        print("[WAIT] Browser will stay open for 5 seconds...")
        time.sleep(5)

        print("[STEP 6] Closing browser...")
        browser.close()

        print("\n[SUCCESS] Browser test passed!")

except Exception as e:
    print(f"\n[ERROR] Browser test failed: {e}")
    import traceback
    traceback.print_exc()
