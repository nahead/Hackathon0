#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Webhook Handler
Receives messages from WhatsApp Cloud API in real-time
Integrates with intelligent auto-responder
"""

import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import intelligent responder
from intelligent_whatsapp_responder import IntelligentWhatsAppResponder

app = Flask(__name__)

# Configuration
WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'ai_employee_whatsapp_verify_2026')
VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
NEEDS_ACTION = VAULT_PATH / "Needs_Action"

# Ensure folder exists
NEEDS_ACTION.mkdir(parents=True, exist_ok=True)

# Initialize responder
responder = IntelligentWhatsAppResponder()


@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """
    WhatsApp webhook endpoint

    GET: Webhook verification (Meta requirement)
    POST: Receive incoming messages
    """

    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
            print(f"[WEBHOOK] ✅ Verified successfully")
            return challenge, 200
        else:
            print(f"[WEBHOOK] ❌ Verification failed")
            return 'Forbidden', 403

    elif request.method == 'POST':
        # Receive incoming message
        try:
            data = request.get_json()

            print(f"\n[WEBHOOK] Received data:")
            print(json.dumps(data, indent=2))

            # Extract message data
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})

            messages = value.get('messages', [])

            if not messages:
                return jsonify({'status': 'ok', 'message': 'No messages'}), 200

            # Process each message
            for message in messages:
                # Extract message details
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

                print(f"\n[MESSAGE] From: {contact_name} ({from_number})")
                print(f"[CONTENT] {content[:100]}...")

                # Create message data
                message_data = {
                    'id': message_id,
                    'from': from_number,
                    'name': contact_name,
                    'content': content,
                    'timestamp': datetime.fromtimestamp(int(timestamp)),
                    'type': message_type
                }

                # Process with intelligent responder
                responder.process_message(message_data)

            return jsonify({'status': 'ok'}), 200

        except Exception as e:
            print(f"[ERROR] Webhook processing failed: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'whatsapp_webhook',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Index page"""
    return """
    <html>
    <head>
        <title>WhatsApp Webhook - AI Employee</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #25D366; }
            .status { background: #e8f5e9; padding: 15px; border-radius: 5px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; }
            code { background: #333; color: #fff; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🤖 WhatsApp Webhook - AI Employee</h1>

        <div class="status">
            <h2>✅ Webhook Active</h2>
            <p>Intelligent auto-responder is running and ready to receive messages.</p>
        </div>

        <h2>📡 Endpoints</h2>

        <div class="endpoint">
            <strong>Webhook URL:</strong><br>
            <code>POST /webhook/whatsapp</code><br>
            Receives incoming WhatsApp messages
        </div>

        <div class="endpoint">
            <strong>Verification URL:</strong><br>
            <code>GET /webhook/whatsapp</code><br>
            For Meta webhook verification
        </div>

        <div class="endpoint">
            <strong>Health Check:</strong><br>
            <code>GET /health</code><br>
            Service health status
        </div>

        <h2>🔧 Setup Instructions</h2>
        <ol>
            <li>Deploy this service to Render.com or similar platform</li>
            <li>Get your public URL (e.g., https://your-app.onrender.com)</li>
            <li>Go to Meta Developer Dashboard → WhatsApp → Configuration</li>
            <li>Add webhook URL: <code>https://your-app.onrender.com/webhook/whatsapp</code></li>
            <li>Verify token: <code>ai_employee_whatsapp_verify_2026</code></li>
            <li>Subscribe to: <code>messages</code></li>
            <li>Save and test!</li>
        </ol>

        <h2>🤖 Features</h2>
        <ul>
            <li>✅ Real-time message reception</li>
            <li>✅ Intelligent classification (routine vs serious)</li>
            <li>✅ Auto-response for routine messages</li>
            <li>✅ Human approval for serious messages</li>
            <li>✅ Complete audit trail</li>
        </ul>

        <p><small>Powered by WhatsApp Cloud API + AI Employee System</small></p>
    </body>
    </html>
    """


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"Starting WhatsApp Webhook on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
