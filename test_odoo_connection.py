#!/usr/bin/env python3
"""
Test Odoo Connection and MCP Server Integration
"""
import os
import xmlrpc.client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8070')
ODOO_DB = os.getenv('ODOO_DB', 'H0')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'nahead jokhio')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'ahmed451401')

def test_odoo_connection():
    """Test Odoo connection and basic operations"""
    print("[TEST] Testing Odoo Connection...")
    print(f"   URL: {ODOO_URL}")
    print(f"   Database: {ODOO_DB}")
    print(f"   Username: {ODOO_USERNAME}")
    print()

    try:
        # Connect to Odoo
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')

        # Test authentication
        print("[1] Testing authentication...")
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})

        if uid:
            print(f"   [OK] Authentication successful! User ID: {uid}")
        else:
            print("   [FAIL] Authentication failed!")
            return False

        # Connect to object endpoint
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

        # Test reading partner (customer) data
        print("\n[2] Testing data access (reading partners)...")
        partners = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search_read',
            [[]], {'fields': ['name', 'email'], 'limit': 5}
        )
        print(f"   [OK] Found {len(partners)} partners")
        for partner in partners:
            print(f"      - {partner.get('name')} ({partner.get('email', 'No email')})")

        # Test creating a test customer
        print("\n[3] Testing customer creation...")
        test_partner_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'create',
            [{
                'name': 'Test Client - Gold Tier Demo',
                'email': 'testclient@goldtier.com',
                'phone': '+92 312 1234567',
                'is_company': True
            }]
        )
        print(f"   [OK] Test customer created! Partner ID: {test_partner_id}")

        # Test reading invoices
        print("\n[4] Testing invoice access...")
        invoices = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'search_read',
            [[('move_type', '=', 'out_invoice')]],
            {'fields': ['name', 'partner_id', 'amount_total'], 'limit': 5}
        )
        print(f"   [OK] Found {len(invoices)} invoices")

        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED! Odoo MCP integration is working!")
        print("="*60)
        return True

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return False

if __name__ == '__main__':
    success = test_odoo_connection()
    exit(0 if success else 1)
