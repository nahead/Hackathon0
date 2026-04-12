#!/usr/bin/env node
/**
 * Odoo MCP Server
 * Provides Odoo Community Edition operations via Model Context Protocol
 * Uses Odoo JSON-RPC API (Odoo 19+)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DB = process.env.ODOO_DB || 'odoo';
const ODOO_USERNAME = process.env.ODOO_USERNAME || 'admin';
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || 'admin';

class OdooMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'odoo-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.uid = null;
    this.setupToolHandlers();

    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async authenticate() {
    if (this.uid) return this.uid;

    try {
      const response = await axios.post(
        `${ODOO_URL}/web/session/authenticate`,
        {
          jsonrpc: '2.0',
          params: {
            db: ODOO_DB,
            login: ODOO_USERNAME,
            password: ODOO_PASSWORD,
          },
        },
        {
          headers: { 'Content-Type': 'application/json' },
        }
      );

      if (response.data.result && response.data.result.uid) {
        this.uid = response.data.result.uid;
        this.sessionId = response.headers['set-cookie'];
        return this.uid;
      }

      throw new Error('Authentication failed');
    } catch (error) {
      throw new Error(`Odoo authentication error: ${error.message}`);
    }
  }

  async callOdoo(model, method, args = [], kwargs = {}) {
    await this.authenticate();

    const response = await axios.post(
      `${ODOO_URL}/web/dataset/call_kw`,
      {
        jsonrpc: '2.0',
        method: 'call',
        params: {
          model,
          method,
          args,
          kwargs,
        },
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Cookie: this.sessionId,
        },
      }
    );

    if (response.data.error) {
      throw new Error(response.data.error.data.message);
    }

    return response.data.result;
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'create_invoice',
          description: 'Create a customer invoice in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              partnerId: {
                type: 'number',
                description: 'Customer partner ID',
              },
              invoiceLines: {
                type: 'array',
                description: 'Invoice line items',
                items: {
                  type: 'object',
                  properties: {
                    productId: { type: 'number' },
                    quantity: { type: 'number' },
                    priceUnit: { type: 'number' },
                    name: { type: 'string' },
                  },
                },
              },
            },
            required: ['partnerId', 'invoiceLines'],
          },
        },
        {
          name: 'list_invoices',
          description: 'List customer invoices',
          inputSchema: {
            type: 'object',
            properties: {
              limit: {
                type: 'number',
                description: 'Maximum number of invoices',
                default: 10,
              },
              state: {
                type: 'string',
                description: 'Invoice state (draft, posted, cancel)',
              },
            },
          },
        },
        {
          name: 'get_partner',
          description: 'Get customer/partner information',
          inputSchema: {
            type: 'object',
            properties: {
              partnerId: {
                type: 'number',
                description: 'Partner ID',
              },
            },
            required: ['partnerId'],
          },
        },
        {
          name: 'create_partner',
          description: 'Create a new customer/partner',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Partner name',
              },
              email: {
                type: 'string',
                description: 'Email address',
              },
              phone: {
                type: 'string',
                description: 'Phone number',
              },
            },
            required: ['name'],
          },
        },
        {
          name: 'get_revenue_report',
          description: 'Get revenue summary report',
          inputSchema: {
            type: 'object',
            properties: {
              dateFrom: {
                type: 'string',
                description: 'Start date (YYYY-MM-DD)',
              },
              dateTo: {
                type: 'string',
                description: 'End date (YYYY-MM-DD)',
              },
            },
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'create_invoice':
            return await this.createInvoice(args);
          case 'list_invoices':
            return await this.listInvoices(args);
          case 'get_partner':
            return await this.getPartner(args);
          case 'create_partner':
            return await this.createPartner(args);
          case 'get_revenue_report':
            return await this.getRevenueReport(args);
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

  async createInvoice(args) {
    const { partnerId, invoiceLines } = args;

    const invoiceData = {
      partner_id: partnerId,
      move_type: 'out_invoice',
      invoice_line_ids: invoiceLines.map(line => [0, 0, {
        product_id: line.productId,
        quantity: line.quantity,
        price_unit: line.priceUnit,
        name: line.name,
      }]),
    };

    const invoiceId = await this.callOdoo('account.move', 'create', [[invoiceData]]);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            invoiceId,
            partnerId,
            status: 'draft',
          }, null, 2),
        },
      ],
    };
  }

  async listInvoices(args) {
    const { limit = 10, state } = args;

    const domain = [['move_type', '=', 'out_invoice']];
    if (state) {
      domain.push(['state', '=', state]);
    }

    const invoices = await this.callOdoo(
      'account.move',
      'search_read',
      [domain],
      {
        fields: ['name', 'partner_id', 'amount_total', 'state', 'invoice_date'],
        limit,
      }
    );

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            count: invoices.length,
            invoices,
          }, null, 2),
        },
      ],
    };
  }

  async getPartner(args) {
    const { partnerId } = args;

    const partner = await this.callOdoo(
      'res.partner',
      'read',
      [[partnerId]],
      { fields: ['name', 'email', 'phone', 'street', 'city', 'country_id'] }
    );

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(partner[0], null, 2),
        },
      ],
    };
  }

  async createPartner(args) {
    const { name, email, phone } = args;

    const partnerData = {
      name,
      email: email || false,
      phone: phone || false,
    };

    const partnerId = await this.callOdoo('res.partner', 'create', [[partnerData]]);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            partnerId,
            name,
          }, null, 2),
        },
      ],
    };
  }

  async getRevenueReport(args) {
    const { dateFrom, dateTo } = args;

    const domain = [
      ['move_type', '=', 'out_invoice'],
      ['state', '=', 'posted'],
    ];

    if (dateFrom) {
      domain.push(['invoice_date', '>=', dateFrom]);
    }
    if (dateTo) {
      domain.push(['invoice_date', '<=', dateTo]);
    }

    const invoices = await this.callOdoo(
      'account.move',
      'search_read',
      [domain],
      { fields: ['amount_total', 'invoice_date'] }
    );

    const totalRevenue = invoices.reduce((sum, inv) => sum + inv.amount_total, 0);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            period: { from: dateFrom, to: dateTo },
            totalRevenue,
            invoiceCount: invoices.length,
            averageInvoice: invoices.length > 0 ? totalRevenue / invoices.length : 0,
          }, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Odoo MCP server running on stdio');
  }
}

const server = new OdooMCPServer();
server.run().catch(console.error);
