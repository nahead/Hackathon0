#!/usr/bin/env node

/**
 * Email MCP Server for AI Employee
 * Provides email sending and management capabilities via Model Context Protocol
 */

import { Server } from '@anthropic/mcp-server';
import nodemailer from 'nodemailer';
import Joi from 'joi';
import dotenv from 'dotenv';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class EmailMCPServer {
    constructor() {
        this.server = new Server({
            name: 'ai-employee-email',
            version: '1.0.0',
            description: 'Email server for AI Employee automation'
        });

        this.transporter = null;
        this.emailTemplates = this.loadEmailTemplates();
        this.sentEmails = [];
        this.setupTransporter();
        this.setupHandlers();
    }

    setupTransporter() {
        const config = {
            host: process.env.SMTP_HOST || 'smtp.gmail.com',
            port: parseInt(process.env.SMTP_PORT) || 587,
            secure: false,
            auth: {
                user: process.env.SMTP_USER,
                pass: process.env.SMTP_PASS
            }
        };

        this.transporter = nodemailer.createTransporter(config);

        // Verify connection
        this.transporter.verify((error, success) => {
            if (error) {
                console.error('SMTP connection failed:', error);
            } else {
                console.log('✅ Email server ready');
            }
        });
    }

    loadEmailTemplates() {
        const templatesPath = join(__dirname, 'templates.json');

        if (existsSync(templatesPath)) {
            try {
                return JSON.parse(readFileSync(templatesPath, 'utf8'));
            } catch (error) {
                console.error('Error loading email templates:', error);
            }
        }

        // Default templates
        return {
            business_reply: {
                subject: "Re: {original_subject}",
                body: `Dear {recipient_name},

Thank you for your message regarding {topic}.

{response_content}

Best regards,
{sender_name}
{company_name}

---
This email was sent with AI assistance.`
            },
            invoice_follow_up: {
                subject: "Invoice Follow-up: {invoice_number}",
                body: `Dear {client_name},

I hope this email finds you well. I wanted to follow up regarding invoice {invoice_number} dated {invoice_date}.

{follow_up_message}

Please let me know if you have any questions or if there's anything I can help clarify.

Best regards,
{sender_name}
{company_name}

Invoice Details:
- Invoice Number: {invoice_number}
- Amount: {amount}
- Due Date: {due_date}`
            },
            meeting_confirmation: {
                subject: "Meeting Confirmation: {meeting_topic}",
                body: `Dear {attendee_name},

This email confirms our meeting scheduled for:

📅 Date: {meeting_date}
🕐 Time: {meeting_time}
📍 Location: {meeting_location}
📋 Topic: {meeting_topic}

{additional_details}

Please let me know if you need to reschedule or have any questions.

Best regards,
{sender_name}`
            }
        };
    }

    setupHandlers() {
        // List available tools
        this.server.setRequestHandler('tools/list', async () => ({
            tools: [
                {
                    name: 'send_email',
                    description: 'Send an email with specified content',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            to: { type: 'string', description: 'Recipient email address' },
                            subject: { type: 'string', description: 'Email subject' },
                            body: { type: 'string', description: 'Email body content' },
                            template: { type: 'string', description: 'Optional template name' },
                            template_vars: { type: 'object', description: 'Variables for template' },
                            cc: { type: 'string', description: 'CC recipients (optional)' },
                            bcc: { type: 'string', description: 'BCC recipients (optional)' }
                        },
                        required: ['to', 'subject', 'body']
                    }
                },
                {
                    name: 'draft_email',
                    description: 'Create an email draft for approval',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            to: { type: 'string', description: 'Recipient email address' },
                            subject: { type: 'string', description: 'Email subject' },
                            body: { type: 'string', description: 'Email body content' },
                            template: { type: 'string', description: 'Optional template name' },
                            template_vars: { type: 'object', description: 'Variables for template' },
                            priority: { type: 'string', enum: ['low', 'normal', 'high'], default: 'normal' }
                        },
                        required: ['to', 'subject', 'body']
                    }
                },
                {
                    name: 'list_templates',
                    description: 'List available email templates',
                    inputSchema: {
                        type: 'object',
                        properties: {}
                    }
                },
                {
                    name: 'get_sent_emails',
                    description: 'Get list of recently sent emails',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            limit: { type: 'number', default: 10, description: 'Number of emails to return' }
                        }
                    }
                }
            ]
        }));

        // Handle tool calls
        this.server.setRequestHandler('tools/call', async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case 'send_email':
                        return await this.sendEmail(args);
                    case 'draft_email':
                        return await this.draftEmail(args);
                    case 'list_templates':
                        return await this.listTemplates();
                    case 'get_sent_emails':
                        return await this.getSentEmails(args);
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [{
                        type: 'text',
                        text: `Error: ${error.message}`
                    }],
                    isError: true
                };
            }
        });
    }

    async sendEmail(args) {
        // Validate input
        const schema = Joi.object({
            to: Joi.string().email().required(),
            subject: Joi.string().required(),
            body: Joi.string().required(),
            template: Joi.string().optional(),
            template_vars: Joi.object().optional(),
            cc: Joi.string().email().optional(),
            bcc: Joi.string().email().optional()
        });

        const { error, value } = schema.validate(args);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        let { to, subject, body, template, template_vars, cc, bcc } = value;

        // Apply template if specified
        if (template && this.emailTemplates[template]) {
            const templateData = this.emailTemplates[template];
            subject = this.applyTemplate(templateData.subject, template_vars || {});
            body = this.applyTemplate(templateData.body, template_vars || {});
        }

        // Prepare email options
        const mailOptions = {
            from: process.env.SMTP_USER,
            to,
            subject,
            text: body,
            html: this.convertToHtml(body)
        };

        if (cc) mailOptions.cc = cc;
        if (bcc) mailOptions.bcc = bcc;

        // Send email
        const info = await this.transporter.sendMail(mailOptions);

        // Log sent email
        const emailLog = {
            id: info.messageId,
            to,
            subject,
            timestamp: new Date().toISOString(),
            status: 'sent'
        };

        this.sentEmails.unshift(emailLog);
        this.saveSentEmailsLog();

        return {
            content: [{
                type: 'text',
                text: `✅ Email sent successfully!\n\nTo: ${to}\nSubject: ${subject}\nMessage ID: ${info.messageId}`
            }]
        };
    }

    async draftEmail(args) {
        // Validate input
        const schema = Joi.object({
            to: Joi.string().email().required(),
            subject: Joi.string().required(),
            body: Joi.string().required(),
            template: Joi.string().optional(),
            template_vars: Joi.object().optional(),
            priority: Joi.string().valid('low', 'normal', 'high').default('normal')
        });

        const { error, value } = schema.validate(args);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        let { to, subject, body, template, template_vars, priority } = value;

        // Apply template if specified
        if (template && this.emailTemplates[template]) {
            const templateData = this.emailTemplates[template];
            subject = this.applyTemplate(templateData.subject, template_vars || {});
            body = this.applyTemplate(templateData.body, template_vars || {});
        }

        // Create draft file for approval
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const draftId = `EMAIL_DRAFT_${timestamp}`;

        const draftContent = `---
type: approval_request
action: send_email
priority: ${priority}
created: ${new Date().toISOString()}
expires: ${new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()}
status: pending
---

# Email Draft Approval Request

## Email Details
- **To**: ${to}
- **Subject**: ${subject}
- **Priority**: ${priority.toUpperCase()}

## Email Content
\`\`\`
${body}
\`\`\`

## Actions
- **To Approve**: Move this file to /Approved folder
- **To Reject**: Move this file to /Rejected folder

## MCP Command (for approved execution)
\`\`\`json
{
  "tool": "send_email",
  "args": {
    "to": "${to}",
    "subject": "${subject}",
    "body": ${JSON.stringify(body)}
  }
}
\`\`\`

---
*Created by Email MCP Server*
`;

        // Save draft to Pending_Approval folder
        const vaultPath = process.env.VAULT_PATH || '../AI_Employee_Vault';
        const draftPath = join(vaultPath, 'Pending_Approval', `${draftId}.md`);

        try {
            writeFileSync(draftPath, draftContent, 'utf8');
        } catch (error) {
            console.error('Error saving draft:', error);
            throw new Error('Failed to save email draft for approval');
        }

        return {
            content: [{
                type: 'text',
                text: `📝 Email draft created for approval!\n\nDraft ID: ${draftId}\nTo: ${to}\nSubject: ${subject}\n\n⚠️ Approval required before sending (per Company Handbook)`
            }]
        };
    }

    async listTemplates() {
        const templates = Object.keys(this.emailTemplates).map(name => ({
            name,
            description: this.getTemplateDescription(name)
        }));

        return {
            content: [{
                type: 'text',
                text: `📧 Available Email Templates:\n\n${templates.map(t => `• ${t.name}: ${t.description}`).join('\n')}`
            }]
        };
    }

    async getSentEmails(args = {}) {
        const limit = args.limit || 10;
        const recentEmails = this.sentEmails.slice(0, limit);

        const emailList = recentEmails.map(email =>
            `• ${email.timestamp} - To: ${email.to} - Subject: ${email.subject}`
        ).join('\n');

        return {
            content: [{
                type: 'text',
                text: `📨 Recent Sent Emails (${recentEmails.length}):\n\n${emailList || 'No emails sent yet'}`
            }]
        };
    }

    applyTemplate(template, vars) {
        let result = template;
        for (const [key, value] of Object.entries(vars)) {
            result = result.replace(new RegExp(`{${key}}`, 'g'), value);
        }
        return result;
    }

    convertToHtml(text) {
        return text
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }

    getTemplateDescription(name) {
        const descriptions = {
            business_reply: 'Professional business email reply',
            invoice_follow_up: 'Follow up on unpaid invoices',
            meeting_confirmation: 'Confirm meeting details'
        };
        return descriptions[name] || 'Email template';
    }

    saveSentEmailsLog() {
        try {
            const logPath = join(__dirname, 'sent_emails.json');
            writeFileSync(logPath, JSON.stringify(this.sentEmails, null, 2));
        } catch (error) {
            console.error('Error saving sent emails log:', error);
        }
    }

    async start() {
        const transport = process.stdio;
        await this.server.connect(transport);
        console.log('🚀 Email MCP Server started');
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new EmailMCPServer();
    server.start().catch(console.error);
}

export default EmailMCPServer;