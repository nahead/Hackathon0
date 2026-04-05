#!/usr/bin/env node

/**
 * Odoo Accounting MCP Server for Gold Tier AI Employee
 * Provides comprehensive accounting operations via Odoo Community Edition
 */

import axios from 'axios';
import Joi from 'joi';
import dotenv from 'dotenv';
import { parseString } from 'xml2js';
import moment from 'moment';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class OdooMCPServer {
    constructor() {
        this.odooUrl = process.env.ODOO_URL || 'http://localhost:8069';
        this.database = process.env.ODOO_DATABASE || 'ai_employee_db';
        this.username = process.env.ODOO_USERNAME || 'admin';
        this.password = process.env.ODOO_PASSWORD || 'admin';
        this.uid = null;
        this.sessionId = null;

        this.setupServer();
    }

    setupServer() {
        console.log('🥇 Starting Odoo MCP Server for Gold Tier AI Employee...');

        // Initialize server capabilities
        this.tools = [
            {
                name: 'create_invoice',
                description: 'Create a new customer invoice in Odoo',
                inputSchema: {
                    type: 'object',
                    properties: {
                        customer_name: { type: 'string', description: 'Customer name' },
                        customer_email: { type: 'string', description: 'Customer email' },
                        invoice_lines: {
                            type: 'array',
                            items: {
                                type: 'object',
                                properties: {
                                    product_name: { type: 'string' },
                                    quantity: { type: 'number' },
                                    unit_price: { type: 'number' },
                                    description: { type: 'string' }
                                }
                            }
                        },
                        due_date: { type: 'string', description: 'Invoice due date (YYYY-MM-DD)' }
                    },
                    required: ['customer_name', 'invoice_lines']
                }
            },
            {
                name: 'track_payment',
                description: 'Record a payment against an invoice',
                inputSchema: {
                    type: 'object',
                    properties: {
                        invoice_id: { type: 'number', description: 'Invoice ID in Odoo' },
                        amount: { type: 'number', description: 'Payment amount' },
                        payment_date: { type: 'string', description: 'Payment date (YYYY-MM-DD)' },
                        payment_method: { type: 'string', description: 'Payment method' },
                        reference: { type: 'string', description: 'Payment reference' }
                    },
                    required: ['invoice_id', 'amount']
                }
            },
            {
                name: 'get_financial_summary',
                description: 'Get financial summary for CEO briefing',
                inputSchema: {
                    type: 'object',
                    properties: {
                        period: { type: 'string', enum: ['week', 'month', 'quarter'], default: 'month' },
                        include_details: { type: 'boolean', default: false }
                    }
                }
            },
            {
                name: 'list_unpaid_invoices',
                description: 'Get list of unpaid invoices',
                inputSchema: {
                    type: 'object',
                    properties: {
                        overdue_only: { type: 'boolean', default: false },
                        customer_id: { type: 'number', description: 'Filter by customer ID' }
                    }
                }
            },
            {
                name: 'create_customer',
                description: 'Create a new customer in Odoo',
                inputSchema: {
                    type: 'object',
                    properties: {
                        name: { type: 'string', description: 'Customer name' },
                        email: { type: 'string', description: 'Customer email' },
                        phone: { type: 'string', description: 'Customer phone' },
                        address: { type: 'string', description: 'Customer address' },
                        is_company: { type: 'boolean', default: false }
                    },
                    required: ['name']
                }
            }
        ];
    }

    async authenticate() {
        try {
            const response = await axios.post(`${this.odooUrl}/web/session/authenticate`, {
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    db: this.database,
                    login: this.username,
                    password: this.password
                }
            });

            if (response.data.result && response.data.result.uid) {
                this.uid = response.data.result.uid;
                this.sessionId = response.data.result.session_id;
                console.log('✅ Odoo authentication successful');
                return true;
            } else {
                console.error('❌ Odoo authentication failed');
                return false;
            }
        } catch (error) {
            console.error('❌ Odoo connection error:', error.message);
            return false;
        }
    }

    async callOdooMethod(model, method, args = [], kwargs = {}) {
        if (!this.uid) {
            const authenticated = await this.authenticate();
            if (!authenticated) {
                throw new Error('Failed to authenticate with Odoo');
            }
        }

        try {
            const response = await axios.post(`${this.odooUrl}/web/dataset/call_kw`, {
                jsonrpc: '2.0',
                method: 'call',
                params: {
                    model: model,
                    method: method,
                    args: args,
                    kwargs: kwargs
                }
            });

            if (response.data.error) {
                throw new Error(`Odoo error: ${response.data.error.message}`);
            }

            return response.data.result;
        } catch (error) {
            console.error(`Error calling Odoo method ${model}.${method}:`, error.message);
            throw error;
        }
    }

    async createInvoice(params) {
        const schema = Joi.object({
            customer_name: Joi.string().required(),
            customer_email: Joi.string().email().optional(),
            invoice_lines: Joi.array().items(Joi.object({
                product_name: Joi.string().required(),
                quantity: Joi.number().positive().required(),
                unit_price: Joi.number().positive().required(),
                description: Joi.string().optional()
            })).required(),
            due_date: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            // Find or create customer
            let customerId = await this.findOrCreateCustomer(value.customer_name, value.customer_email);

            // Prepare invoice lines
            const invoiceLines = [];
            for (const line of value.invoice_lines) {
                invoiceLines.push([0, 0, {
                    name: line.description || line.product_name,
                    quantity: line.quantity,
                    price_unit: line.unit_price,
                    account_id: 1, // Default income account (should be configured)
                }]);
            }

            // Create invoice
            const invoiceData = {
                partner_id: customerId,
                move_type: 'out_invoice',
                invoice_date: moment().format('YYYY-MM-DD'),
                invoice_date_due: value.due_date || moment().add(30, 'days').format('YYYY-MM-DD'),
                invoice_line_ids: invoiceLines,
                state: 'draft'
            };

            const invoiceId = await this.callOdooMethod('account.move', 'create', [invoiceData]);

            // Post the invoice (confirm it)
            await this.callOdooMethod('account.move', 'action_post', [[invoiceId]]);

            // Get invoice details
            const invoice = await this.callOdooMethod('account.move', 'read', [[invoiceId]], {
                fields: ['name', 'amount_total', 'state', 'invoice_date_due']
            });

            return {
                success: true,
                invoice_id: invoiceId,
                invoice_number: invoice[0].name,
                total_amount: invoice[0].amount_total,
                due_date: invoice[0].invoice_date_due,
                status: invoice[0].state
            };

        } catch (error) {
            console.error('Error creating invoice:', error);
            throw new Error(`Failed to create invoice: ${error.message}`);
        }
    }

    async findOrCreateCustomer(name, email) {
        try {
            // Search for existing customer
            const existingCustomers = await this.callOdooMethod('res.partner', 'search_read',
                [[['name', '=', name]]], { fields: ['id', 'name'] });

            if (existingCustomers.length > 0) {
                return existingCustomers[0].id;
            }

            // Create new customer
            const customerData = {
                name: name,
                email: email || '',
                is_company: false,
                customer_rank: 1
            };

            const customerId = await this.callOdooMethod('res.partner', 'create', [customerData]);
            console.log(`✅ Created new customer: ${name} (ID: ${customerId})`);

            return customerId;

        } catch (error) {
            console.error('Error finding/creating customer:', error);
            throw error;
        }
    }

    async trackPayment(params) {
        const schema = Joi.object({
            invoice_id: Joi.number().required(),
            amount: Joi.number().positive().required(),
            payment_date: Joi.string().optional(),
            payment_method: Joi.string().optional(),
            reference: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            // Get invoice details
            const invoice = await this.callOdooMethod('account.move', 'read', [[value.invoice_id]], {
                fields: ['name', 'amount_residual', 'state', 'partner_id']
            });

            if (invoice.length === 0) {
                throw new Error(`Invoice with ID ${value.invoice_id} not found`);
            }

            // Create payment
            const paymentData = {
                payment_type: 'inbound',
                partner_type: 'customer',
                partner_id: invoice[0].partner_id[0],
                amount: value.amount,
                date: value.payment_date || moment().format('YYYY-MM-DD'),
                ref: value.reference || `Payment for ${invoice[0].name}`,
                journal_id: 1, // Default bank journal (should be configured)
            };

            const paymentId = await this.callOdooMethod('account.payment', 'create', [paymentData]);

            // Post the payment
            await this.callOdooMethod('account.payment', 'action_post', [[paymentId]]);

            // Reconcile with invoice
            await this.reconcilePayment(paymentId, value.invoice_id);

            return {
                success: true,
                payment_id: paymentId,
                amount: value.amount,
                invoice_number: invoice[0].name,
                remaining_balance: Math.max(0, invoice[0].amount_residual - value.amount)
            };

        } catch (error) {
            console.error('Error tracking payment:', error);
            throw new Error(`Failed to track payment: ${error.message}`);
        }
    }

    async reconcilePayment(paymentId, invoiceId) {
        try {
            // This is a simplified reconciliation
            // In production, you'd need more sophisticated matching
            const payment = await this.callOdooMethod('account.payment', 'read', [[paymentId]], {
                fields: ['move_id']
            });

            if (payment.length > 0 && payment[0].move_id) {
                // Get payment move lines
                const paymentLines = await this.callOdooMethod('account.move.line', 'search_read',
                    [[['move_id', '=', payment[0].move_id[0]], ['credit', '>', 0]]],
                    { fields: ['id'] });

                // Get invoice move lines
                const invoiceLines = await this.callOdooMethod('account.move.line', 'search_read',
                    [[['move_id', '=', invoiceId], ['debit', '>', 0]]],
                    { fields: ['id'] });

                if (paymentLines.length > 0 && invoiceLines.length > 0) {
                    const lineIds = [paymentLines[0].id, invoiceLines[0].id];
                    await this.callOdooMethod('account.move.line', 'reconcile', [lineIds]);
                }
            }
        } catch (error) {
            console.error('Error reconciling payment:', error);
            // Don't throw here as payment was created successfully
        }
    }

    async getFinancialSummary(params = {}) {
        try {
            const period = params.period || 'month';
            const includeDetails = params.include_details || false;

            let dateFrom;
            switch (period) {
                case 'week':
                    dateFrom = moment().startOf('week').format('YYYY-MM-DD');
                    break;
                case 'quarter':
                    dateFrom = moment().startOf('quarter').format('YYYY-MM-DD');
                    break;
                default:
                    dateFrom = moment().startOf('month').format('YYYY-MM-DD');
            }

            const dateTo = moment().format('YYYY-MM-DD');

            // Get revenue (posted invoices)
            const invoices = await this.callOdooMethod('account.move', 'search_read',
                [[
                    ['move_type', '=', 'out_invoice'],
                    ['state', '=', 'posted'],
                    ['invoice_date', '>=', dateFrom],
                    ['invoice_date', '<=', dateTo]
                ]], {
                    fields: ['name', 'amount_total', 'amount_residual', 'invoice_date', 'partner_id']
                });

            const totalRevenue = invoices.reduce((sum, inv) => sum + inv.amount_total, 0);
            const totalOutstanding = invoices.reduce((sum, inv) => sum + inv.amount_residual, 0);
            const totalPaid = totalRevenue - totalOutstanding;

            // Get expenses (vendor bills)
            const bills = await this.callOdooMethod('account.move', 'search_read',
                [[
                    ['move_type', '=', 'in_invoice'],
                    ['state', '=', 'posted'],
                    ['invoice_date', '>=', dateFrom],
                    ['invoice_date', '<=', dateTo]
                ]], {
                    fields: ['amount_total']
                });

            const totalExpenses = bills.reduce((sum, bill) => sum + bill.amount_total, 0);

            const summary = {
                period: period,
                date_from: dateFrom,
                date_to: dateTo,
                revenue: {
                    total: totalRevenue,
                    paid: totalPaid,
                    outstanding: totalOutstanding
                },
                expenses: totalExpenses,
                profit: totalPaid - totalExpenses,
                invoice_count: invoices.length,
                overdue_count: invoices.filter(inv =>
                    inv.amount_residual > 0 && moment(inv.invoice_date_due).isBefore(moment())
                ).length
            };

            if (includeDetails) {
                summary.top_customers = await this.getTopCustomers(dateFrom, dateTo);
                summary.recent_invoices = invoices.slice(0, 10);
            }

            return summary;

        } catch (error) {
            console.error('Error getting financial summary:', error);
            throw new Error(`Failed to get financial summary: ${error.message}`);
        }
    }

    async getTopCustomers(dateFrom, dateTo) {
        try {
            // This would require a more complex query in production
            // For now, return a simplified version
            return [
                { name: 'Top Customer Analysis', note: 'Requires advanced reporting setup' }
            ];
        } catch (error) {
            console.error('Error getting top customers:', error);
            return [];
        }
    }

    async listUnpaidInvoices(params = {}) {
        try {
            const overdueOnly = params.overdue_only || false;
            const customerId = params.customer_id;

            let domain = [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['amount_residual', '>', 0]
            ];

            if (overdueOnly) {
                domain.push(['invoice_date_due', '<', moment().format('YYYY-MM-DD')]);
            }

            if (customerId) {
                domain.push(['partner_id', '=', customerId]);
            }

            const unpaidInvoices = await this.callOdooMethod('account.move', 'search_read',
                [domain], {
                    fields: ['name', 'partner_id', 'amount_total', 'amount_residual',
                            'invoice_date', 'invoice_date_due', 'state'],
                    order: 'invoice_date_due asc'
                });

            return {
                count: unpaidInvoices.length,
                total_outstanding: unpaidInvoices.reduce((sum, inv) => sum + inv.amount_residual, 0),
                invoices: unpaidInvoices.map(inv => ({
                    id: inv.id,
                    number: inv.name,
                    customer: inv.partner_id[1],
                    total_amount: inv.amount_total,
                    outstanding_amount: inv.amount_residual,
                    invoice_date: inv.invoice_date,
                    due_date: inv.invoice_date_due,
                    days_overdue: overdueOnly ? moment().diff(moment(inv.invoice_date_due), 'days') : 0
                }))
            };

        } catch (error) {
            console.error('Error listing unpaid invoices:', error);
            throw new Error(`Failed to list unpaid invoices: ${error.message}`);
        }
    }

    async createCustomer(params) {
        const schema = Joi.object({
            name: Joi.string().required(),
            email: Joi.string().email().optional(),
            phone: Joi.string().optional(),
            address: Joi.string().optional(),
            is_company: Joi.boolean().default(false)
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const customerData = {
                name: value.name,
                email: value.email || '',
                phone: value.phone || '',
                street: value.address || '',
                is_company: value.is_company,
                customer_rank: 1
            };

            const customerId = await this.callOdooMethod('res.partner', 'create', [customerData]);

            const customer = await this.callOdooMethod('res.partner', 'read', [[customerId]], {
                fields: ['name', 'email', 'phone', 'street']
            });

            return {
                success: true,
                customer_id: customerId,
                customer_data: customer[0]
            };

        } catch (error) {
            console.error('Error creating customer:', error);
            throw new Error(`Failed to create customer: ${error.message}`);
        }
    }

    // MCP Server Interface Methods
    async handleToolCall(toolName, params) {
        try {
            switch (toolName) {
                case 'create_invoice':
                    return await this.createInvoice(params);
                case 'track_payment':
                    return await this.trackPayment(params);
                case 'get_financial_summary':
                    return await this.getFinancialSummary(params);
                case 'list_unpaid_invoices':
                    return await this.listUnpaidInvoices(params);
                case 'create_customer':
                    return await this.createCustomer(params);
                default:
                    throw new Error(`Unknown tool: ${toolName}`);
            }
        } catch (error) {
            return {
                error: true,
                message: error.message
            };
        }
    }

    async start() {
        console.log('🥇 Odoo MCP Server starting...');

        // Test connection
        const connected = await this.authenticate();
        if (!connected) {
            console.error('❌ Failed to connect to Odoo. Please check configuration.');
            process.exit(1);
        }

        console.log('✅ Odoo MCP Server ready for Gold Tier operations!');
        console.log(`📊 Connected to: ${this.odooUrl}`);
        console.log(`🗄️  Database: ${this.database}`);
        console.log(`👤 User: ${this.username}`);

        // Keep server running
        process.stdin.resume();
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new OdooMCPServer();
    server.start().catch(console.error);
}

export default OdooMCPServer;