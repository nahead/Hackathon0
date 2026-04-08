#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Page ID Finder
Uses access token to find your Facebook Page ID
"""

import requests
import json

# Your access token
ACCESS_TOKEN = "EAAM3unuwm80BRAerA8pGw9kvmWapeMRcURR3JDLzyJHz7V3UOu7ZA3wqPvObHpBZAOjLSr0pB15Cu6PxZCWHk9VQ3dkgrQpG1pXAjwKDCBoZBph79ZCJOQxxkEVKgEZA7TlwIfdVav4aXHvv2LcYZC734ZAMZArVs8VRfnzGNZBGDetLaCIbSFa660KhFXgD0XVaO2rTQAGPwYV7BTQLOhmjipJ85qikfV9m2CtZAEY0mLhnmeX6Qyydvs4trpl47tt2HrCXA9X2WZBvtlx4PU7kFdukvKOo2gZDZD"

print("="*70)
print("FACEBOOK PAGE ID FINDER")
print("="*70)

# Get pages managed by this token
print("\n[STEP 1] Fetching your Facebook pages...")
url = "https://graph.facebook.com/v18.0/me/accounts"
params = {'access_token': ACCESS_TOKEN}

try:
    response = requests.get(url, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        pages = data.get('data', [])

        if pages:
            print(f"[OK] Found {len(pages)} page(s):\n")

            for i, page in enumerate(pages, 1):
                print(f"Page {i}:")
                print(f"  Name: {page.get('name')}")
                print(f"  Page ID: {page.get('id')}")
                print(f"  Category: {page.get('category', 'N/A')}")
                print(f"  Access Token: {page.get('access_token', 'N/A')[:50]}...")
                print()

            # Show .env format
            print("="*70)
            print("ADD TO YOUR .ENV FILE:")
            print("="*70)
            first_page = pages[0]
            print(f"\nFACEBOOK_PAGE_ID={first_page.get('id')}")
            print(f"FACEBOOK_PAGE_ACCESS_TOKEN={first_page.get('access_token')}")
            print()

        else:
            print("[ERROR] No pages found for this token")
            print("[INFO] Make sure you have admin access to a Facebook page")
    else:
        print(f"[ERROR] API request failed: {response.status_code}")
        print(f"[ERROR] Response: {response.text}")

except Exception as e:
    print(f"[ERROR] Exception: {e}")

print("="*70)
