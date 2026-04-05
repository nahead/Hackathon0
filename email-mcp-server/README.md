# Email MCP Server
# Model Context Protocol server for email actions

## Description
MCP server that provides email sending capabilities for Claude Code to use as external actions.

## Implementation

```javascript
// email-mcp-server/server.js
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const nodemailer = require('nodemailer');
const fs = require('fs').promises;
const path = require('path');

class EmailMCPServer {
    constructor() {
        this.server = new Server(
            {
                name: 'email-mcp-server',
                version: '1.0.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        this.setupToolHandlers();
        this.setupTransporter();
    }

    async setupTransporter() {
        // Setup email transporter using environment variables
        this.transporter = nodemailer.createTransporter({
            service: 'gmail',
            auth: {
                user: process.env.SMTP_USER,
                pass: process.env.SMTP_PASS
            }
        });
    }

    setupToolHandlers() {
        // List available tools
        this.server.setRequestHandler(ListToolsRequestSchema, async () => {
            return {
                tools: [
                    {
                        name: 'send_email',
                        description: 'Send an email to specified recipient',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                to: {
                                    type: 'string',
                                    description: 'Recipient email address'
                                },
                                subject: {
                                    type: 'string',
                                    description: 'Email subject'
                                },
                                body: {
                                    type: 'string',
                                    description: 'Email body content'
                                },
                                cc: {
                                    type: 'string',
                                    description: 'CC email addresses (optional)'
                                },
                                attachments: {
                                    type: 'array',
                                    description: 'File paths for attachments (optional)',
                                    items: {
                                        type: 'string'
                                    }
                                }
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
                                to: { type: 'string' },
                                subject: { type: 'string' },
                                body: { type: 'string' },
                                cc: { type: 'string' },
                                priority: {
                                    type: 'string',
                                    enum: ['low', 'normal', 'high'],
                                    default: 'normal'
                                }
                            },
                            required: ['to', 'subject', 'body']
                        }
                    },
                    {
                        name: 'check_email_status',
                        description: 'Check the status of sent emails',
                        inputSchema: {
                            type: 'object',
                            properties: {
                                message_id: {
                                    type: 'string',
                                    description: 'Message ID to check'
                                }
                            }
                        }
                    }
                ]
            };
        });

        // Handle tool calls
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            const { name, arguments: args } = request.params;

            try {
                switch (name) {
                    case 'send_email':
                        return await this.sendEmail(args);
                    case 'draft_email':
                        return await this.draftEmail(args);
                    case 'check_email_status':
                        return await this.checkEmailStatus(args);
                    default:
                        throw new Error(`Unknown tool: ${name}`);
                }
            } catch (error) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Error: ${error.message}`
                        }
                    ],
                    isError: true
                };
            }
        });
    }

    async sendEmail(args) {
        const { to, subject, body, cc, attachments } = args;

        // Prepare email options
        const mailOptions = {
            from: process.env.SMTP_USER,
            to: to,
            subject: subject,
            html: body,
            messageId: `ai-employee-${Date.now()}@${process.env.SMTP_DOMAIN || 'localhost'}`
        };

        if (cc) {
            mailOptions.cc = cc;
        }

        if (attachments && attachments.length > 0) {
            mailOptions.attachments = attachments.map(filePath => ({
                path: filePath,
                filename: path.basename(filePath)
            }));
        }

        try {
            const info = await this.transporter.sendMail(mailOptions);

            // Log the sent email
            await this.logEmailActivity('sent', mailOptions, info);

            return {
                content: [
                    {
                        type: 'text',
                        text: `Email sent successfully to ${to}. Message ID: ${info.messageId}`
                    }
                ]
            };
        } catch (error) {
            await this.logEmailActivity('failed', mailOptions, { error: error.message });
            throw error;
        }
    }

    async draftEmail(args) {
        const { to, subject, body, cc, priority } = args;

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const vaultPath = process.env.AI_EMPLOYEE_VAULT || './AI_Employee_Vault';
        const approvalPath = path.join(vaultPath, 'Pending_Approval');

        // Ensure approval directory exists
        await fs.mkdir(approvalPath, { recursive: true });

        const draftContent = `---
type: email_approval
to: ${to}
subject: ${subject}
cc: ${cc || ''}
priority: ${priority}
created: ${new Date().toISOString()}
status: pending_approval
---

## Email Draft for Approval

**To:** ${to}
**Subject:** ${subject}
${cc ? `**CC:** ${cc}` : ''}
**Priority:** ${priority}

### Email Content:
${body}

### Actions:
- Move this file to /Approved folder to send
- Move this file to /Rejected folder to cancel
- Edit content above if changes needed before approval

### AI Instructions:
This email draft requires human approval before sending. The email will be sent automatically once moved to the Approved folder.
`;

        const filename = `EMAIL_DRAFT_${to.replace(/[^a-zA-Z0-9]/g, '_')}_${timestamp}.md`;
        const filepath = path.join(approvalPath, filename);

        await fs.writeFile(filepath, draftContent, 'utf8');

        return {
            content: [
                {
                    type: 'text',
                    text: `Email draft created for approval: ${filepath}\nMove to /Approved folder to send.`
                }
            ]
        };
    }

    async checkEmailStatus(args) {
        const { message_id } = args;

        // This is a simplified status check
        // In a real implementation, you might check with email service provider
        return {
            content: [
                {
                    type: 'text',
                    text: `Email status check for ${message_id}: This feature requires integration with email service provider APIs for detailed tracking.`
                }
            ]
        };
    }

    async logEmailActivity(status, mailOptions, info) {
        try {
            const vaultPath = process.env.AI_EMPLOYEE_VAULT || './AI_Employee_Vault';
            const logsPath = path.join(vaultPath, 'Logs');

            await fs.mkdir(logsPath, { recursive: true });

            const logEntry = {
                timestamp: new Date().toISOString(),
                action: 'email_send',
                status: status,
                to: mailOptions.to,
                subject: mailOptions.subject,
                message_id: info.messageId || 'unknown',
                error: info.error || null
            };

            const logFile = path.join(logsPath, `${new Date().toISOString().split('T')[0]}.json`);

            let logs = [];
            try {
                const existingLogs = await fs.readFile(logFile, 'utf8');
                logs = JSON.parse(existingLogs);
            } catch (e) {
                // File doesn't exist or is invalid, start fresh
            }

            logs.push(logEntry);
            await fs.writeFile(logFile, JSON.stringify(logs, null, 2));

        } catch (error) {
            console.error('Failed to log email activity:', error);
        }
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Email MCP Server running on stdio');
    }
}

// Start the server
if (require.main === module) {
    const server = new EmailMCPServer();
    server.run().catch(console.error);
}

module.exports = EmailMCPServer;
```

## Package.json

```json
{
  "name": "email-mcp-server",
  "version": "1.0.0",
  "description": "MCP server for email operations",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.4.0",
    "nodemailer": "^6.9.0"
  }
}
```

## Installation

```bash
cd email-mcp-server
npm install
```

## Configuration

Add to your Claude Code MCP configuration:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["./email-mcp-server/server.js"],
      "env": {
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_PASS": "your-app-password",
        "SMTP_DOMAIN": "gmail.com",
        "AI_EMPLOYEE_VAULT": "./AI_Employee_Vault"
      }
    }
  ]
}
```

## Usage in Claude Code

```
# Send email directly (for approved contacts)
Use the email MCP server to send an email to client@example.com with subject "Invoice Ready" and body "Your invoice is attached."

# Create draft for approval (for new contacts or sensitive emails)
Use the email MCP server to draft an email to newclient@example.com for approval.
```

This MCP server provides secure email functionality with human-in-the-loop approval for sensitive communications.