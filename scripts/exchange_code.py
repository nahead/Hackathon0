#!/usr/bin/env python3
"""
LinkedIn OAuth - Exchange Code for Token
Quick script to exchange authorization code for access token
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python exchange_code.py YOUR_AUTHORIZATION_CODE")
    print("\nExample:")
    print("  python exchange_code.py AQTxxx...xxx")
    sys.exit(1)

auth_code = sys.argv[1]

print("="*70)
print("EXCHANGING CODE FOR ACCESS TOKEN")
print("="*70)

# Get credentials from environment
LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:8080/callback')

if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
    print("[ERROR] LinkedIn credentials not found in .env file")
    print("[INFO] Please add LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET to .env")
    sys.exit(1)

# Exchange code for token
token_url = "https://www.linkedin.com/oauth/v2/accessToken"

data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': LINKEDIN_REDIRECT_URI,
    'client_id': LINKEDIN_CLIENT_ID,
    'client_secret': LINKEDIN_CLIENT_SECRET
}

print("\n[STEP 1] Exchanging authorization code...")
response = requests.post(token_url, data=data)

if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get('access_token')
    expires_in = token_data.get('expires_in', 0)

    print(f"[OK] Access token received!")
    print(f"[INFO] Expires in: {expires_in} seconds (~{expires_in//86400} days)")

    # Get person URN
    print("\n[STEP 2] Getting person URN...")
    userinfo_url = "https://api.linkedin.com/v2/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}

    user_response = requests.get(userinfo_url, headers=headers)

    if user_response.status_code == 200:
        user_data = user_response.json()
        person_id = user_data.get('sub')
        name = user_data.get('name', 'Unknown')
        email = user_data.get('email', 'Unknown')

        person_urn = f"urn:li:person:{person_id}"

        print(f"[OK] User info retrieved!")
        print(f"[INFO] Name: {name}")
        print(f"[INFO] Email: {email}")

        # Show credentials
        print("\n" + "="*70)
        print("YOUR LINKEDIN CREDENTIALS")
        print("="*70)
        print(f"\nLINKEDIN_ACCESS_TOKEN={access_token}")
        print(f"LINKEDIN_PERSON_URN={person_urn}")

        print("\n" + "="*70)
        print("NEXT STEP: Add these to your .env file")
        print("="*70)

    else:
        print(f"[ERROR] Could not get user info: {user_response.status_code}")
        print(f"[ERROR] Response: {user_response.text}")

else:
    print(f"[ERROR] Token exchange failed: {response.status_code}")
    print(f"[ERROR] Response: {response.text}")
