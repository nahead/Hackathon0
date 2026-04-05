#!/usr/bin/env python3
"""
Gmail OAuth2 Token Generator
Run this locally to generate token for Railway deployment
"""

import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def generate_token():
    """Generate OAuth2 token for Gmail API"""

    # Load credentials from credentials.json file
    # Create this file with your Google OAuth credentials
    # Download from: https://console.cloud.google.com/apis/credentials

    if not os.path.exists('credentials.json'):
        print("[!] Error: credentials.json not found")
        print("[*] Please download OAuth credentials from Google Cloud Console")
        print("[*] https://console.cloud.google.com/apis/credentials")
        return

    with open('credentials.json', 'r') as f:
        credentials_info = json.load(f)

    print("[*] Starting Gmail OAuth2 token generation...")

    # Create flow
    flow = InstalledAppFlow.from_client_config(credentials_info, SCOPES)

    # Run local server for OAuth callback
    print("[*] Opening browser for Gmail authorization...")
    print("[*] Please authorize the application in your browser")

    creds = flow.run_local_server(port=0)

    # Convert credentials to JSON
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

    print("\n[+] Token generated successfully!")
    print("[*] Copy this token data to Railway:")
    print("=" * 50)
    print(json.dumps(token_data, indent=2))
    print("=" * 50)

    # Save to file
    with open('gmail_token.json', 'w') as f:
        json.dump(token_data, f, indent=2)

    print(f"\n[*] Token saved to: gmail_token.json")
    print("\n[*] Next steps:")
    print("1. Copy the token JSON above")
    print("2. Add to Railway as GMAIL_TOKEN_JSON variable")
    print("3. Redeploy Railway service")

if __name__ == "__main__":
    try:
        generate_token()
    except Exception as e:
        print(f"[!] Error: {e}")
        print("\n[*] Make sure you have installed:")
        print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")