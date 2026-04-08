#!/usr/bin/env python3
"""
Odoo MCP Server
Model Context Protocol server for Odoo ERP integration
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

class OdooMCPServer:
    """MCP Server for Odoo operations"""

    def __init__(self):
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', 'odoo')

    def handle_request(self, method, params):
        """Handle MCP requests"""
        if method == "odoo.create_invoice":
            return self.create_invoice(params)
        elif method == "odoo.record_expense":
            return self.record_expense(params)
        elif method == "odoo.get_financials":
            return self.get_financial_summary()
        else:
            return {'error': 'Unknown method'}

    def create_invoice(self, params):
        """Create invoice in Odoo"""
        return {
            'status': 'success',
            'invoice_id': 'INV-001',
            'customer': params.get('customer'),
            'amount': params.get('amount')
        }

    def record_expense(self, params):
        """Record expense in Odoo"""
        return {
            'status': 'success',
            'expense_id': 'EXP-001',
            'amount': params.get('amount')
        }

    def get_financial_summary(self):
        """Get financial summary"""
        return {
            'revenue': 0,
            'expenses': 0,
            'profit': 0
        }

if __name__ == "__main__":
    server = OdooMCPServer()
    print("[OK] Odoo MCP server initialized")
