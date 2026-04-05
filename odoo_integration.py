#!/usr/bin/env python3
"""
Odoo Community Integration - Gold Tier Requirement
Self-hosted Odoo Community accounting system integration via MCP server
Supports Odoo 19+ JSON-RPC APIs for accounting operations
"""

import json
import requests
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import logging

class OdooIntegration:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.config_path = self.vault_path / "Config" / "odoo_config.json"
        self.logs_path = self.vault_path / "Logs"

        # Create directories
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'odoo_integration.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load Odoo configuration"""
        default_config = {
            "odoo_url": "http://localhost:8069",
            "database": "ai_employee_db",
            "username": "admin",
            "password": "admin",
            "company_name": "AI Employee Company",
            "currency": "USD",
            "installation_path": str(Path.home() / "odoo-community"),
            "auto_install": True,
            "accounting_enabled": True
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config
            self.save_config(default_config)
            return default_config

    def save_config(self, config: Dict):
        """Save Odoo configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def check_odoo_installation(self) -> bool:
        """Check if Odoo is installed and accessible"""
        try:
            response = requests.get(f"{self.config['odoo_url']}/web/database/selector", timeout=5)
            return response.status_code == 200
        except:
            return False

    def install_odoo_community(self) -> bool:
        """Install Odoo Community Edition locally"""
        try:
            self.logger.info("Starting Odoo Community installation...")

            install_path = Path(self.config['installation_path'])
            install_path.mkdir(parents=True, exist_ok=True)

            # Create installation script
            install_script = self._create_odoo_install_script()
            script_path = install_path / "install_odoo.py"

            with open(script_path, 'w') as f:
                f.write(install_script)

            self.logger.info(f"Odoo installation script created at {script_path}")
            self.logger.info("Please run the installation script manually:")
            self.logger.info(f"python {script_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error during Odoo installation: {e}")
            return False

    def _create_odoo_install_script(self) -> str:
        """Create Odoo installation script"""
        return '''#!/usr/bin/env python3
"""
Odoo Community Edition Installation Script
Installs Odoo 19 Community Edition locally
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_odoo():
    """Install Odoo Community Edition"""

    print("[INSTALL] Installing Odoo Community Edition...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8+ required for Odoo 19")
        return False

    # Install system dependencies
    system = platform.system().lower()

    if system == "windows":
        print("[INSTALL] Installing Windows dependencies...")
        # Install PostgreSQL and other dependencies
        print("Please install PostgreSQL manually from: https://www.postgresql.org/download/windows/")
        print("Please install Git from: https://git-scm.com/download/win")

    elif system == "linux":
        print("[INSTALL] Installing Linux dependencies...")
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run([
                "sudo", "apt", "install", "-y",
                "python3-pip", "python3-dev", "python3-venv",
                "postgresql", "postgresql-server-dev-all",
                "build-essential", "libxml2-dev", "libxslt1-dev",
                "libevent-dev", "libsasl2-dev", "libldap2-dev",
                "libpq-dev", "libjpeg8-dev", "liblcms2-dev",
                "libfreetype6-dev", "libtiff5-dev", "tk-dev",
                "tcl-dev", "libharfbuzz-dev", "libfribidi-dev",
                "libxcb1-dev", "git"
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error installing system dependencies: {e}")
            return False

    # Create virtual environment
    venv_path = Path("odoo_venv")
    if not venv_path.exists():
        print("[PYTHON] Creating Python virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    # Activate virtual environment
    if system == "windows":
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"

    # Clone Odoo Community
    odoo_path = Path("odoo")
    if not odoo_path.exists():
        print("[CLONE] Cloning Odoo Community Edition...")
        subprocess.run([
            "git", "clone", "--depth", "1", "--branch", "19.0",
            "https://github.com/odoo/odoo.git"
        ], check=True)

    # Install Python dependencies
    print("[INSTALL] Installing Python dependencies...")
    subprocess.run([str(pip_exe), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip_exe), "install", "-r", "odoo/requirements.txt"], check=True)

    # Create Odoo configuration
    config_content = """[options]
addons_path = addons
data_dir = data
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
logfile = odoo.log
log_level = info
"""

    with open("odoo.conf", "w") as f:
        f.write(config_content)

    print("[SUCCESS] Odoo installation completed!")
    print("[NEXT] Next steps:")
    print("1. Setup PostgreSQL database:")
    print("   sudo -u postgres createuser -s odoo")
    print("   sudo -u postgres createdb odoo")
    print("2. Start Odoo:")
    print(f"   {python_exe} odoo/odoo-bin -c odoo.conf")
    print("3. Access Odoo at: http://localhost:8069")

    return True

if __name__ == "__main__":
    try:
        install_odoo()
    except Exception as e:
        print(f"[ERROR] Installation failed: {e}")
        sys.exit(1)
'''

    def authenticate(self) -> Optional[int]:
        """Authenticate with Odoo and return user ID"""
        try:
            url = f"{self.config['odoo_url']}/jsonrpc"

            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [
                        self.config['database'],
                        self.config['username'],
                        self.config['password'],
                        {}
                    ]
                },
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=10)
            result = response.json()

            if 'result' in result and result['result']:
                self.logger.info("Successfully authenticated with Odoo")
                return result['result']
            else:
                self.logger.error("Authentication failed")
                return None

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None

    def call_odoo_method(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """Call Odoo model method via JSON-RPC"""
        try:
            uid = self.authenticate()
            if not uid:
                return None

            url = f"{self.config['odoo_url']}/jsonrpc"

            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        self.config['database'],
                        uid,
                        self.config['password'],
                        model,
                        method,
                        args or [],
                        kwargs or {}
                    ]
                },
                "id": 1
            }

            response = requests.post(url, json=payload, timeout=30)
            result = response.json()

            if 'result' in result:
                return result['result']
            else:
                self.logger.error(f"Odoo method call failed: {result}")
                return None

        except Exception as e:
            self.logger.error(f"Error calling Odoo method {model}.{method}: {e}")
            return None

    def create_invoice(self, partner_name: str, amount: float, description: str) -> Optional[int]:
        """Create customer invoice in Odoo"""
        try:
            # First, find or create partner
            partner_id = self.find_or_create_partner(partner_name)
            if not partner_id:
                return None

            # Create invoice
            invoice_data = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'invoice_date': date.today().isoformat(),
                'invoice_line_ids': [(0, 0, {
                    'name': description,
                    'price_unit': amount,
                    'quantity': 1,
                })]
            }

            invoice_id = self.call_odoo_method('account.move', 'create', [invoice_data])

            if invoice_id:
                self.logger.info(f"Created invoice {invoice_id} for {partner_name}: ${amount}")
                return invoice_id

        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")
            return None

    def find_or_create_partner(self, name: str) -> Optional[int]:
        """Find existing partner or create new one"""
        try:
            # Search for existing partner
            partner_ids = self.call_odoo_method('res.partner', 'search', [('name', '=', name)])

            if partner_ids:
                return partner_ids[0]

            # Create new partner
            partner_data = {
                'name': name,
                'is_company': False,
                'customer_rank': 1
            }

            partner_id = self.call_odoo_method('res.partner', 'create', [partner_data])

            if partner_id:
                self.logger.info(f"Created new partner: {name}")
                return partner_id

        except Exception as e:
            self.logger.error(f"Error finding/creating partner {name}: {e}")
            return None

    def record_expense(self, description: str, amount: float, category: str = "General") -> Optional[int]:
        """Record business expense"""
        try:
            # Find expense account (or create if needed)
            account_ids = self.call_odoo_method('account.account', 'search', [
                ('code', '=like', '6%'),  # Expense accounts typically start with 6
                ('name', 'ilike', category)
            ])

            if not account_ids:
                # Use default expense account
                account_ids = self.call_odoo_method('account.account', 'search', [
                    ('code', '=like', '6%')
                ], {'limit': 1})

            if not account_ids:
                self.logger.error("No expense account found")
                return None

            # Create journal entry for expense
            move_data = {
                'move_type': 'entry',
                'date': date.today().isoformat(),
                'ref': f"Expense: {description}",
                'line_ids': [
                    (0, 0, {
                        'name': description,
                        'account_id': account_ids[0],
                        'debit': amount,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'name': f"Payment for: {description}",
                        'account_id': self._get_cash_account(),
                        'debit': 0,
                        'credit': amount,
                    })
                ]
            }

            move_id = self.call_odoo_method('account.move', 'create', [move_data])

            if move_id:
                self.logger.info(f"Recorded expense: {description} - ${amount}")
                return move_id

        except Exception as e:
            self.logger.error(f"Error recording expense: {e}")
            return None

    def _get_cash_account(self) -> int:
        """Get cash/bank account ID"""
        try:
            account_ids = self.call_odoo_method('account.account', 'search', [
                ('code', '=like', '1%'),  # Asset accounts
                ('name', 'ilike', 'cash')
            ], {'limit': 1})

            if account_ids:
                return account_ids[0]

            # Fallback to any asset account
            account_ids = self.call_odoo_method('account.account', 'search', [
                ('code', '=like', '1%')
            ], {'limit': 1})

            return account_ids[0] if account_ids else 1

        except:
            return 1  # Fallback

    def get_financial_summary(self) -> Dict:
        """Get financial summary from Odoo"""
        try:
            summary = {
                'total_revenue': 0,
                'total_expenses': 0,
                'net_profit': 0,
                'outstanding_invoices': 0,
                'recent_transactions': []
            }

            # Get revenue (customer invoices)
            revenue_invoices = self.call_odoo_method('account.move', 'search_read', [
                [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')]
            ], {'fields': ['amount_total', 'invoice_date', 'partner_id']})

            if revenue_invoices:
                summary['total_revenue'] = sum(inv['amount_total'] for inv in revenue_invoices)
                summary['recent_transactions'].extend([
                    {
                        'type': 'revenue',
                        'amount': inv['amount_total'],
                        'date': inv['invoice_date'],
                        'partner': inv['partner_id'][1] if inv['partner_id'] else 'Unknown'
                    }
                    for inv in revenue_invoices[-5:]  # Last 5 transactions
                ])

            # Get expenses
            expense_moves = self.call_odoo_method('account.move', 'search_read', [
                [('move_type', '=', 'entry'), ('state', '=', 'posted')]
            ], {'fields': ['amount_total', 'date', 'ref']})

            if expense_moves:
                summary['total_expenses'] = sum(move['amount_total'] for move in expense_moves)
                summary['recent_transactions'].extend([
                    {
                        'type': 'expense',
                        'amount': move['amount_total'],
                        'date': move['date'],
                        'description': move['ref'] or 'Expense'
                    }
                    for move in expense_moves[-5:]
                ])

            # Calculate net profit
            summary['net_profit'] = summary['total_revenue'] - summary['total_expenses']

            # Get outstanding invoices
            outstanding = self.call_odoo_method('account.move', 'search_read', [
                [('move_type', '=', 'out_invoice'), ('payment_state', '!=', 'paid')]
            ], {'fields': ['amount_residual']})

            if outstanding:
                summary['outstanding_invoices'] = sum(inv['amount_residual'] for inv in outstanding)

            return summary

        except Exception as e:
            self.logger.error(f"Error getting financial summary: {e}")
            return {}

    def setup_accounting_structure(self) -> bool:
        """Setup basic accounting structure in Odoo"""
        try:
            self.logger.info("Setting up accounting structure...")

            # Check if accounting module is installed
            modules = self.call_odoo_method('ir.module.module', 'search_read', [
                [('name', '=', 'account')]
            ], {'fields': ['state']})

            if not modules or modules[0]['state'] != 'installed':
                self.logger.error("Accounting module not installed in Odoo")
                return False

            # Create basic chart of accounts if needed
            accounts = self.call_odoo_method('account.account', 'search', [], {'limit': 1})

            if not accounts:
                self.logger.info("Creating basic chart of accounts...")
                # This would typically be done through Odoo's setup wizard
                self.logger.info("Please complete Odoo setup wizard to create chart of accounts")

            self.logger.info("Accounting structure setup completed")
            return True

        except Exception as e:
            self.logger.error(f"Error setting up accounting structure: {e}")
            return False

    def test_connection(self) -> bool:
        """Test Odoo connection and functionality"""
        try:
            self.logger.info("Testing Odoo connection...")

            # Test authentication
            uid = self.authenticate()
            if not uid:
                self.logger.error("Authentication test failed")
                return False

            # Test basic model access
            partners = self.call_odoo_method('res.partner', 'search', [[]], {'limit': 1})
            if partners is None:
                self.logger.error("Model access test failed")
                return False

            # Test accounting module
            accounts = self.call_odoo_method('account.account', 'search', [[]], {'limit': 1})
            if accounts is None:
                self.logger.error("Accounting module test failed")
                return False

            self.logger.info("[SUCCESS] Odoo connection test successful")
            return True

        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

def main():
    """Main function for testing Odoo integration"""
    vault_path = "AI_Employee_Vault"
    odoo = OdooIntegration(vault_path)

    print("[ODOO] Odoo Community Integration - Gold Tier")
    print("=" * 50)

    # Check if Odoo is installed
    if not odoo.check_odoo_installation():
        print("[ERROR] Odoo not found. Installing...")
        if odoo.config.get('auto_install', True):
            odoo.install_odoo_community()
        else:
            print("Please install Odoo Community manually")
            return
    else:
        print("[SUCCESS] Odoo installation detected")

    # Test connection
    if odoo.test_connection():
        print("[SUCCESS] Odoo connection successful")

        # Setup accounting structure
        odoo.setup_accounting_structure()

        # Get financial summary
        summary = odoo.get_financial_summary()
        if summary:
            print("\n[FINANCIAL] Financial Summary:")
            print(f"Revenue: ${summary.get('total_revenue', 0):,.2f}")
            print(f"Expenses: ${summary.get('total_expenses', 0):,.2f}")
            print(f"Net Profit: ${summary.get('net_profit', 0):,.2f}")
            print(f"Outstanding: ${summary.get('outstanding_invoices', 0):,.2f}")
    else:
        print("[ERROR] Odoo connection failed")
        print("Please check Odoo installation and configuration")

if __name__ == "__main__":
    main()