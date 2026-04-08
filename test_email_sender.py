#!/usr/bin/env python3
"""
Test Email Sending - Resend API
Tests if email sending is working via Resend API
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_resend_api():
    """Test email sending via Resend API"""
    print("[TEST] Testing Resend API Email Sending...")

    # Get API key from environment
    resend_api_key = os.getenv('RESEND_API_KEY')

    if not resend_api_key:
        print("[ERROR] ERROR: RESEND_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export RESEND_API_KEY='re_your_api_key'")
        print("\nGet your API key from: https://resend.com/api-keys")
        return False

    try:
        # Prepare email
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }

        # Test email data
        data = {
            "from": "AI Employee <onboarding@resend.dev>",
            "to": [os.getenv('SMTP_USER', 'test@example.com')],
            "subject": f"Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "text": """This is a test email from your AI Employee system.

If you received this email, the email sending functionality is working correctly!

Timestamp: """ + datetime.now().isoformat()
        }

        print(f"\n[SEND] Sending test email to: {data['to'][0]}")
        print(f"   Subject: {data['subject']}")

        # Send email
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"\n[OK] Email sent successfully!")
            print(f"   Email ID: {result.get('id', 'N/A')}")
            print(f"\n[INBOX] Check your inbox: {data['to'][0]}")
            return True
        else:
            print(f"\n[ERROR] ERROR: Failed to send email")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

def test_smtp_fallback():
    """Test SMTP email sending (fallback method)"""
    print("\n[TEST] Testing SMTP Email Sending (Fallback)...")

    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("[WARN] SMTP credentials not set, skipping SMTP test")
        return None

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        msg['Subject'] = f"SMTP Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = f"""This is a test email via SMTP.

Timestamp: {datetime.now().isoformat()}
"""
        msg.attach(MIMEText(body, 'plain'))

        print(f"\n[SEND] Sending SMTP test email to: {smtp_user}")

        # Try SSL first (port 465)
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print("[OK] SMTP email sent successfully (SSL port 465)")
            return True
        except Exception as e:
            print(f"[WARN] SSL failed: {e}")

            # Try TLS (port 587)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                print("[OK] SMTP email sent successfully (TLS port 587)")
                return True
            except Exception as e2:
                print(f"[ERROR] TLS also failed: {e2}")
                return False

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL SENDING TEST")
    print("=" * 60)

    # Test Resend API (recommended)
    resend_success = test_resend_api()

    # Test SMTP (fallback)
    smtp_success = test_smtp_fallback()

    print("\n" + "=" * 60)
    if resend_success or smtp_success:
        print("[OK] EMAIL SENDING WORKING")
        if resend_success:
            print("   Method: Resend API (recommended)")
        elif smtp_success:
            print("   Method: SMTP (fallback)")
    else:
        print("[ERROR] EMAIL SENDING FAILED")
        print("\nTroubleshooting:")
        print("1. Set RESEND_API_KEY for Resend API")
        print("2. Or set SMTP_USER and SMTP_PASS for Gmail")
        print("3. For Gmail, use App Password (not regular password)")
    print("=" * 60)
