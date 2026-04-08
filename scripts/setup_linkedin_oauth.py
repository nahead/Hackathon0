#!/usr/bin/env python3
"""
LinkedIn OAuth Setup Helper
Complete guide to get LinkedIn access token and person URN
"""

import os
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn OAuth configuration
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '777mj195y7yyos')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')  # Load from .env file
REDIRECT_URI = 'http://localhost:8080/callback'
SCOPES = 'openid profile email w_member_social'

if not CLIENT_SECRET:
    print("[ERROR] LINKEDIN_CLIENT_SECRET not found in .env file")
    print("[INFO] Please add it to your .env file")
    exit(1)

# Global variable to store authorization code
auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from LinkedIn"""

    def do_GET(self):
        global auth_code

        # Parse the callback URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if 'code' in query_params:
            auth_code = query_params['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            success_html = """
            <html>
            <head><title>LinkedIn OAuth Success</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: green;">✓ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            error_html = """
            <html>
            <head><title>LinkedIn OAuth Error</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: red;">✗ Authorization Failed</h1>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())

    def log_message(self, format, *args):
        # Suppress server logs
        pass

def step1_authorize():
    """Step 1: Get authorization code"""
    print("\n" + "="*70)
    print("STEP 1: AUTHORIZE APPLICATION")
    print("="*70)

    # Build authorization URL
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
    )

    print("\n[INFO] Starting local server on http://localhost:8080")
    print("[INFO] Opening LinkedIn authorization page in browser...")
    print("\n[ACTION] Please:")
    print("  1. Login to LinkedIn if not already logged in")
    print("  2. Click 'Allow' to authorize the application")
    print("  3. Wait for redirect (this window will show success)")

    # Open browser
    webbrowser.open(auth_url)

    # Start local server to receive callback
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)

    print("\n[WAIT] Waiting for authorization...")

    # Handle one request (the callback)
    server.handle_request()

    if auth_code:
        print("\n[OK] Authorization code received!")
        return auth_code
    else:
        print("\n[ERROR] Failed to get authorization code")
        return None

def step2_get_access_token(code):
    """Step 2: Exchange authorization code for access token"""
    print("\n" + "="*70)
    print("STEP 2: GET ACCESS TOKEN")
    print("="*70)

    print("\n[INFO] Exchanging authorization code for access token...")

    token_url = "https://www.linkedin.com/oauth/v2/accessToken"

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    try:
        response = requests.post(token_url, data=data, timeout=10)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 0)

            print(f"\n[OK] Access token received!")
            print(f"[INFO] Token expires in: {expires_in} seconds (~{expires_in//86400} days)")

            return access_token
        else:
            print(f"\n[ERROR] Failed to get access token")
            print(f"[ERROR] Status: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return None

def step3_get_person_urn(access_token):
    """Step 3: Get person URN"""
    print("\n" + "="*70)
    print("STEP 3: GET PERSON URN")
    print("="*70)

    print("\n[INFO] Fetching user profile...")

    profile_url = "https://api.linkedin.com/v2/userinfo"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(profile_url, headers=headers, timeout=10)

        if response.status_code == 200:
            profile_data = response.json()
            person_id = profile_data.get('sub')
            name = profile_data.get('name', 'Unknown')
            email = profile_data.get('email', 'Unknown')

            print(f"\n[OK] Profile retrieved!")
            print(f"[INFO] Name: {name}")
            print(f"[INFO] Email: {email}")
            print(f"[INFO] Person ID: {person_id}")

            # Create person URN
            person_urn = f"urn:li:person:{person_id}"

            return person_urn
        else:
            print(f"\n[ERROR] Failed to get profile")
            print(f"[ERROR] Status: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return None

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        return None

def step4_save_credentials(access_token, person_urn):
    """Step 4: Save credentials"""
    print("\n" + "="*70)
    print("STEP 4: SAVE CREDENTIALS")
    print("="*70)

    print("\n[INFO] Your LinkedIn credentials:")
    print("\n" + "-"*70)
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_PERSON_URN={person_urn}")
    print("-"*70)

    print("\n[ACTION] To use locally:")
    print("  1. Copy the values above")
    print("  2. Update your .env file")
    print("  3. Run: python test_linkedin_poster.py")

    print("\n[ACTION] To use on Render.com (cloud):")
    print("  1. Go to: https://dashboard.render.com")
    print("  2. Select your service: ai-employee-cloud")
    print("  3. Go to: Environment tab")
    print("  4. Add these variables:")
    print(f"     LINKEDIN_ACCESS_TOKEN = {access_token}")
    print(f"     LINKEDIN_PERSON_URN = {person_urn}")
    print("  5. Click 'Save Changes'")
    print("  6. Service will auto-redeploy")

    print("\n[INFO] After setup, approved LinkedIn posts will be posted automatically!")

def main():
    """Main setup flow"""
    print("="*70)
    print("LINKEDIN OAUTH SETUP - COMPLETE GUIDE")
    print("="*70)

    print("\n[INFO] This script will help you get:")
    print("  1. LinkedIn Access Token")
    print("  2. LinkedIn Person URN")
    print("\n[INFO] You will need:")
    print("  - LinkedIn account")
    print("  - Browser access")
    print("  - Internet connection")

    input("\n[PRESS ENTER TO START]")

    # Step 1: Get authorization code
    code = step1_authorize()
    if not code:
        print("\n[ERROR] Setup failed at Step 1")
        return

    # Step 2: Get access token
    access_token = step2_get_access_token(code)
    if not access_token:
        print("\n[ERROR] Setup failed at Step 2")
        return

    # Step 3: Get person URN
    person_urn = step3_get_person_urn(access_token)
    if not person_urn:
        print("\n[ERROR] Setup failed at Step 3")
        return

    # Step 4: Save credentials
    step4_save_credentials(access_token, person_urn)

    print("\n" + "="*70)
    print("[OK] SETUP COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    main()
