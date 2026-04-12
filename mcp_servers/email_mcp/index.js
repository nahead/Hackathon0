#!/usr/bin/env node
/**
 * Email MCP Server
 * Provides email operations via Model Context Protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import nodemailer from 'nodemailer';
import { google } from 'googleapis';

const SMTP_HOST = process.env.SMTP_HOST || 'smtp.gmail.com';
const SMTP_PORT = parseInt(process.env.SMTP_PORT || '587');
const SMTP_USER = process.env.SMTP_USER || '';
const SMTP_PASS = process.env.SMTP_PASS || '';

// Create email transporter
const transporter = nodemailer.createTransport({
  host: SMTP_HOST,
  port: SMTP_PORT,
  secure: false,
  auth: {
    user: SMTP_USER,
    pass: SMTP_PASS,
  },
});

// Gmail API setup
const oauth2Client = new google.auth.OAuth2();
const gmail = google.gmail({ version: 'v1', auth: oauth2Client });

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

    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'send_email',
          description: 'Send an email via SMTP',
          inputSchema: {
            type: 'object',
            properties: {
              to: {
                type: 'string',
                description: 'Recipient email address',
              },
              subject: {
                type: 'string',
                description: 'Email subject',
              },
              body: {
                type: 'string',
                description: 'Email body (plain text or HTML)',
              },
              html: {
                type: 'boolean',
                description: 'Whether body is HTML',
                default: false,
              },
            },
            required: ['to', 'subject', 'body'],
          },
        },
        {
          name: 'list_emails',
          description: 'List recent emails from Gmail',
          inputSchema: {
            type: 'object',
            properties: {
              maxResults: {
                type: 'number',
                description: 'Maximum number of emails to return',
                default: 10,
              },
              query: {
                type: 'string',
                description: 'Gmail search query (e.g., "is:unread")',
                default: '',
              },
            },
          },
        },
        {
          name: 'read_email',
          description: 'Read a specific email by ID',
          inputSchema: {
            type: 'object',
            properties: {
              messageId: {
                type: 'string',
                description: 'Gmail message ID',
              },
            },
            required: ['messageId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'send_email':
            return await this.sendEmail(args);
          case 'list_emails':
            return await this.listEmails(args);
          case 'read_email':
            return await this.readEmail(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async sendEmail(args) {
    const { to, subject, body, html = false } = args;

    const mailOptions = {
      from: SMTP_USER,
      to,
      subject,
      [html ? 'html' : 'text']: body,
    };

    const info = await transporter.sendMail(mailOptions);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            messageId: info.messageId,
            to,
            subject,
          }, null, 2),
        },
      ],
    };
  }

  async listEmails(args) {
    const { maxResults = 10, query = '' } = args;

    const response = await gmail.users.messages.list({
      userId: 'me',
      maxResults,
      q: query,
    });

    const messages = response.data.messages || [];

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            count: messages.length,
            messages: messages.map(m => ({ id: m.id, threadId: m.threadId })),
          }, null, 2),
        },
      ],
    };
  }

  async readEmail(args) {
    const { messageId } = args;

    const response = await gmail.users.messages.get({
      userId: 'me',
      id: messageId,
      format: 'full',
    });

    const message = response.data;
    const headers = message.payload.headers;

    const getHeader = (name) => {
      const header = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
      return header ? header.value : '';
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            id: message.id,
            from: getHeader('From'),
            to: getHeader('To'),
            subject: getHeader('Subject'),
            date: getHeader('Date'),
            snippet: message.snippet,
          }, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Email MCP server running on stdio');
  }
}

const server = new EmailMCPServer();
server.run().catch(console.error);
