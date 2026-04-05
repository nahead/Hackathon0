#!/usr/bin/env python3
"""
Odoo MCP Server - Model Context Protocol Server for Odoo Integration
Provides Claude Code with direct access to Odoo accounting functions
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from odoo_integration import OdooIntegration
except ImportError:
    print("Error: odoo_integration.py not found. Please ensure it's in the same directory.")
    sys.exit(1)

# MCP Server implementation
class OdooMCPServer:
    def __init__(self):
        # Use absolute path to vault from parent directory
        self.vault_path = str(Path(__file__).parent.parent / "AI_Employee_Vault")
        self.odoo = OdooIntegration(self.vault_path)

    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests for Odoo operations"""
        try:
            method = request.get('method')
            params = request.get('params', {})

            if method == 'odoo.test_connection':
                return await self.test_connection()
            elif method == 'odoo.create_invoice':
                return await self.create_invoice(params)
            elif method == 'odoo.record_expense':
                return await self.record_expense(params)
            elif method == 'odoo.get_financial_summary':
                return await self.get_financial_summary()
            elif method == 'odoo.find_partner':
                return await self.find_partner(params)
            elif method == 'odoo.list_invoices':
                return await self.list_invoices(params)
            elif method == 'odoo.get_account_balance':
                return await self.get_account_balance(params)
            else:
                return {
                    'error': f'Unknown method: {method}',
                    'available_methods': [
                        'odoo.test_connection',
                        'odoo.create_invoice',
                        'odoo.record_expense',
                        'odoo.get_financial_summary',
                        'odoo.find_partner',
                        'odoo.list_invoices',
                        'odoo.get_account_balance'
                    ]
                }

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}

    async def test_connection(self) -> Dict:
        """Test Odoo connection"""
        try:
            success = self.odoo.test_connection()
            return {
                'success': success,
                'message': 'Connection successful' if success else 'Connection failed',
                'odoo_url': self.odoo.config.get('odoo_url'),
                'database': self.odoo.config.get('database')
            }
        except Exception as e:
            return {'error': str(e)}

    async def create_invoice(self, params: Dict) -> Dict:
        """Create customer invoice"""
        try:
            partner_name = params.get('partner_name')
            amount = params.get('amount')
            description = params.get('description', 'Service')

            if not partner_name or not amount:
                return {'error': 'partner_name and amount are required'}

            invoice_id = self.odoo.create_invoice(partner_name, float(amount), description)

            if invoice_id:
                return {
                    'success': True,
                    'invoice_id': invoice_id,
                    'message': f'Invoice created for {partner_name}: ${amount}'
                }
            else:
                return {'error': 'Failed to create invoice'}

        except Exception as e:
            return {'error': str(e)}

    async def record_expense(self, params: Dict) -> Dict:
        """Record business expense"""
        try:
            description = params.get('description')
            amount = params.get('amount')
            category = params.get('category', 'General')

            if not description or not amount:
                return {'error': 'description and amount are required'}

            expense_id = self.odoo.record_expense(description, float(amount), category)

            if expense_id:
                return {
                    'success': True,
                    'expense_id': expense_id,
                    'message': f'Expense recorded: {description} - ${amount}'
                }
            else:
                return {'error': 'Failed to record expense'}

        except Exception as e:
            return {'error': str(e)}

    async def get_financial_summary(self) -> Dict:
        """Get financial summary"""
        try:
            summary = self.odoo.get_financial_summary()
            return {
                'success': True,
                'summary': summary
            }
        except Exception as e:
            return {'error': str(e)}

    async def find_partner(self, params: Dict) -> Dict:
        """Find partner by name"""
        try:
            name = params.get('name')
            if not name:
                return {'error': 'name parameter is required'}

            partner_id = self.odoo.find_or_create_partner(name)

            if partner_id:
                return {
                    'success': True,
                    'partner_id': partner_id,
                    'message': f'Partner found/created: {name}'
                }
            else:
                return {'error': 'Failed to find/create partner'}

        except Exception as e:
            return {'error': str(e)}

    async def list_invoices(self, params: Dict) -> Dict:
        """List invoices with optional filters"""
        try:
            limit = params.get('limit', 10)
            invoice_type = params.get('type', 'out_invoice')  # out_invoice, in_invoice

            invoices = self.odoo.call_odoo_method('account.move', 'search_read', [
                [('move_type', '=', invoice_type)]
            ], {
                'fields': ['name', 'partner_id', 'amount_total', 'invoice_date', 'state'],
                'limit': limit,
                'order': 'invoice_date desc'
            })

            if invoices:
                return {
                    'success': True,
                    'invoices': invoices,
                    'count': len(invoices)
                }
            else:
                return {'error': 'No invoices found or failed to retrieve'}

        except Exception as e:
            return {'error': str(e)}

    async def get_account_balance(self, params: Dict) -> Dict:
        """Get account balance"""
        try:
            account_code = params.get('account_code')
            if not account_code:
                return {'error': 'account_code parameter is required'}

            # Find account by code
            accounts = self.odoo.call_odoo_method('account.account', 'search_read', [
                [('code', '=like', f'{account_code}%')]
            ], {'fields': ['name', 'code', 'balance'], 'limit': 1})

            if accounts:
                account = accounts[0]
                return {
                    'success': True,
                    'account': {
                        'name': account['name'],
                        'code': account['code'],
                        'balance': account.get('balance', 0)
                    }
                }
            else:
                return {'error': f'Account with code {account_code} not found'}

        except Exception as e:
            return {'error': str(e)}

# MCP Server Protocol Implementation
async def main():
    """Main MCP server loop"""
    server = OdooMCPServer()

    print("[ODOO MCP] Odoo MCP Server starting...")
    print("Available methods:")
    print("- odoo.test_connection")
    print("- odoo.create_invoice")
    print("- odoo.record_expense")
    print("- odoo.get_financial_summary")
    print("- odoo.find_partner")
    print("- odoo.list_invoices")
    print("- odoo.get_account_balance")

    # Test connection on startup
    test_result = await server.test_connection()
    if test_result.get('success'):
        print("[SUCCESS] Odoo connection verified")
    else:
        print("[ERROR] Odoo connection failed - server will still start")

    # Simple JSON-RPC over stdin/stdout for MCP
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line.strip())
            response = await server.handle_request(request)

            # Add JSON-RPC envelope
            rpc_response = {
                'jsonrpc': '2.0',
                'id': request.get('id'),
                'result': response
            }

            print(json.dumps(rpc_response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32700, 'message': 'Parse error'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': request.get('id') if 'request' in locals() else None,
                'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Odoo MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)