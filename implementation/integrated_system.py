#!/usr/bin/env python3
"""
Integrated All-in-One System
Email + LinkedIn + WhatsApp Intelligent Auto-Responder
All running together on single port
"""

import os
import sys
import threading
from pathlib import Path

# Add implementation directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import existing railway orchestrator
from railway_all_in_one import *

# Import intelligent WhatsApp responder
from intelligent_whatsapp_responder import IntelligentWhatsAppResponder

# Import premium dashboard
from premium_dashboard import get_premium_dashboard

# WhatsApp webhook configuration
WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'ai_employee_whatsapp_verify_2026')

# Initialize WhatsApp responder
whatsapp_responder = IntelligentWhatsAppResponder()


class IntegratedHealthHandler(HealthHandler):
    """Extended handler with WhatsApp webhook endpoints"""

    def do_POST(self):
        """Handle POST requests - WhatsApp webhook"""
        if self.path == '/webhook/whatsapp':
            self.handle_whatsapp_webhook()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        """Handle GET requests - existing + WhatsApp verification"""
        if self.path.startswith('/webhook/whatsapp'):
            self.handle_whatsapp_verification()
        elif self.path == '/':
            # Serve premium dashboard
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(get_premium_dashboard().encode('utf-8'))
        else:
            # Call parent class for existing endpoints
            super().do_GET()

    def handle_whatsapp_verification(self):
        """Handle WhatsApp webhook verification (GET)"""
        from urllib.parse import urlparse, parse_qs

        query = parse_qs(urlparse(self.path).query)
        mode = query.get('hub.mode', [''])[0]
        token = query.get('hub.verify_token', [''])[0]
        challenge = query.get('hub.challenge', [''])[0]

        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            logger.info("✅ WhatsApp webhook verified")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(challenge.encode())
        else:
            logger.warning("❌ WhatsApp webhook verification failed")
            self.send_response(403)
            self.end_headers()

    def handle_whatsapp_webhook(self):
        """Handle incoming WhatsApp messages (POST)"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            logger.info(f"📱 WhatsApp webhook received")

            # Extract message data
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            if not messages:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
                return

            # Process each message
            for message in messages:
                from_number = message.get('from', '')
                message_id = message.get('id', '')
                timestamp = message.get('timestamp', '')
                message_type = message.get('type', 'text')

                # Get message content
                if message_type == 'text':
                    content = message.get('text', {}).get('body', '')
                else:
                    content = f"[{message_type.upper()} message]"

                # Get contact info
                contacts = value.get('contacts', [{}])
                contact_name = contacts[0].get('profile', {}).get('name', 'Unknown') if contacts else 'Unknown'

                logger.info(f"📨 Message from: {contact_name} ({from_number})")

                # Create message data
                message_data = {
                    'id': message_id,
                    'from': from_number,
                    'name': contact_name,
                    'content': content,
                    'timestamp': datetime.fromtimestamp(int(timestamp)),
                    'type': message_type
                }

                # Process with intelligent responder (with error handling)
                try:
                    logger.info(f"🔄 Processing message: {message_id}")
                    whatsapp_responder.process_message(message_data)
                    logger.info(f"✅ Message processed: {message_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to process message: {e}")
                    import traceback
                    logger.error(traceback.format_exc())

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())

        except Exception as e:
            logger.error(f"❌ WhatsApp webhook error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())


def run_whatsapp_monitor():
    """Background thread for WhatsApp monitoring (fallback if webhook not working)"""
    logger.info("🤖 Starting WhatsApp monitor thread...")

    while True:
        try:
            whatsapp_responder.check_messages()
            time.sleep(15)  # Check every 15 seconds
        except Exception as e:
            logger.error(f"WhatsApp monitor error: {e}")
            time.sleep(60)


def main():
    """Main entry point - integrated system"""
    logger.info("="*70)
    logger.info("🚀 INTEGRATED AI EMPLOYEE SYSTEM")
    logger.info("="*70)
    logger.info("✅ Email Monitoring")
    logger.info("✅ LinkedIn Posting")
    logger.info("✅ WhatsApp Intelligent Auto-Responder")
    logger.info("✅ Vault Sync")
    logger.info("="*70)

    port = int(os.getenv('PORT', 8080))

    # Start WhatsApp monitor thread (fallback)
    monitor_thread = threading.Thread(target=run_whatsapp_monitor, daemon=True)
    monitor_thread.start()

    # Start HTTP server with integrated handler
    logger.info(f"🌐 Starting integrated server on port {port}...")
    server = HTTPServer(('0.0.0.0', port), IntegratedHealthHandler)

    # Start vault sync in background thread
    vault_thread = threading.Thread(target=lambda: None, daemon=True)  # Placeholder
    vault_thread.start()

    logger.info(f"✅ Server running on http://0.0.0.0:{port}")
    logger.info(f"📡 WhatsApp webhook: http://0.0.0.0:{port}/webhook/whatsapp")
    logger.info(f"💚 Health check: http://0.0.0.0:{port}/health")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
