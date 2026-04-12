#!/usr/bin/env node
/**
 * WhatsApp MCP Server
 * Provides WhatsApp Cloud API operations via Model Context Protocol
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const WHATSAPP_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN || '';
const WHATSAPP_PHONE_ID = process.env.WHATSAPP_PHONE_NUMBER_ID || '';
const API_VERSION = 'v18.0';
const BASE_URL = `https://graph.facebook.com/${API_VERSION}`;

class WhatsAppMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'whatsapp-mcp-server',
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
          name: 'send_whatsapp_message',
          description: 'Send a WhatsApp message via Cloud API',
          inputSchema: {
            type: 'object',
            properties: {
              to: {
                type: 'string',
                description: 'Recipient phone number (without + sign)',
              },
              message: {
                type: 'string',
                description: 'Message text to send',
              },
            },
            required: ['to', 'message'],
          },
        },
        {
          name: 'send_whatsapp_template',
          description: 'Send a WhatsApp template message',
          inputSchema: {
            type: 'object',
            properties: {
              to: {
                type: 'string',
                description: 'Recipient phone number',
              },
              templateName: {
                type: 'string',
                description: 'Template name',
              },
              languageCode: {
                type: 'string',
                description: 'Language code (e.g., en_US)',
                default: 'en_US',
              },
            },
            required: ['to', 'templateName'],
          },
        },
        {
          name: 'get_whatsapp_media',
          description: 'Get WhatsApp media URL by media ID',
          inputSchema: {
            type: 'object',
            properties: {
              mediaId: {
                type: 'string',
                description: 'WhatsApp media ID',
              },
            },
            required: ['mediaId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'send_whatsapp_message':
            return await this.sendMessage(args);
          case 'send_whatsapp_template':
            return await this.sendTemplate(args);
          case 'get_whatsapp_media':
            return await this.getMedia(args);
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

  async sendMessage(args) {
    const { to, message } = args;

    const url = `${BASE_URL}/${WHATSAPP_PHONE_ID}/messages`;

    const payload = {
      messaging_product: 'whatsapp',
      recipient_type: 'individual',
      to,
      type: 'text',
      text: {
        preview_url: false,
        body: message,
      },
    };

    const response = await axios.post(url, payload, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_TOKEN}`,
        'Content-Type': 'application/json',
      },
    });

    const messageId = response.data.messages?.[0]?.id || 'unknown';

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            messageId,
            to,
            status: 'sent',
          }, null, 2),
        },
      ],
    };
  }

  async sendTemplate(args) {
    const { to, templateName, languageCode = 'en_US' } = args;

    const url = `${BASE_URL}/${WHATSAPP_PHONE_ID}/messages`;

    const payload = {
      messaging_product: 'whatsapp',
      to,
      type: 'template',
      template: {
        name: templateName,
        language: {
          code: languageCode,
        },
      },
    };

    const response = await axios.post(url, payload, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_TOKEN}`,
        'Content-Type': 'application/json',
      },
    });

    const messageId = response.data.messages?.[0]?.id || 'unknown';

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            messageId,
            to,
            template: templateName,
          }, null, 2),
        },
      ],
    };
  }

  async getMedia(args) {
    const { mediaId } = args;

    const url = `${BASE_URL}/${mediaId}`;

    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_TOKEN}`,
      },
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            mediaId,
            url: response.data.url,
            mimeType: response.data.mime_type,
            fileSize: response.data.file_size,
          }, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('WhatsApp MCP server running on stdio');
  }
}

const server = new WhatsAppMCPServer();
server.run().catch(console.error);
