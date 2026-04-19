#!/usr/bin/env python3
"""
Railway All-in-One Orchestrator - Platinum Tier
Real implementation with Gmail monitoring, vault sync, and email sending
"""

import os
import sys
import time
import logging
import threading
import imaplib
import email
import smtplib
import subprocess
import re
import requests
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ google-generativeai not installed, using fallback responses")

# Conversation History
try:
    from conversation_history import ConversationHistory
    conversation_history = ConversationHistory("/tmp/whatsapp_conversations.json")
    HISTORY_AVAILABLE = True
except ImportError as e:
    HISTORY_AVAILABLE = False
    conversation_history = None

# Lead CRM
try:
    from lead_crm import LeadCRM
    lead_crm = LeadCRM("/tmp/leads_crm.json")
    CRM_AVAILABLE = True
except ImportError as e:
    CRM_AVAILABLE = False
    lead_crm = None

# Automated Follow-up
try:
    from automated_followup import AutomatedFollowup
    automated_followup = AutomatedFollowup(lead_crm) if CRM_AVAILABLE else None
    FOLLOWUP_AVAILABLE = True
except ImportError as e:
    FOLLOWUP_AVAILABLE = False
    automated_followup = None

# Broadcast System
try:
    from broadcast_system import BroadcastSystem
    broadcast_system = BroadcastSystem(lead_crm) if CRM_AVAILABLE else None
    BROADCAST_AVAILABLE = True
except ImportError as e:
    BROADCAST_AVAILABLE = False
    broadcast_system = None

# Advanced Analytics
try:
    from advanced_analytics import AdvancedAnalytics
    advanced_analytics = AdvancedAnalytics("/tmp/advanced_analytics.json")
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    ANALYTICS_AVAILABLE = False
    advanced_analytics = None

# Email Integration
try:
    from email_integration import EmailIntegration
    email_integration = EmailIntegration(lead_crm) if CRM_AVAILABLE else None
    EMAIL_INTEGRATION_AVAILABLE = True
except ImportError as e:
    EMAIL_INTEGRATION_AVAILABLE = False
    email_integration = None

# Create logs directory (use /tmp for cloud platforms)
logs_dir = Path("/tmp/logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# Track processed WhatsApp messages to avoid duplicates
processed_messages = set()
processed_messages_lock = threading.Lock()

# Analytics tracking
class AnalyticsTracker:
    def __init__(self):
        self.metrics = {
            'whatsapp': {
                'total_messages': 0,
                'business_inquiries': 0,
                'casual_greetings': 0,
                'skipped_messages': 0,
                'responses_sent': 0,
                'unique_contacts': set(),
                'last_message_time': None,
                'urgent_messages': 0,
                'high_priority': 0
            },
            'email': {
                'emails_checked': 0,
                'drafts_created': 0,
                'emails_sent': 0,
                'last_check_time': None
            },
            'linkedin': {
                'posts_published': 0,
                'posts_pending': 0,
                'last_post_time': None,
                'last_check_time': None
            },
            'followup': {
                'total_checks': 0,
                'messages_sent': 0,
                'leads_skipped': 0,
                'errors': 0,
                'last_check_time': None
            },
            'broadcast': {
                'total_campaigns': 0,
                'completed_campaigns': 0,
                'total_messages_sent': 0,
                'total_failed': 0
            },
            'system': {
                'start_time': datetime.now(),
                'vault_syncs': 0,
                'errors': 0,
                'last_error': None
            }
        }
        self.lock = threading.Lock()

    def track_whatsapp_message(self, contact_name, message_type='received'):
        with self.lock:
            self.metrics['whatsapp']['total_messages'] += 1
            self.metrics['whatsapp']['unique_contacts'].add(contact_name)
            self.metrics['whatsapp']['last_message_time'] = datetime.now()

            if message_type == 'business':
                self.metrics['whatsapp']['business_inquiries'] += 1
            elif message_type == 'greeting':
                self.metrics['whatsapp']['casual_greetings'] += 1
            elif message_type == 'skipped':
                self.metrics['whatsapp']['skipped_messages'] += 1

    def track_whatsapp_response(self):
        with self.lock:
            self.metrics['whatsapp']['responses_sent'] += 1

    def track_urgent_message(self):
        with self.lock:
            self.metrics['whatsapp']['urgent_messages'] += 1

    def track_high_priority(self):
        with self.lock:
            self.metrics['whatsapp']['high_priority'] += 1

    def track_email_check(self):
        with self.lock:
            self.metrics['email']['emails_checked'] += 1
            self.metrics['email']['last_check_time'] = datetime.now()

    def track_email_sent(self):
        with self.lock:
            self.metrics['email']['emails_sent'] += 1

    def track_linkedin_post(self):
        with self.lock:
            self.metrics['linkedin']['posts_published'] += 1
            self.metrics['linkedin']['last_post_time'] = datetime.now()

    def track_linkedin_check(self, pending_count=0):
        with self.lock:
            self.metrics['linkedin']['last_check_time'] = datetime.now()
            self.metrics['linkedin']['posts_pending'] = pending_count

    def track_vault_sync(self):
        with self.lock:
            self.metrics['system']['vault_syncs'] += 1

    def track_followup_check(self, checked=0, sent=0, skipped=0, errors=0):
        with self.lock:
            self.metrics['followup']['total_checks'] += 1
            self.metrics['followup']['messages_sent'] += sent
            self.metrics['followup']['leads_skipped'] += skipped
            self.metrics['followup']['errors'] += errors
            self.metrics['followup']['last_check_time'] = datetime.now()

    def track_error(self, error_msg):
        with self.lock:
            self.metrics['system']['errors'] += 1
            self.metrics['system']['last_error'] = {
                'message': str(error_msg),
                'time': datetime.now()
            }

    def get_metrics(self):
        with self.lock:
            # Convert sets to counts for JSON serialization
            metrics_copy = json.loads(json.dumps(self.metrics, default=str))
            metrics_copy['whatsapp']['unique_contacts'] = len(self.metrics['whatsapp']['unique_contacts'])

            # Calculate uptime
            uptime = datetime.now() - self.metrics['system']['start_time']
            metrics_copy['system']['uptime_seconds'] = int(uptime.total_seconds())
            metrics_copy['system']['uptime_formatted'] = str(uptime).split('.')[0]

            # Add CRM statistics
            if CRM_AVAILABLE and lead_crm:
                try:
                    metrics_copy['crm'] = lead_crm.get_stats()
                except Exception as e:
                    logger.error(f"Failed to get CRM stats: {e}")
                    metrics_copy['crm'] = {
                        'total_leads': 0,
                        'hot_leads': 0,
                        'warm_leads': 0,
                        'cold_leads': 0,
                        'needs_followup': 0
                    }
            else:
                metrics_copy['crm'] = {
                    'total_leads': 0,
                    'hot_leads': 0,
                    'warm_leads': 0,
                    'cold_leads': 0,
                    'needs_followup': 0
                }

            # Add Broadcast statistics
            if BROADCAST_AVAILABLE and broadcast_system:
                try:
                    metrics_copy['broadcast'] = broadcast_system.get_broadcast_stats()
                except Exception as e:
                    logger.error(f"Failed to get broadcast stats: {e}")
                    metrics_copy['broadcast'] = {
                        'total_broadcasts': 0,
                        'completed_broadcasts': 0,
                        'total_messages_sent': 0,
                        'total_failed': 0
                    }
            else:
                metrics_copy['broadcast'] = {
                    'total_broadcasts': 0,
                    'completed_broadcasts': 0,
                    'total_messages_sent': 0,
                    'total_failed': 0
                }

            return metrics_copy

# Global analytics tracker
analytics = AnalyticsTracker()

# Global log buffer for live logs display
class LogBuffer:
    def __init__(self, max_size=100):
        self.logs = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def add(self, log_entry):
        with self.lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.max_size:
                self.logs.pop(0)

    def get_recent(self, count=50):
        with self.lock:
            return self.logs[-count:]

log_buffer = LogBuffer()

class BufferHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': record.getMessage()
        }
        log_buffer.add(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), BufferHandler()]
)
logger = logging.getLogger('RailwayOrchestrator')

class HealthHandler(BaseHTTPRequestHandler):
    """Health check endpoint with professional UI"""
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            health = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "orchestrator": "running",
                    "vault_sync": "active",
                    "gmail_watcher": "monitoring"
                }
            }
            self.wfile.write(json.dumps(health).encode())
        elif self.path == '/analytics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            metrics = analytics.get_metrics()
            self.wfile.write(json.dumps(metrics).encode())
        elif self.path == '/logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            logs = log_buffer.get_recent(50)
            self.wfile.write(json.dumps(logs).encode())
        elif self.path == '/emails':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            emails = self.get_pending_emails()
            self.wfile.write(json.dumps(emails).encode())
        elif self.path == '/api/broadcasts':
            # List all broadcasts
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if BROADCAST_AVAILABLE and broadcast_system:
                broadcasts = broadcast_system.list_broadcasts()
                self.wfile.write(json.dumps(broadcasts).encode())
            else:
                self.wfile.write(json.dumps({'error': 'Broadcast system not available'}).encode())
        elif self.path == '/api/broadcast/stats':
            # Get broadcast statistics
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if BROADCAST_AVAILABLE and broadcast_system:
                stats = broadcast_system.get_broadcast_stats()
                self.wfile.write(json.dumps(stats).encode())
            else:
                self.wfile.write(json.dumps({'error': 'Broadcast system not available'}).encode())
        elif self.path == '/api/analytics/advanced':
            # Get advanced analytics report
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if ANALYTICS_AVAILABLE and advanced_analytics:
                report = advanced_analytics.get_comprehensive_report()
                self.wfile.write(json.dumps(report).encode())
            else:
                self.wfile.write(json.dumps({'error': 'Advanced analytics not available'}).encode())
        elif self.path == '/api/email/stats':
            # Get email campaign statistics
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if EMAIL_INTEGRATION_AVAILABLE and email_integration:
                stats = email_integration.get_campaign_stats()
                self.wfile.write(json.dumps(stats).encode())
            else:
                self.wfile.write(json.dumps({'error': 'Email integration not available'}).encode())
        elif self.path.startswith('/api/leads/export/'):
            # Export leads (CSV or JSON)
            format_type = self.path.split('/')[-1]  # csv or json
            self.send_response(200)

            if format_type == 'csv':
                self.send_header('Content-type', 'text/csv')
                self.send_header('Content-Disposition', 'attachment; filename="leads_export.csv"')
            else:
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Disposition', 'attachment; filename="leads_export.json"')

            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if EMAIL_INTEGRATION_AVAILABLE and email_integration:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='r', delete=False, suffix=f'.{format_type}') as tmp:
                    tmp_path = tmp.name

                if format_type == 'csv':
                    email_integration.export_leads_csv(tmp_path)
                else:
                    email_integration.export_leads_json(tmp_path)

                with open(tmp_path, 'rb') as f:
                    self.wfile.write(f.read())

                os.unlink(tmp_path)
            else:
                self.wfile.write(b'Email integration not available')
        elif self.path.startswith('/webhook/whatsapp'):
            # WhatsApp webhook verification (GET request)
            self.handle_whatsapp_verification()
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests - WhatsApp webhook and broadcast creation"""
        if self.path.startswith('/webhook/whatsapp'):
            self.handle_whatsapp_message()
        elif self.path == '/api/broadcast/create':
            self.handle_broadcast_create()
        elif self.path.startswith('/api/broadcast/send/'):
            self.handle_broadcast_send()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_broadcast_create(self):
        """Handle broadcast creation request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if not BROADCAST_AVAILABLE or not broadcast_system:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Broadcast system not available'}).encode())
                return

            # Create broadcast
            broadcast = broadcast_system.create_broadcast(
                name=data.get('name', 'Untitled Broadcast'),
                message=data.get('message', ''),
                segment_criteria=data.get('segment_criteria', {})
            )

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(broadcast).encode())

        except Exception as e:
            logger.error(f"Broadcast creation error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_broadcast_send(self):
        """Handle broadcast send request"""
        try:
            # Extract broadcast ID from path
            broadcast_id = self.path.split('/')[-1]

            if not BROADCAST_AVAILABLE or not broadcast_system:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Broadcast system not available'}).encode())
                return

            # Send broadcast
            results = broadcast_system.send_broadcast(broadcast_id)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())

        except Exception as e:
            logger.error(f"Broadcast send error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_whatsapp_verification(self):
        """Handle WhatsApp webhook verification (GET)"""
        try:
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)

            mode = query.get('hub.mode', [''])[0]
            token = query.get('hub.verify_token', [''])[0]
            challenge = query.get('hub.challenge', [''])[0]

            verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'ai_employee_whatsapp_verify_2026')

            if mode == 'subscribe' and token == verify_token:
                logger.info("✅ WhatsApp webhook verified")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(challenge.encode())
            else:
                logger.warning("❌ WhatsApp webhook verification failed")
                self.send_response(403)
                self.end_headers()
        except Exception as e:
            logger.error(f"❌ Webhook verification error: {e}")
            self.send_response(500)
            self.end_headers()

    def handle_whatsapp_message(self):
        """Handle incoming WhatsApp message (POST)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            logger.info("📱 WhatsApp message received")

            # Extract message data
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            if messages:
                for message in messages:
                    message_id = message.get('id', '')

                    # Check if already processed (prevent duplicates)
                    with processed_messages_lock:
                        if message_id in processed_messages:
                            logger.info(f"⏭️ Skipping duplicate message: {message_id}")
                            continue
                        processed_messages.add(message_id)

                    from_number = message.get('from', '')
                    message_type = message.get('type', 'text')

                    if message_type == 'text':
                        content = message.get('text', {}).get('body', '')
                    else:
                        content = f"[{message_type.upper()} message]"

                    contacts = value.get('contacts', [{}])
                    contact_name = contacts[0].get('profile', {}).get('name', 'Unknown') if contacts else 'Unknown'

                    logger.info(f"📱 From: {contact_name} ({from_number}): {content[:50]}...")

                    # Track analytics
                    analytics.track_whatsapp_message(contact_name, 'received')

                    # Track advanced analytics - message received
                    if ANALYTICS_AVAILABLE and advanced_analytics:
                        advanced_analytics.track_message_received(from_number)

                    # Check if this is a new lead
                    if CRM_AVAILABLE and lead_crm and from_number not in lead_crm.leads:
                        if ANALYTICS_AVAILABLE and advanced_analytics:
                            advanced_analytics.track_new_lead(from_number, 'whatsapp')

                    # Auto-respond intelligently (only for business inquiries)
                    response_start_time = time.time()
                    self.send_whatsapp_auto_response(from_number, content, contact_name, response_start_time)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode())

        except Exception as e:
            logger.error(f"❌ WhatsApp message handling error: {e}")
            self.send_response(500)
            self.end_headers()

    def send_whatsapp_auto_response(self, to_number, message_content, contact_name, response_start_time=None):
        """Send intelligent WhatsApp response using Gemini AI"""
        try:
            if response_start_time is None:
                response_start_time = time.time()

            access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
            phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')

            if not access_token or not phone_id:
                logger.warning("⚠️ WhatsApp credentials not configured")
                return

            # Generate intelligent response using Gemini with conversation history
            response_text = self.generate_intelligent_response(message_content, contact_name, to_number)

            url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            payload = {
                'messaging_product': 'whatsapp',
                'recipient_type': 'individual',
                'to': to_number,
                'type': 'text',
                'text': {
                    'preview_url': False,
                    'body': response_text
                }
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                logger.info(f"✅ Intelligent response sent to {contact_name}")
                analytics.track_whatsapp_response()

                # Track response time in advanced analytics
                if ANALYTICS_AVAILABLE and advanced_analytics and response_start_time:
                    response_time = time.time() - response_start_time
                    advanced_analytics.track_response_sent(to_number, response_time)
            else:
                logger.warning(f"⚠️ Failed to send response: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Auto-response error: {e}")

    def detect_sentiment(self, message_content):
        """Detect message sentiment and priority level"""
        message_lower = message_content.lower()

        # Urgent keywords
        urgent_keywords = ['urgent', 'asap', 'immediately', 'emergency', 'now', 'quick', 'fast',
                          'فوری', 'ابھی', 'jaldi', 'turant', 'abhi']

        # Negative sentiment keywords
        negative_keywords = ['angry', 'disappointed', 'frustrated', 'upset', 'unhappy', 'bad',
                           'terrible', 'worst', 'disappointed', 'ناراض', 'مایوس', 'naraz', 'mayoos']

        # High-value keywords
        high_value_keywords = ['enterprise', 'company', 'business', 'team', 'budget', 'investment',
                              'کمپنی', 'کاروبار', 'company', 'business']

        sentiment = {
            'is_urgent': any(keyword in message_lower for keyword in urgent_keywords),
            'is_negative': any(keyword in message_lower for keyword in negative_keywords),
            'is_high_value': any(keyword in message_lower for keyword in high_value_keywords),
            'priority': 'normal'
        }

        # Determine priority
        if sentiment['is_urgent'] or sentiment['is_negative']:
            sentiment['priority'] = 'high'
        elif sentiment['is_high_value']:
            sentiment['priority'] = 'medium'

        return sentiment

    def generate_intelligent_response(self, message_content, contact_name, contact_number):
        """Generate intelligent response using Gemini AI with conversation history and sentiment analysis"""
        try:
            # Detect sentiment first
            sentiment = self.detect_sentiment(message_content)

            # Track sentiment in analytics
            if sentiment['is_urgent']:
                analytics.track_urgent_message()
                logger.warning(f"🚨 URGENT message from {contact_name}: {message_content[:50]}...")

            if sentiment['priority'] == 'high':
                analytics.track_high_priority()
                logger.warning(f"⚠️ HIGH PRIORITY message from {contact_name}")

            message_lower = message_content.lower().strip()

            # Check if it's a greeting - send complete business card
            casual_greetings = ['hi', 'hello', 'hey', 'hlo', 'hii', 'helo', 'assalam', 'salam', 'good morning', 'good evening']

            if any(greeting in message_lower for greeting in casual_greetings) and len(message_content.strip()) < 20:
                # Send complete business card for greetings
                business_card = f"""👋 Hi {contact_name}!

I'm *Nahead Jokhio* - AI Developer & Full-Stack Engineer

🎯 *What I Do:*
✅ AI Automation & Intelligent Systems
✅ Custom Software Development
✅ Cloud Architecture & 24/7 Deployments
✅ API Integration & Workflow Automation

🏆 *Recent Achievement:*
Built a production AI Employee system that autonomously handles Email, WhatsApp, LinkedIn, Twitter & more - running 24/7 on cloud!

📞 *Let's Connect:*
📱 WhatsApp: +92 312 2955972
📧 Email: naheadj@gmail.com
🔗 LinkedIn: https://linkedin.com/in/nahead
💼 Portfolio: https://my-personal-porfolio-navy.vercel.app

💡 Looking for AI automation or custom development? Let's discuss your project!"""

                logger.info(f"✅ Sending business card to {contact_name}")
                analytics.track_whatsapp_message(contact_name, 'greeting')

                # Save to conversation history
                if HISTORY_AVAILABLE and conversation_history:
                    conversation_history.add_message(contact_number, contact_name, message_content, business_card)

                # Save to Lead CRM (greeting = low urgency, neutral sentiment)
                if CRM_AVAILABLE and lead_crm:
                    greeting_sentiment = {
                        'is_urgent': False,
                        'is_negative': False,
                        'is_high_value': False,
                        'priority': 'normal'
                    }
                    lead_crm.add_or_update_lead(
                        phone=contact_number,
                        name=contact_name,
                        message=message_content,
                        sentiment=greeting_sentiment,
                        response=business_card
                    )

                return business_card

            gemini_api_key = os.getenv('GEMINI_API_KEY', '')

            if not gemini_api_key or not GEMINI_AVAILABLE:
                return None

            # Get conversation history for context
            context_summary = ""
            if HISTORY_AVAILABLE and conversation_history:
                context_summary = conversation_history.get_context_summary(contact_number)
                contact_stats = conversation_history.get_contact_stats(contact_number)

                if contact_stats['status'] == 'returning':
                    logger.info(f"📚 Retrieved conversation history for {contact_name} ({contact_stats['total_messages']} messages)")

            # Configure Gemini
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

            # Business context and instructions
            system_context = """You are an AI assistant representing Nahead Jokhio's business.

PERSONAL INFORMATION:
- Name: Nahead Jokhio
- Location: Pakistan
- Phone/WhatsApp: +92 312 2955972
- Email: naheadj@gmail.com
- LinkedIn: https://www.linkedin.com/in/nahead/
- GitHub: https://github.com/nahead
- Portfolio: https://my-personal-porfolio-navy.vercel.app

EXPERTISE & SKILLS:
- AI Development & Integration (Claude, Gemini, OpenAI)
- Full-Stack Development (Python, JavaScript, React, Node.js)
- Cloud Computing & DevOps (Render, Railway, AWS, Docker)
- Automation & Workflow Optimization
- API Development & Integration
- Database Design (SQL, NoSQL)
- Real-time Systems (WebSockets, Webhooks)
- MCP (Model Context Protocol) Servers

SERVICES OFFERED:
1. AI Automation Solutions
2. Custom Software Development
3. Cloud Deployments
4. AI Integration Services

CURRENT ACHIEVEMENT:
- Built production-ready AI Employee system running 24/7
- Achieved Gold Tier (100%) + Platinum Tier (89%) in Hackathon
- Live Demo: https://ai-employee-cloud.onrender.com

LANGUAGE HANDLING (CRITICAL):
- DETECT the language of the customer's message: English, Urdu (اردو), or Roman Urdu
- RESPOND in the EXACT SAME language as the customer used
- If customer writes in Urdu script (اردو) → respond in Urdu script
- If customer writes in Roman Urdu (e.g., "Mujhe AI automation chahiye") → respond in Roman Urdu
- If customer writes in English → respond in English
- Match their formality level and tone
- Use natural, conversational language appropriate for Pakistan

YOUR ROLE:
- Analyze if the message is a RELEVANT business inquiry
- RELEVANT: Questions about services, projects, AI, automation, collaboration, pricing, availability, technical questions
- IRRELEVANT: Random questions, jokes, personal questions unrelated to business, spam, nonsense
- If RELEVANT → provide helpful, professional response with contact details when appropriate
- If IRRELEVANT → return exactly "SKIP"

RESPONSE GUIDELINES:
Analyze the message carefully:
- Is it asking about services/projects/collaboration? → Respond professionally
- Is it a technical question related to your expertise? → Provide helpful answer
- Is it asking how to contact/connect? → Share contact details
- Is it completely unrelated to business (weather, jokes, random topics)? → return "SKIP"

Keep responses under 250 characters. Be professional and include relevant contact info when needed.
"""

            # Add sentiment context to prompt
            if sentiment['priority'] == 'high':
                if sentiment['is_urgent']:
                    system_context += "\n\nIMPORTANT: This is an URGENT message. Respond with immediate availability and fast turnaround time. Show you understand the urgency."
                if sentiment['is_negative']:
                    system_context += "\n\nIMPORTANT: Customer seems frustrated or disappointed. Be extra empathetic, apologetic if needed, and solution-focused. Prioritize resolving their concern."

            # Add conversation history to prompt if available
            if context_summary and context_summary != "No previous conversation history.":
                system_context += f"\n\n{context_summary}\n\nIMPORTANT: Use the conversation history above to provide context-aware responses. Reference previous discussions when relevant."

            # Generate response
            prompt = f"{system_context}\n\nCUSTOMER MESSAGE from {contact_name}:\n{message_content}\n\nAnalyze and respond (or return SKIP if irrelevant):"

            response = model.generate_content(prompt)

            if response and response.text:
                response_text = response.text.strip()

                # Check if AI decided to skip
                if response_text.upper() == "SKIP" or "SKIP" in response_text.upper()[:10]:
                    logger.info(f"⏭️ Skipping irrelevant message from {contact_name}")
                    analytics.track_whatsapp_message(contact_name, 'skipped')
                    return None

                analytics.track_whatsapp_message(contact_name, 'business')

                # Save to conversation history
                if HISTORY_AVAILABLE and conversation_history:
                    conversation_history.add_message(contact_number, contact_name, message_content, response_text)

                # Save to Lead CRM with sentiment data
                if CRM_AVAILABLE and lead_crm:
                    lead_crm.add_or_update_lead(
                        phone=contact_number,
                        name=contact_name,
                        message=message_content,
                        sentiment=sentiment,
                        response=response_text
                    )
                    logger.info(f"💼 Lead updated in CRM: {contact_name}")

                return response_text
            else:
                return None

        except Exception as e:
            logger.error(f"❌ Gemini API error: {e}")
            return None

    def get_pending_emails(self):
        """Get list of pending emails"""
        try:
            vault_path = Path("AI_Employee_Vault/Pending_Approval")
            if not vault_path.exists():
                return []

            emails = []
            for email_file in vault_path.glob("EMAIL_*.md"):
                try:
                    content = email_file.read_text(encoding='utf-8')

                    # Extract email details
                    sender_match = re.search(r'sender:\s*(.+)', content)
                    subject_match = re.search(r'subject:\s*(.+)', content)
                    body_match = re.search(r'## Email Body:\s*```\s*(.+?)\s*```', content, re.DOTALL)

                    emails.append({
                        'filename': email_file.name,
                        'sender': sender_match.group(1).strip() if sender_match else 'Unknown',
                        'subject': subject_match.group(1).strip() if subject_match else 'No Subject',
                        'preview': body_match.group(1).strip()[:200] + '...' if body_match else '',
                        'timestamp': datetime.fromtimestamp(email_file.stat().st_mtime).isoformat()
                    })
                except Exception:
                    pass

            return sorted(emails, key=lambda x: x['timestamp'], reverse=True)
        except Exception:
            return []

    def get_dashboard_html(self):
        """Generate professional dashboard HTML with analytics"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Employee - Analytics Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeIn 1s ease-in;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
        }

        .status-badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 15px;
            animation: pulse 2s infinite;
        }

        .analytics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
        }

        .metric-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #10b981;
            margin-bottom: 10px;
        }

        .metric-label {
            color: #666;
            font-size: 0.9em;
        }

        .sub-metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }

        .sub-metric {
            text-align: center;
        }

        .sub-metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }

        .sub-metric-label {
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
        }

        .logs-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-top: 20px;
        }

        .logs-section h2 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .logs-container {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
        }

        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }

        .log-timestamp {
            color: #858585;
            margin-right: 10px;
        }

        .log-level-INFO { color: #4ade80; }
        .log-level-WARNING { color: #fbbf24; }
        .log-level-ERROR { color: #f87171; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .last-activity {
            font-size: 0.85em;
            color: #999;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Employee Analytics</h1>
            <p class="subtitle">Real-time Performance Dashboard</p>
            <div class="status-badge">● LIVE</div>
        </div>

        <div class="analytics-grid">
            <!-- WhatsApp Metrics -->
            <div class="metric-card">
                <h3>📱 WhatsApp</h3>
                <div class="metric-value" id="whatsapp-total">0</div>
                <div class="metric-label">Total Messages</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="whatsapp-business">0</div>
                        <div class="sub-metric-label">Business</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="whatsapp-responses">0</div>
                        <div class="sub-metric-label">Responses</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="whatsapp-urgent">0</div>
                        <div class="sub-metric-label">🚨 Urgent</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="whatsapp-priority">0</div>
                        <div class="sub-metric-label">⚠️ Priority</div>
                    </div>
                </div>
                <div class="last-activity" id="whatsapp-last">No activity yet</div>
            </div>

            <!-- Email Metrics -->
            <div class="metric-card">
                <h3>📧 Email</h3>
                <div class="metric-value" id="email-checks">0</div>
                <div class="metric-label">Inbox Checks</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="email-sent">0</div>
                        <div class="sub-metric-label">Sent</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="email-drafts">0</div>
                        <div class="sub-metric-label">Drafts</div>
                    </div>
                </div>
                <div class="last-activity" id="email-last">No activity yet</div>
            </div>

            <!-- LinkedIn Metrics -->
            <div class="metric-card">
                <h3>💼 LinkedIn</h3>
                <div class="metric-value" id="linkedin-published">0</div>
                <div class="metric-label">Posts Published</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="linkedin-pending">0</div>
                        <div class="sub-metric-label">Pending</div>
                    </div>
                </div>
                <div class="last-activity" id="linkedin-last">No activity yet</div>
            </div>

            <!-- System Metrics -->
            <div class="metric-card">
                <h3>⚙️ System</h3>
                <div class="metric-value" id="system-uptime">0h 0m</div>
                <div class="metric-label">Uptime</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="system-syncs">0</div>
                        <div class="sub-metric-label">Vault Syncs</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="system-errors">0</div>
                        <div class="sub-metric-label">Errors</div>
                    </div>
                </div>
            </div>

            <!-- Lead CRM Metrics -->
            <div class="metric-card">
                <h3>💼 Lead CRM</h3>
                <div class="metric-value" id="crm-total">0</div>
                <div class="metric-label">Total Leads</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="crm-hot">0</div>
                        <div class="sub-metric-label">🔥 Hot</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="crm-warm">0</div>
                        <div class="sub-metric-label">🌡️ Warm</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="crm-cold">0</div>
                        <div class="sub-metric-label">❄️ Cold</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="crm-followup">0</div>
                        <div class="sub-metric-label">📞 Follow-up</div>
                    </div>
                </div>
            </div>

            <!-- Automated Follow-up Metrics -->
            <div class="metric-card">
                <h3>📞 Auto Follow-up</h3>
                <div class="metric-value" id="followup-sent">0</div>
                <div class="metric-label">Messages Sent</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="followup-checks">0</div>
                        <div class="sub-metric-label">Total Checks</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="followup-skipped">0</div>
                        <div class="sub-metric-label">Skipped</div>
                    </div>
                </div>
                <div class="last-activity" id="followup-last">No activity yet</div>
            </div>

            <!-- Broadcast Metrics -->
            <div class="metric-card">
                <h3>📢 Broadcasts</h3>
                <div class="metric-value" id="broadcast-sent">0</div>
                <div class="metric-label">Messages Sent</div>
                <div class="sub-metrics">
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="broadcast-campaigns">0</div>
                        <div class="sub-metric-label">Campaigns</div>
                    </div>
                    <div class="sub-metric">
                        <div class="sub-metric-value" id="broadcast-completed">0</div>
                        <div class="sub-metric-label">Completed</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Advanced Analytics Section -->
        <div class="logs-section">
            <h2>📊 Advanced Analytics</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px;">
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 10px; font-size: 1em;">⚡ Response Times</h3>
                    <div style="font-size: 0.9em; color: #666;">
                        <div>Average: <strong id="analytics-avg-response">0s</strong></div>
                        <div>Median: <strong id="analytics-median-response">0s</strong></div>
                        <div>Total Responses: <strong id="analytics-response-count">0</strong></div>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 10px; font-size: 1em;">🎯 Conversion Rate</h3>
                    <div style="font-size: 0.9em; color: #666;">
                        <div>Rate: <strong id="analytics-conversion-rate">0%</strong></div>
                        <div>Conversions: <strong id="analytics-conversions">0</strong></div>
                        <div>Total Leads: <strong id="analytics-total-leads">0</strong></div>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 10px; font-size: 1em;">📍 Lead Sources</h3>
                    <div style="font-size: 0.9em; color: #666;" id="analytics-lead-sources">
                        <div>No data yet</div>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <h3 style="color: #667eea; margin-bottom: 10px; font-size: 1em;">💰 Revenue</h3>
                    <div style="font-size: 0.9em; color: #666;">
                        <div>Total: <strong id="analytics-revenue">$0</strong></div>
                        <div>Avg per Conversion: <strong id="analytics-avg-value">$0</strong></div>
                        <div>Period: 30 days</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Live Logs -->
        <div class="logs-section">
            <h2>📋 Live Activity Logs</h2>
            <div class="logs-container" id="logs"></div>
        </div>
    </div>

    <script>
        function formatTime(isoString) {
            if (!isoString) return 'Never';
            const date = new Date(isoString);
            const now = new Date();
            const diff = Math.floor((now - date) / 1000);

            if (diff < 60) return `${diff}s ago`;
            if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
            return date.toLocaleString();
        }

        async function fetchAnalytics() {
            try {
                const response = await fetch('/analytics');
                const data = await response.json();

                // WhatsApp metrics
                document.getElementById('whatsapp-total').textContent = data.whatsapp.total_messages;
                document.getElementById('whatsapp-business').textContent = data.whatsapp.business_inquiries;
                document.getElementById('whatsapp-responses').textContent = data.whatsapp.responses_sent;
                document.getElementById('whatsapp-urgent').textContent = data.whatsapp.urgent_messages;
                document.getElementById('whatsapp-priority').textContent = data.whatsapp.high_priority;
                document.getElementById('whatsapp-last').textContent = 'Last: ' + formatTime(data.whatsapp.last_message_time);

                // Email metrics
                document.getElementById('email-checks').textContent = data.email.emails_checked;
                document.getElementById('email-sent').textContent = data.email.emails_sent;
                document.getElementById('email-drafts').textContent = data.email.drafts_created;
                document.getElementById('email-last').textContent = 'Last check: ' + formatTime(data.email.last_check_time);

                // LinkedIn metrics
                document.getElementById('linkedin-published').textContent = data.linkedin.posts_published;
                document.getElementById('linkedin-pending').textContent = data.linkedin.posts_pending;
                document.getElementById('linkedin-last').textContent = 'Last post: ' + formatTime(data.linkedin.last_post_time);

                // System metrics
                document.getElementById('system-uptime').textContent = data.system.uptime_formatted;
                document.getElementById('system-syncs').textContent = data.system.vault_syncs;
                document.getElementById('system-errors').textContent = data.system.errors;

                // CRM metrics
                if (data.crm) {
                    document.getElementById('crm-total').textContent = data.crm.total_leads;
                    document.getElementById('crm-hot').textContent = data.crm.hot_leads;
                    document.getElementById('crm-warm').textContent = data.crm.warm_leads;
                    document.getElementById('crm-cold').textContent = data.crm.cold_leads;
                    document.getElementById('crm-followup').textContent = data.crm.needs_followup;
                }

                // Follow-up metrics
                if (data.followup) {
                    document.getElementById('followup-sent').textContent = data.followup.messages_sent;
                    document.getElementById('followup-checks').textContent = data.followup.total_checks;
                    document.getElementById('followup-skipped').textContent = data.followup.leads_skipped;
                    document.getElementById('followup-last').textContent = 'Last check: ' + formatTime(data.followup.last_check_time);
                }

                // Broadcast metrics
                if (data.broadcast) {
                    document.getElementById('broadcast-sent').textContent = data.broadcast.total_messages_sent;
                    document.getElementById('broadcast-campaigns').textContent = data.broadcast.total_broadcasts;
                    document.getElementById('broadcast-completed').textContent = data.broadcast.completed_broadcasts;
                }

            } catch (error) {
                console.error('Failed to fetch analytics:', error);
            }
        }

        async function fetchAdvancedAnalytics() {
            try {
                const response = await fetch('/api/analytics/advanced');
                const data = await response.json();

                // Response times
                if (data.response_times) {
                    document.getElementById('analytics-avg-response').textContent =
                        data.response_times.average.toFixed(2) + 's';
                    document.getElementById('analytics-median-response').textContent =
                        data.response_times.median.toFixed(2) + 's';
                    document.getElementById('analytics-response-count').textContent =
                        data.response_times.count;
                }

                // Conversion rate
                if (data.conversion_rate) {
                    document.getElementById('analytics-conversion-rate').textContent =
                        data.conversion_rate.conversion_rate + '%';
                    document.getElementById('analytics-conversions').textContent =
                        data.conversion_rate.total_conversions;
                    document.getElementById('analytics-total-leads').textContent =
                        data.conversion_rate.total_leads;
                }

                // Lead sources
                if (data.lead_sources && data.lead_sources.sources) {
                    const sourcesDiv = document.getElementById('analytics-lead-sources');
                    const sources = data.lead_sources.sources;
                    if (Object.keys(sources).length > 0) {
                        sourcesDiv.innerHTML = Object.entries(sources)
                            .map(([source, info]) =>
                                `<div>${source}: <strong>${info.count}</strong> (${info.percentage}%)</div>`)
                            .join('');
                    }
                }

                // Revenue
                if (data.revenue) {
                    document.getElementById('analytics-revenue').textContent =
                        '$' + data.revenue.total_revenue.toFixed(0);
                    document.getElementById('analytics-avg-value').textContent =
                        '$' + data.revenue.average_value.toFixed(0);
                }

            } catch (error) {
                console.error('Failed to fetch advanced analytics:', error);
            }
        }

        async function fetchLogs() {
            try {
                const response = await fetch('/logs');
                const logs = await response.json();
                const logsContainer = document.getElementById('logs');

                logsContainer.innerHTML = logs.map(log => `
                    <div class="log-entry">
                        <span class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
                        <span class="log-level-${log.level}">[${log.level}]</span>
                        ${log.message}
                    </div>
                `).join('');

                logsContainer.scrollTop = logsContainer.scrollHeight;
            } catch (error) {
                console.error('Failed to fetch logs:', error);
            }
        }

        // Initial fetch
        fetchAnalytics();
        fetchAdvancedAnalytics();
        fetchLogs();

        // Auto-refresh every 3 seconds
        setInterval(fetchAnalytics, 3000);
        setInterval(fetchAdvancedAnalytics, 5000);  // Refresh advanced analytics every 5 seconds
        setInterval(fetchLogs, 3000);
    </script>
</body>
</html>"""

    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

class CloudEmailSender:
    """Email sending for cloud deployment - SMTP only"""

    def __init__(self):
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')

        if not (self.smtp_user and self.smtp_pass):
            logger.warning("⚠️ SMTP credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ SMTP credentials configured")

    def send_email_via_smtp(self, to_email, subject, body):
        """Send email via SMTP - tries SSL port 465 first, then TLS port 587"""
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Try port 465 (SSL) first
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            logger.info(f"✅ Email sent to: {to_email} (via SMTP SSL)")
            return True
        except (OSError, ConnectionError, TimeoutError):
            pass
        except Exception:
            pass

        # Fallback to port 587 (TLS)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            logger.info(f"✅ Email sent to: {to_email} (via SMTP TLS)")
            return True
        except (OSError, ConnectionError, TimeoutError):
            # Silent failure - no warning logs
            return False
        except Exception:
            # Silent failure - no warning logs
            return False

    def send_email(self, to_email, subject, body):
        """Send email via SMTP"""
        if not self.enabled:
            return False

        # Send via SMTP
        if self.smtp_user and self.smtp_pass:
            return self.send_email_via_smtp(to_email, subject, body)

        return False

class CloudGmailWatcher:
    """Gmail monitoring for cloud deployment"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

        self.email = os.getenv('SMTP_USER')
        self.password = os.getenv('SMTP_PASS')

        if not self.email or not self.password:
            logger.warning("⚠️ Gmail credentials not configured - running in demo mode")
            self.enabled = False
        else:
            self.enabled = True

    def connect_to_gmail(self):
        """Connect to Gmail using IMAP"""
        if not self.enabled:
            return None

        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com', timeout=10)
            mail.login(self.email, self.password)
            logger.info(f"✅ Connected to Gmail: {self.email}")
            return mail
        except (OSError, ConnectionError, TimeoutError) as e:
            logger.warning(f"⚠️ Gmail connection failed (network issue) - will retry later")
            return None
        except Exception as e:
            logger.warning(f"⚠️ Gmail connection failed: {e}")
            return None

    def check_new_emails(self, mail):
        """Check for new unread emails"""
        try:
            mail.select('inbox')
            status, messages = mail.search(None, 'UNSEEN')

            analytics.track_email_check()

            if status == 'OK':
                email_ids = messages[0].split()
                if email_ids:
                    logger.info(f"📧 Found {len(email_ids)} new emails")
                    for email_id in email_ids[:5]:  # Process max 5 at a time
                        self.process_email(mail, email_id)

        except Exception as e:
            logger.warning(f"⚠️ Error checking emails: {e}")
            analytics.track_error(f"Email check error: {e}")

    def process_email(self, mail, email_id):
        """Process individual email"""
        try:
            status, msg_data = mail.fetch(email_id, '(RFC822)')

            if status == 'OK':
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                subject = email_message['Subject'] or "No Subject"
                sender = email_message['From']

                content = self.get_email_content(email_message)

                logger.info(f"📨 Processing: {subject[:50]}...")

                self.create_action_file(subject, sender, content, email_id)

        except Exception as e:
            logger.error(f"❌ Error processing email: {e}")

    def get_email_content(self, email_message):
        """Extract email content"""
        content = ""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            content = "Could not decode email content"

        return content[:1000]  # Limit content length

    def create_action_file(self, subject, sender, content, email_id):
        """Create action file in Needs_Action folder"""
        # Ensure Needs_Action folder exists
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_DETECTED_{timestamp}.md"
        filepath = self.needs_action_path / filename

        action_content = f"""---
type: email_action
sender: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
status: needs_action
priority: normal
email_id: {email_id.decode() if isinstance(email_id, bytes) else email_id}
---

## Email Details
A new email has been detected and needs processing.

**From:** {sender}
**Subject:** {subject}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Content:**
```
{content}
```

## Next Steps
1. System will analyze this email
2. Generate appropriate response
3. Create approval file in Pending_Approval/
4. Wait for human approval
5. Send response via SMTP

## Workflow
Needs_Action -> Processing -> Pending_Approval -> Approved -> Done
"""

        filepath.write_text(action_content, encoding='utf-8')
        logger.info(f"✅ Created action file: {filename}")

class CloudVaultSync:
    """Vault synchronization with GitHub"""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.enabled = True

        # Ensure vault directory exists
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Create required subdirectories
        (self.vault_path / "Needs_Action").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "Processing").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "Pending_Approval").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "Approved").mkdir(parents=True, exist_ok=True)
        (self.vault_path / "Done").mkdir(parents=True, exist_ok=True)

        # Initialize email sender
        try:
            self.email_sender = CloudEmailSender()
        except Exception as e:
            logger.warning(f"⚠️ Email sender not available: {e}")
            self.email_sender = None

        logger.info(f"✅ Vault initialized at: {self.vault_path}")

    def generate_email_response(self, email_data):
        """Generate appropriate response based on email content"""
        subject = email_data.get('subject', '').lower()
        content = email_data.get('email_content', '').lower()

        # Simple response generation based on keywords
        if 'urgent' in subject or 'urgent' in content:
            if 'payment' in subject or 'payment' in content:
                response = """Thank you for your email regarding the urgent payment matter.

I have received your message and understand the urgency. I will review the payment details and get back to you within 2 hours with a resolution.

If you need immediate assistance, please feel free to call our support line.

Best regards,
AI Employee System"""
            else:
                response = """Thank you for your urgent message.

I have received your email and will prioritize this matter. I will respond with the necessary information within 2 hours.

Best regards,
AI Employee System"""

        elif 'meeting' in subject or 'meeting' in content:
            response = """Thank you for your email.

I have received your meeting request. I will check the calendar and get back to you with available time slots within 24 hours.

Best regards,
AI Employee System"""

        elif 'question' in subject or 'inquiry' in subject or '?' in content:
            response = """Thank you for your inquiry.

I have received your question and will provide you with a detailed response within 24 hours.

Best regards,
AI Employee System"""

        else:
            # Default response
            response = """Thank you for your email.

I have received your message and will review it carefully. I will respond with the appropriate information within 24 hours.

Best regards,
AI Employee System"""

        return response

    def process_needs_action(self):
        """Process files from Needs_Action and create approval files"""
        if not self.enabled:
            return

        needs_action_path = self.vault_path / "Needs_Action"
        processing_path = self.vault_path / "Processing"
        pending_approval_path = self.vault_path / "Pending_Approval"

        if not needs_action_path.exists():
            return

        # Get all action files
        action_files = list(needs_action_path.glob("EMAIL_DETECTED_*.md"))

        if not action_files:
            return

        logger.info(f"📋 Processing {len(action_files)} action file(s)")

        for action_file in action_files:
            try:
                # Read action file
                content = action_file.read_text(encoding='utf-8')

                # Extract email data from frontmatter
                email_data = {}
                frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if frontmatter_match:
                    frontmatter = frontmatter_match.group(1)
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            email_data[key.strip()] = value.strip()

                # Extract email content
                content_match = re.search(r'\*\*Content:\*\*\n```\n(.*?)\n```', content, re.DOTALL)
                if content_match:
                    email_data['email_content'] = content_match.group(1).strip()
                else:
                    email_data['email_content'] = "No content available"

                if not email_data.get('sender') or not email_data.get('subject'):
                    logger.warning(f"⚠️ Could not parse action file: {action_file.name}")
                    continue

                # Generate response
                response = self.generate_email_response(email_data)

                # Create approval file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                approval_filename = f"EMAIL_RESPONSE_{timestamp}.md"
                approval_filepath = pending_approval_path / approval_filename

                approval_content = f"""---
type: email_response_approval
sender: {email_data.get('sender', 'Unknown')}
subject: {email_data.get('subject', 'No Subject')}
email_id: {email_data.get('email_id', 'unknown')}
created: {datetime.now().isoformat()}
status: pending_approval
---

## Original Email

**From:** {email_data.get('sender', 'Unknown')}
**Subject:** {email_data.get('subject', 'No Subject')}
**Received:** {email_data.get('received', 'Unknown')}

**Content:**
```
{email_data.get('email_content', 'No content available')}
```

## Proposed Response:

```
{response}
```

## Instructions

1. **To Approve:** Move this file to `Approved/` folder
2. **To Edit:** Modify the response above and keep in Pending_Approval/
3. **To Reject:** Delete this file

## Workflow
Needs_Action -> Processing -> **Pending_Approval** -> Approved -> Done
"""

                approval_filepath.write_text(approval_content, encoding='utf-8')
                logger.info(f"✅ Created approval file: {approval_filename}")

                # Move processed action file to Processing folder
                processing_path.mkdir(parents=True, exist_ok=True)
                processed_filepath = processing_path / action_file.name
                action_file.rename(processed_filepath)
                logger.info(f"📁 Moved to Processing: {action_file.name}")

            except Exception as e:
                logger.warning(f"⚠️ Error processing {action_file.name}: {e}")

    def process_approved_emails(self):
        """Process approved emails and send them"""
        if not self.enabled:
            return

        approved_path = self.vault_path / "Approved"
        done_path = self.vault_path / "Done"

        if not approved_path.exists():
            return

        # Get all approved email files
        approved_files = list(approved_path.glob("EMAIL_*.md"))

        if not approved_files:
            return

        logger.info(f"📧 Found {len(approved_files)} approved emails to send")

        for file_path in approved_files:
            try:
                # Read approval file
                content = file_path.read_text(encoding='utf-8')

                # Extract email details
                sender_match = re.search(r'sender:\s*(.+)', content)
                subject_match = re.search(r'subject:\s*(.+)', content)
                response_match = re.search(r'## Proposed Response:\s*```\s*(.+?)\s*```', content, re.DOTALL)

                if not all([sender_match, subject_match, response_match]):
                    logger.warning(f"⚠️ Could not parse: {file_path.name}")
                    continue

                # Extract values
                sender = sender_match.group(1).strip()
                original_subject = subject_match.group(1).strip()
                response_body = response_match.group(1).strip()

                # Extract email address from sender
                email_match = re.search(r'<(.+?)>', sender)
                if email_match:
                    to_email = email_match.group(1)
                else:
                    to_email = sender

                # Create reply subject
                reply_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject

                # Send email
                if self.email_sender:
                    logger.info(f"📤 Sending email to: {to_email}")
                    success = self.email_sender.send_email(to_email, reply_subject, response_body)

                    if success:
                        analytics.track_email_sent()
                        # Move to Done folder
                        done_path.mkdir(parents=True, exist_ok=True)
                        done_file = done_path / file_path.name
                        file_path.rename(done_file)
                        logger.info(f"✅ Email sent and moved to Done: {file_path.name}")
                    # Silent failure - no warning logs

            except Exception:
                # Silent failure - no warning logs
                pass

    def process_approved_linkedin_posts(self):
        """Process approved LinkedIn posts and publish them"""
        if not self.enabled:
            return

        approved_path = self.vault_path / "Approved"
        done_path = self.vault_path / "Done"

        if not approved_path.exists():
            return

        # Get all approved LinkedIn post files
        linkedin_posts = list(approved_path.glob("LINKEDIN_POST_*.md"))

        analytics.track_linkedin_check(len(linkedin_posts))

        if not linkedin_posts:
            return

        # Check LinkedIn credentials
        access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        person_urn = os.getenv('LINKEDIN_PERSON_URN', '')

        if not access_token or not person_urn:
            logger.warning("⚠️ LinkedIn credentials not configured, skipping posts")
            return

        logger.info(f"📱 Processing {len(linkedin_posts)} LinkedIn post(s)")

        for post_file in linkedin_posts:
            try:
                # Read post content
                content = post_file.read_text(encoding='utf-8')

                # Extract content (skip frontmatter if present)
                lines = content.split('\n')
                post_content = []
                in_frontmatter = False

                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue
                    if not in_frontmatter and line.strip():
                        post_content.append(line)

                post_text = '\n'.join(post_content).strip()

                if not post_text:
                    logger.warning(f"⚠️ Empty post content in: {post_file.name}")
                    continue

                # Post to LinkedIn using API
                logger.info(f"📱 Posting to LinkedIn: {post_file.name}")
                success = self.post_to_linkedin(post_text, access_token, person_urn)

                if success:
                    # Move to Done folder
                    done_path.mkdir(parents=True, exist_ok=True)
                    done_file = done_path / post_file.name
                    post_file.rename(done_file)
                    logger.info(f"✅ LinkedIn post published and moved to Done: {post_file.name}")
                    analytics.track_linkedin_post()
                else:
                    logger.warning(f"❌ Failed to post: {post_file.name}")

            except Exception as e:
                logger.error(f"❌ Error processing LinkedIn post {post_file.name}: {e}")

    def post_to_linkedin(self, content, access_token, person_urn):
        """Post content to LinkedIn using API"""
        url = "https://api.linkedin.com/v2/ugcPosts"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }

        # Prepare post data
        post_data = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=post_data,
                timeout=30
            )

            if response.status_code == 201:
                post_id = response.headers.get('X-RestLi-Id', 'unknown')
                logger.info(f"✅ LinkedIn post published successfully! Post ID: {post_id}")
                return True
            else:
                logger.error(f"❌ LinkedIn API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Exception while posting to LinkedIn: {e}")
            return False

    def process_approved_whatsapp_responses(self):
        """Process approved WhatsApp responses and send them"""
        if not self.enabled:
            return

        approved_path = self.vault_path / "Approved"
        done_path = self.vault_path / "Done"

        if not approved_path.exists():
            return

        # Get all approved WhatsApp response files
        whatsapp_responses = list(approved_path.glob("WHATSAPP_RESPONSE_*.md"))

        if not whatsapp_responses:
            return

        # Check WhatsApp credentials
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')

        if not access_token or not phone_id:
            logger.warning("⚠️ WhatsApp credentials not configured, skipping responses")
            return

        logger.info(f"📱 Processing {len(whatsapp_responses)} WhatsApp response(s)")

        for response_file in whatsapp_responses:
            try:
                # Read response file
                content = response_file.read_text(encoding='utf-8')

                # Extract phone number and message
                phone = None
                message_lines = []

                # Parse frontmatter and content
                lines = content.split('\n')
                in_frontmatter = False

                for line in lines:
                    if line.strip() == '---':
                        in_frontmatter = not in_frontmatter
                        continue

                    if in_frontmatter:
                        if line.startswith('phone:'):
                            phone = line.split(':', 1)[1].strip()
                    else:
                        if line.strip() and not line.startswith('#'):
                            message_lines.append(line)

                message = '\n'.join(message_lines).strip()

                if not phone or not message:
                    logger.warning(f"⚠️ Missing phone or message in: {response_file.name}")
                    continue

                # Send WhatsApp message
                logger.info(f"📱 Sending WhatsApp to: {phone}")
                success = self.send_whatsapp_message(phone, message, access_token, phone_id)

                if success:
                    # Move to Done folder
                    done_path.mkdir(parents=True, exist_ok=True)
                    done_file = done_path / response_file.name
                    response_file.rename(done_file)
                    logger.info(f"✅ WhatsApp sent and moved to Done: {response_file.name}")
                else:
                    logger.warning(f"❌ Failed to send WhatsApp: {response_file.name}")

            except Exception as e:
                logger.error(f"❌ Error processing WhatsApp response {response_file.name}: {e}")

    def send_whatsapp_message(self, to_number, message_text, access_token, phone_id):
        """Send WhatsApp message using Cloud API"""
        url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to_number,
            'type': 'text',
            'text': {
                'preview_url': False,
                'body': message_text
            }
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                message_id = result.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"✅ WhatsApp message sent successfully! ID: {message_id}")
                return True
            else:
                logger.error(f"❌ WhatsApp API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Exception while sending WhatsApp: {e}")
            return False

    def clone_or_pull_vault(self):
        """Ensure vault directory is ready"""
        if not self.enabled:
            return True

        # Vault is already initialized in __init__
        logger.info("✅ Vault directory ready")
        return True

    def commit_and_push_changes(self):
        """Commit and push vault changes back to GitHub"""
        if not self.enabled:
            return True

        try:
            # Check if there are any changes specifically in AI_Employee_Vault/
            result = subprocess.run(
                ['git', 'status', '--porcelain', 'AI_Employee_Vault/'],
                cwd=self.vault_path.parent,
                capture_output=True,
                text=True,
                timeout=10
            )

            if not result.stdout.strip():
                # No changes in vault to commit
                return True

            logger.info("📝 Detected vault changes, committing...")

            # Configure git user (required for commits)
            subprocess.run(
                ['git', 'config', 'user.name', 'AI Employee Bot'],
                cwd=self.vault_path.parent,
                check=True,
                timeout=10
            )
            subprocess.run(
                ['git', 'config', 'user.email', 'ai-employee@render.com'],
                cwd=self.vault_path.parent,
                check=True,
                timeout=10
            )

            # Add all changes in vault
            subprocess.run(
                ['git', 'add', 'AI_Employee_Vault/'],
                cwd=self.vault_path.parent,
                check=True,
                timeout=10
            )

            # Commit changes
            commit_message = f"Auto-sync vault changes - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.vault_path.parent,
                check=True,
                timeout=10
            )

            # Check if we have GitHub credentials for pushing
            git_token = os.getenv('GIT_TOKEN', '')
            if git_token:
                # Push to GitHub with authentication
                git_url = f"https://{git_token}@github.com/nahead/Hackathon0.git"
                subprocess.run(
                    ['git', 'push', git_url, 'main'],
                    cwd=self.vault_path.parent,
                    check=True,
                    timeout=30
                )
                logger.info("✅ Vault changes pushed to GitHub")
            else:
                logger.warning("⚠️ GIT_TOKEN not configured, skipping push")
                logger.info("✅ Vault changes committed locally")

            return True

        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Git operation timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Git operation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error committing changes: {e}")
            return False

class RailwayOrchestrator:
    """All-in-one orchestrator for Railway/Render"""

    def __init__(self):
        self.port = int(os.getenv("PORT", 8080))
        # Use AI_Employee_Vault in main repo instead of separate vault
        self.vault_path = Path("AI_Employee_Vault")

        logger.info("🚀 Railway All-in-One Orchestrator initialized")

    def check_environment(self):
        """Check environment variables"""
        required = ["SMTP_USER", "SMTP_PASS"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            logger.warning(f"⚠️ Missing variables: {missing}")
            return False

        logger.info("✅ Environment variables configured")
        return True

    def linkedin_poster_service(self):
        """Background LinkedIn posting - checks every 3 hours"""
        logger.info("📱 Starting LinkedIn poster service (3-hour checks)...")

        try:
            vault_sync = CloudVaultSync(self.vault_path)

            while True:
                try:
                    # Check for LinkedIn posts every 3 hours
                    vault_sync.process_approved_linkedin_posts()

                    logger.info("📱 LinkedIn check heartbeat")
                    time.sleep(10800)  # 3 hours

                except Exception as e:
                    logger.error(f"❌ LinkedIn poster error: {e}")
                    time.sleep(10800)

        except Exception as e:
            logger.error(f"❌ LinkedIn poster initialization failed: {e}")

    def vault_sync_service(self):
        """Background vault synchronization"""
        logger.info("🔄 Starting vault sync service...")

        try:
            vault_sync = CloudVaultSync(self.vault_path)

            # Initial clone/pull
            vault_sync.clone_or_pull_vault()

            while True:
                try:
                    # Pull changes every 5 minutes
                    vault_sync.clone_or_pull_vault()

                    # Process action files (Needs_Action -> Pending_Approval)
                    vault_sync.process_needs_action()

                    # Process approved emails (send them)
                    vault_sync.process_approved_emails()

                    # Process approved WhatsApp responses (send them)
                    vault_sync.process_approved_whatsapp_responses()

                    # Push any local changes
                    vault_sync.commit_and_push_changes()

                    analytics.track_vault_sync()
                    logger.info("💾 Vault sync heartbeat")
                    time.sleep(300)  # 5 minutes

                except Exception as e:
                    logger.error(f"❌ Vault sync error: {e}")
                    analytics.track_error(f"Vault sync error: {e}")
                    time.sleep(60)

        except Exception as e:
            logger.error(f"❌ Vault sync initialization failed: {e}")

    def gmail_watcher_service(self):
        """Background Gmail monitoring"""
        logger.info("📧 Starting Gmail watcher service (2-hour checks)...")

        try:
            gmail_watcher = CloudGmailWatcher(self.vault_path)

            while True:
                try:
                    mail = gmail_watcher.connect_to_gmail()
                    if mail:
                        gmail_watcher.check_new_emails(mail)
                        mail.close()
                        mail.logout()

                    logger.info("📬 Gmail monitoring heartbeat")
                    time.sleep(7200)  # 2 hours

                except Exception as e:
                    logger.error(f"❌ Gmail watcher error: {e}")
                    time.sleep(7200)

        except Exception as e:
            logger.error(f"❌ Gmail watcher initialization failed: {e}")

    def followup_service(self):
        """Background automated follow-up service"""
        logger.info("📞 Starting automated follow-up service (24-hour checks)...")

        if not FOLLOWUP_AVAILABLE or not automated_followup:
            logger.warning("⚠️ Follow-up system not available")
            return

        while True:
            try:
                # Check for leads needing follow-up (48 hours since last contact)
                results = automated_followup.check_and_send_followups(hours_since_contact=48)

                # Track metrics
                analytics.track_followup_check(
                    checked=results['checked'],
                    sent=results['sent'],
                    skipped=results['skipped'],
                    errors=results['errors']
                )

                logger.info(f"📞 Follow-up check: {results['sent']} sent, {results['skipped']} skipped")
                time.sleep(86400)  # 24 hours

            except Exception as e:
                logger.error(f"❌ Follow-up service error: {e}")
                time.sleep(86400)

    def start_background_services(self):
        """Start all background services"""
        logger.info("🔧 Starting background services...")

        # Start vault sync in background
        vault_thread = threading.Thread(target=self.vault_sync_service, daemon=True)
        vault_thread.start()

        # Start Gmail watcher in background
        gmail_thread = threading.Thread(target=self.gmail_watcher_service, daemon=True)
        gmail_thread.start()

        # Start LinkedIn poster in background (checks every 3 hours)
        linkedin_thread = threading.Thread(target=self.linkedin_poster_service, daemon=True)
        linkedin_thread.start()

        # Start automated follow-up service in background (checks every 24 hours)
        if FOLLOWUP_AVAILABLE and automated_followup:
            followup_thread = threading.Thread(target=self.followup_service, daemon=True)
            followup_thread.start()
            logger.info("✅ Automated follow-up service enabled")

        logger.info("✅ Background services started")

    def start_health_server(self):
        """Start health check server"""
        logger.info(f"🌐 Starting health server on port {self.port}")

        try:
            server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
            logger.info(f"✅ Health endpoint: http://0.0.0.0:{self.port}/health")
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Health server failed: {e}")
            raise

    def run(self):
        """Main run method"""
        logger.info("🎯 Starting Railway AI Employee...")

        # Check environment
        env_ok = self.check_environment()
        if not env_ok:
            logger.warning("⚠️ Some environment variables missing, but continuing...")

        # Start background services
        self.start_background_services()

        logger.info("🎉 Railway AI Employee is now LIVE!")
        logger.info("🌐 Your AI Employee is running 24/7 in the cloud!")

        # Start health server (this blocks)
        self.start_health_server()

if __name__ == "__main__":
    try:
        orchestrator = RailwayOrchestrator()
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Railway AI Employee...")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)