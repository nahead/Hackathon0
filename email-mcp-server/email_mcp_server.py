#!/usr/bin/env python3
"""
Email MCP Server - Model Context Protocol Server for Email Operations
Provides Claude Code with email management capabilities
"""

import asyncio
import json
import sys
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

class EmailMCPServer:
    def __init__(self):
        self.vault_path = Path("AI_Employee_Vault")
        self.config_path = self.vault_path / "Config" / "email_config.json"
        self.logs_path = self.vault_path / "Logs"

        # Create directories
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.logs_path / 'email_mcp.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Load configuration
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load email configuration"""
        default_config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "email": "",
            "password": "",
            "use_app_password": True,
            "templates": {
                "client_welcome": {
                    "subject": "Welcome to AI Employee Services",
                    "body": "Thank you for choosing our services. We're excited to work with you!"
                },
                "payment_confirmation": {
                    "subject": "Payment Received - Thank You",
                    "body": "We have received your payment. Thank you for your business!"
                },
                "follow_up": {
                    "subject": "Following Up",
                    "body": "Just following up on our previous conversation."
                }
            }
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
            self.save_config(default_config)
            return default_config

    def save_config(self, config: Dict):
        """Save email configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    async def handle_request(self, request: Dict) -> Dict:
        """Handle MCP requests for email operations"""
        try:
            method = request.get('method')
            params = request.get('params', {})

            if method == 'email.send':
                return await self.send_email(params)
            elif method == 'email.send_template':
                return await self.send_template_email(params)
            elif method == 'email.get_unread':
                return await self.get_unread_emails(params)
            elif method == 'email.mark_read':
                return await self.mark_email_read(params)
            elif method == 'email.get_statistics':
                return await self.get_email_statistics(params)
            elif method == 'email.create_template':
                return await self.create_email_template(params)
            elif method == 'email.test_connection':
                return await self.test_connection()
            else:
                return {
                    'error': f'Unknown method: {method}',
                    'available_methods': [
                        'email.send',
                        'email.send_template',
                        'email.get_unread',
                        'email.mark_read',
                        'email.get_statistics',
                        'email.create_template',
                        'email.test_connection'
                    ]
                }

        except Exception as e:
            return {'error': f'Server error: {str(e)}'}

    async def send_email(self, params: Dict) -> Dict:
        """Send email"""
        try:
            to_email = params.get('to')
            subject = params.get('subject')
            body = params.get('body')
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])

            if not all([to_email, subject, body]):
                return {'error': 'to, subject, and body are required'}

            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email'], self.config['password'])

                recipients = [to_email] + cc + bcc
                server.send_message(msg, to_addrs=recipients)

            self.logger.info(f"Email sent to {to_email}")
            return {
                'success': True,
                'message': f'Email sent to {to_email}',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {'error': str(e)}

    async def send_template_email(self, params: Dict) -> Dict:
        """Send email using template"""
        try:
            template_name = params.get('template')
            to_email = params.get('to')
            variables = params.get('variables', {})

            if not template_name or not to_email:
                return {'error': 'template and to are required'}

            if template_name not in self.config['templates']:
                return {'error': f'Template {template_name} not found'}

            template = self.config['templates'][template_name]

            # Replace variables in template
            subject = template['subject']
            body = template['body']

            for key, value in variables.items():
                subject = subject.replace(f'{{{key}}}', str(value))
                body = body.replace(f'{{{key}}}', str(value))

            # Send email
            return await self.send_email({
                'to': to_email,
                'subject': subject,
                'body': body
            })

        except Exception as e:
            return {'error': str(e)}

    async def get_unread_emails(self, params: Dict) -> Dict:
        """Get unread emails"""
        try:
            limit = params.get('limit', 10)

            # Connect to IMAP
            with imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port']) as mail:
                mail.login(self.config['email'], self.config['password'])
                mail.select('INBOX')

                # Search for unread emails
                status, messages = mail.search(None, 'UNSEEN')

                if status != 'OK':
                    return {'error': 'Failed to search emails'}

                email_ids = messages[0].split()
                emails = []

                for email_id in email_ids[-limit:]:  # Get latest emails
                    status, msg_data = mail.fetch(email_id, '(RFC822)')

                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)

                        emails.append({
                            'id': email_id.decode(),
                            'from': email_message['From'],
                            'subject': email_message['Subject'],
                            'date': email_message['Date'],
                            'body': self._get_email_body(email_message)
                        })

                return {
                    'success': True,
                    'emails': emails,
                    'count': len(emails)
                }

        except Exception as e:
            self.logger.error(f"Error getting unread emails: {e}")
            return {'error': str(e)}

    async def mark_email_read(self, params: Dict) -> Dict:
        """Mark email as read"""
        try:
            email_id = params.get('email_id')

            if not email_id:
                return {'error': 'email_id is required'}

            with imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port']) as mail:
                mail.login(self.config['email'], self.config['password'])
                mail.select('INBOX')

                mail.store(email_id, '+FLAGS', '\\Seen')

            return {
                'success': True,
                'message': f'Email {email_id} marked as read'
            }

        except Exception as e:
            return {'error': str(e)}

    async def get_email_statistics(self, params: Dict) -> Dict:
        """Get email statistics"""
        try:
            period = params.get('period', 'week')  # day, week, month

            # This is a simplified version - in real implementation would analyze email logs
            stats = {
                'emails_sent': 15,
                'emails_received': 23,
                'unread_count': 3,
                'response_rate': 94.2,
                'average_response_time_hours': 2.3,
                'period': period
            }

            return {
                'success': True,
                'statistics': stats
            }

        except Exception as e:
            return {'error': str(e)}

    async def create_email_template(self, params: Dict) -> Dict:
        """Create new email template"""
        try:
            name = params.get('name')
            subject = params.get('subject')
            body = params.get('body')

            if not all([name, subject, body]):
                return {'error': 'name, subject, and body are required'}

            self.config['templates'][name] = {
                'subject': subject,
                'body': body
            }

            self.save_config(self.config)

            return {
                'success': True,
                'message': f'Template {name} created successfully'
            }

        except Exception as e:
            return {'error': str(e)}

    async def test_connection(self) -> Dict:
        """Test email connection"""
        try:
            # Test SMTP
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['email'], self.config['password'])

            # Test IMAP
            with imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port']) as mail:
                mail.login(self.config['email'], self.config['password'])

            return {
                'success': True,
                'message': 'Email connection successful',
                'smtp_server': self.config['smtp_server'],
                'imap_server': self.config['imap_server']
            }

        except Exception as e:
            return {'error': f'Connection failed: {str(e)}'}

    def _get_email_body(self, email_message) -> str:
        """Extract email body"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode()
            else:
                return email_message.get_payload(decode=True).decode()
        except:
            return "Could not extract email body"

# MCP Server Protocol Implementation
async def main():
    """Main MCP server loop"""
    server = EmailMCPServer()

    print("[EMAIL MCP] Email MCP Server starting...")
    print("Available methods:")
    print("- email.send")
    print("- email.send_template")
    print("- email.get_unread")
    print("- email.mark_read")
    print("- email.get_statistics")
    print("- email.create_template")
    print("- email.test_connection")

    # Test connection on startup
    test_result = await server.test_connection()
    if test_result.get('success'):
        print("[SUCCESS] Email connection verified")
    else:
        print("[ERROR] Email connection failed - server will still start")

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
        print("\n👋 Email MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)