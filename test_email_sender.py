#!/usr/bin/env python3
"""
Test Email Sending - SMTP (Gmail)
Tests if email sending is working via SMTP
"""

import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_smtp_email_sending():
    """Test SMTP email sending via Gmail"""
    print("[TEST] Testing SMTP Email Sending (Gmail)...")

    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not smtp_user or not smtp_pass:
        print("[ERROR] ERROR: SMTP_USER and SMTP_PASS environment variables not set")
        print("\nSet them in .env file:")
        print("  SMTP_USER=your-email@gmail.com")
        print("  SMTP_PASS=your-app-password")
        print("\nFor Gmail App Password:")
        print("  1. Go to: https://myaccount.google.com/apppasswords")
        print("  2. Generate new app password")
        print("  3. Use that password (not your regular Gmail password)")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = smtp_user
        msg['Subject'] = f"AI Employee Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = f"""This is a test email from your AI Employee system.

Email sending via SMTP is working correctly!

Timestamp: {datetime.now().isoformat()}

System: AI Employee - Platinum Tier
Method: SMTP (Gmail)
Status: Operational
"""
        msg.attach(MIMEText(body, 'plain'))

        print(f"\n[SEND] Sending test email to: {smtp_user}")
        print(f"   Subject: {msg['Subject']}")

        # Try SSL first (port 465) - most reliable
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print("\n[OK] Email sent successfully via SMTP (SSL port 465)")
            print(f"[INBOX] Check your inbox: {smtp_user}")
            return True
        except Exception as e:
            print(f"[WARN] SSL port 465 failed: {e}")

            # Try TLS (port 587) as fallback
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                server.quit()
                print("\n[OK] Email sent successfully via SMTP (TLS port 587)")
                print(f"[INBOX] Check your inbox: {smtp_user}")
                return True
            except Exception as e2:
                print(f"\n[ERROR] TLS port 587 also failed: {e2}")
                print("\nTroubleshooting:")
                print("1. Make sure you're using Gmail App Password (not regular password)")
                print("2. Check if 2-factor authentication is enabled")
                print("3. Verify SMTP_USER and SMTP_PASS are correct in .env file")
                return False

    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EMAIL SENDING TEST - SMTP")
    print("=" * 60)

    # Test SMTP email sending
    success = test_smtp_email_sending()

    print("\n" + "=" * 60)
    if success:
        print("[OK] EMAIL SENDING WORKING")
        print("   Method: SMTP (Gmail)")
        print("   Status: Production Ready")
    else:
        print("[ERROR] EMAIL SENDING FAILED")
        print("\nPlease check:")
        print("1. SMTP_USER and SMTP_PASS in .env file")
        print("2. Using Gmail App Password (not regular password)")
        print("3. Internet connection")
    print("=" * 60)
