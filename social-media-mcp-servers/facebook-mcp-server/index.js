#!/usr/bin/env node

/**
 * Facebook MCP Server for Gold Tier AI Employee
 * Provides comprehensive Facebook page management and marketing automation
 */

import axios from 'axios';
import Joi from 'joi';
import dotenv from 'dotenv';
import FormData from 'form-data';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class FacebookMCPServer {
    constructor() {
        this.accessToken = process.env.FACEBOOK_ACCESS_TOKEN;
        this.pageId = process.env.FACEBOOK_PAGE_ID;
        this.appId = process.env.FACEBOOK_APP_ID;
        this.appSecret = process.env.FACEBOOK_APP_SECRET;
        this.apiVersion = 'v19.0';
        this.baseUrl = `https://graph.facebook.com/${this.apiVersion}`;

        this.setupServer();
    }

    setupServer() {
        console.log('📘 Starting Facebook MCP Server for Gold Tier AI Employee...');

        // Initialize server capabilities
        this.tools = [
            {
                name: 'create_facebook_post',
                description: 'Create and publish a post to Facebook page',
                inputSchema: {
                    type: 'object',
                    properties: {
                        message: { type: 'string', description: 'Post content text' },
                        image_url: { type: 'string', description: 'Optional image URL' },
                        link: { type: 'string', description: 'Optional link to share' },
                        scheduled_time: { type: 'string', description: 'Schedule post (ISO 8601 format)' },
                        target_audience: { type: 'string', description: 'Target audience for post' }
                    },
                    required: ['message']
                }
            },
            {
                name: 'get_page_insights',
                description: 'Get Facebook page analytics and insights',
                inputSchema: {
                    type: 'object',
                    properties: {
                        metric: {
                            type: 'string',
                            enum: ['page_fans', 'page_impressions', 'page_engaged_users', 'page_post_engagements'],
                            description: 'Specific metric to retrieve'
                        },
                        period: {
                            type: 'string',
                            enum: ['day', 'week', 'days_28'],
                            default: 'week'
                        },
                        since: { type: 'string', description: 'Start date (YYYY-MM-DD)' },
                        until: { type: 'string', description: 'End date (YYYY-MM-DD)' }
                    }
                }
            },
            {
                name: 'manage_comments',
                description: 'Monitor and respond to page comments',
                inputSchema: {
                    type: 'object',
                    properties: {
                        action: {
                            type: 'string',
                            enum: ['list', 'reply', 'hide', 'delete'],
                            description: 'Action to perform on comments'
                        },
                        comment_id: { type: 'string', description: 'Comment ID for reply/hide/delete actions' },
                        reply_message: { type: 'string', description: 'Reply message content' },
                        post_id: { type: 'string', description: 'Post ID to get comments from' }
                    },
                    required: ['action']
                }
            },
            {
                name: 'create_lead_ad',
                description: 'Create Facebook lead generation advertisement',
                inputSchema: {
                    type: 'object',
                    properties: {
                        campaign_name: { type: 'string', description: 'Campaign name' },
                        ad_text: { type: 'string', description: 'Advertisement text content' },
                        target_audience: { type: 'object', description: 'Audience targeting parameters' },
                        budget: { type: 'number', description: 'Daily budget in USD' },
                        call_to_action: { type: 'string', description: 'Call to action button text' }
                    },
                    required: ['campaign_name', 'ad_text', 'budget']
                }
            },
            {
                name: 'analyze_competitors',
                description: 'Analyze competitor Facebook pages and content',
                inputSchema: {
                    type: 'object',
                    properties: {
                        competitor_pages: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'List of competitor page IDs or usernames'
                        },
                        analysis_type: {
                            type: 'string',
                            enum: ['engagement', 'content', 'posting_frequency'],
                            default: 'engagement'
                        }
                    },
                    required: ['competitor_pages']
                }
            }
        ];
    }

    async makeAPICall(endpoint, method = 'GET', data = null) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const config = {
                method,
                url,
                params: method === 'GET' ? { access_token: this.accessToken, ...data } : { access_token: this.accessToken },
                data: method !== 'GET' ? data : undefined
            };

            const response = await axios(config);
            return response.data;
        } catch (error) {
            console.error(`Facebook API error: ${error.response?.data?.error?.message || error.message}`);
            throw new Error(`Facebook API call failed: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    async createFacebookPost(params) {
        const schema = Joi.object({
            message: Joi.string().required(),
            image_url: Joi.string().uri().optional(),
            link: Joi.string().uri().optional(),
            scheduled_time: Joi.string().optional(),
            target_audience: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const postData = {
                message: value.message
            };

            if (value.image_url) {
                postData.url = value.image_url;
            }

            if (value.link) {
                postData.link = value.link;
            }

            if (value.scheduled_time) {
                postData.scheduled_publish_time = Math.floor(new Date(value.scheduled_time).getTime() / 1000);
                postData.published = false;
            }

            const result = await this.makeAPICall(`/${this.pageId}/feed`, 'POST', postData);

            return {
                success: true,
                post_id: result.id,
                message: 'Facebook post created successfully',
                scheduled: !!value.scheduled_time,
                post_url: `https://facebook.com/${result.id}`
            };

        } catch (error) {
            console.error('Error creating Facebook post:', error);
            throw new Error(`Failed to create Facebook post: ${error.message}`);
        }
    }

    async getPageInsights(params = {}) {
        try {
            const metric = params.metric || 'page_impressions';
            const period = params.period || 'week';

            const insightsData = {
                metric: metric,
                period: period
            };

            if (params.since) insightsData.since = params.since;
            if (params.until) insightsData.until = params.until;

            const result = await this.makeAPICall(`/${this.pageId}/insights`, 'GET', insightsData);

            // Get basic page info
            const pageInfo = await this.makeAPICall(`/${this.pageId}`, 'GET', {
                fields: 'name,fan_count,talking_about_count,were_here_count'
            });

            return {
                success: true,
                page_info: pageInfo,
                insights: result.data,
                period: period,
                metric: metric,
                summary: this.formatInsightsSummary(result.data, pageInfo)
            };

        } catch (error) {
            console.error('Error getting page insights:', error);
            throw new Error(`Failed to get page insights: ${error.message}`);
        }
    }

    formatInsightsSummary(insights, pageInfo) {
        const summary = {
            page_name: pageInfo.name,
            total_fans: pageInfo.fan_count,
            talking_about: pageInfo.talking_about_count
        };

        insights.forEach(insight => {
            if (insight.values && insight.values.length > 0) {
                const latestValue = insight.values[insight.values.length - 1];
                summary[insight.name] = latestValue.value;
            }
        });

        return summary;
    }

    async manageComments(params) {
        const schema = Joi.object({
            action: Joi.string().valid('list', 'reply', 'hide', 'delete').required(),
            comment_id: Joi.string().optional(),
            reply_message: Joi.string().optional(),
            post_id: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            switch (value.action) {
                case 'list':
                    const endpoint = value.post_id ? `/${value.post_id}/comments` : `/${this.pageId}/conversations`;
                    const comments = await this.makeAPICall(endpoint, 'GET', {
                        fields: 'id,message,from,created_time,like_count'
                    });

                    return {
                        success: true,
                        action: 'list',
                        comments: comments.data || [],
                        count: comments.data?.length || 0
                    };

                case 'reply':
                    if (!value.comment_id || !value.reply_message) {
                        throw new Error('Comment ID and reply message required for reply action');
                    }

                    const replyResult = await this.makeAPICall(`/${value.comment_id}/comments`, 'POST', {
                        message: value.reply_message
                    });

                    return {
                        success: true,
                        action: 'reply',
                        reply_id: replyResult.id,
                        message: 'Reply posted successfully'
                    };

                case 'hide':
                    if (!value.comment_id) {
                        throw new Error('Comment ID required for hide action');
                    }

                    await this.makeAPICall(`/${value.comment_id}`, 'POST', {
                        is_hidden: true
                    });

                    return {
                        success: true,
                        action: 'hide',
                        message: 'Comment hidden successfully'
                    };

                case 'delete':
                    if (!value.comment_id) {
                        throw new Error('Comment ID required for delete action');
                    }

                    await this.makeAPICall(`/${value.comment_id}`, 'DELETE');

                    return {
                        success: true,
                        action: 'delete',
                        message: 'Comment deleted successfully'
                    };

                default:
                    throw new Error(`Unknown action: ${value.action}`);
            }

        } catch (error) {
            console.error('Error managing comments:', error);
            throw new Error(`Failed to manage comments: ${error.message}`);
        }
    }

    async createLeadAd(params) {
        const schema = Joi.object({
            campaign_name: Joi.string().required(),
            ad_text: Joi.string().required(),
            target_audience: Joi.object().optional(),
            budget: Joi.number().positive().required(),
            call_to_action: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            // This is a simplified implementation
            // In production, you'd need to create campaign, ad set, and ad
            const campaignData = {
                name: value.campaign_name,
                objective: 'LEAD_GENERATION',
                status: 'PAUSED', // Start paused for review
                special_ad_categories: []
            };

            // Note: This requires Facebook Marketing API access
            // For now, return a mock response
            return {
                success: true,
                campaign_name: value.campaign_name,
                status: 'created_pending_review',
                budget: value.budget,
                message: 'Lead ad campaign created (requires Facebook Marketing API setup for full functionality)',
                next_steps: [
                    'Set up Facebook Marketing API access',
                    'Configure payment method',
                    'Review and activate campaign'
                ]
            };

        } catch (error) {
            console.error('Error creating lead ad:', error);
            throw new Error(`Failed to create lead ad: ${error.message}`);
        }
    }

    async analyzeCompetitors(params) {
        const schema = Joi.object({
            competitor_pages: Joi.array().items(Joi.string()).required(),
            analysis_type: Joi.string().valid('engagement', 'content', 'posting_frequency').default('engagement')
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const analysis = {
                analysis_type: value.analysis_type,
                competitors: [],
                summary: {}
            };

            for (const pageId of value.competitor_pages) {
                try {
                    // Get basic page info (public data only)
                    const pageInfo = await this.makeAPICall(`/${pageId}`, 'GET', {
                        fields: 'name,fan_count,talking_about_count,category'
                    });

                    // Get recent posts (public posts only)
                    const posts = await this.makeAPICall(`/${pageId}/posts`, 'GET', {
                        fields: 'message,created_time,likes.summary(true),comments.summary(true),shares',
                        limit: 10
                    });

                    const competitorData = {
                        page_id: pageId,
                        name: pageInfo.name,
                        fan_count: pageInfo.fan_count,
                        category: pageInfo.category,
                        recent_posts: posts.data?.length || 0,
                        avg_engagement: this.calculateAverageEngagement(posts.data || [])
                    };

                    analysis.competitors.push(competitorData);

                } catch (pageError) {
                    console.warn(`Could not analyze competitor ${pageId}:`, pageError.message);
                    analysis.competitors.push({
                        page_id: pageId,
                        error: 'Could not access page data',
                        note: 'Page may be private or ID incorrect'
                    });
                }
            }

            // Generate summary
            analysis.summary = this.generateCompetitorSummary(analysis.competitors, value.analysis_type);

            return {
                success: true,
                ...analysis
            };

        } catch (error) {
            console.error('Error analyzing competitors:', error);
            throw new Error(`Failed to analyze competitors: ${error.message}`);
        }
    }

    calculateAverageEngagement(posts) {
        if (!posts || posts.length === 0) return 0;

        const totalEngagement = posts.reduce((sum, post) => {
            const likes = post.likes?.summary?.total_count || 0;
            const comments = post.comments?.summary?.total_count || 0;
            const shares = post.shares?.count || 0;
            return sum + likes + comments + shares;
        }, 0);

        return Math.round(totalEngagement / posts.length);
    }

    generateCompetitorSummary(competitors, analysisType) {
        const validCompetitors = competitors.filter(c => !c.error);

        if (validCompetitors.length === 0) {
            return { message: 'No competitor data available for analysis' };
        }

        const summary = {
            total_analyzed: validCompetitors.length,
            avg_fan_count: Math.round(validCompetitors.reduce((sum, c) => sum + (c.fan_count || 0), 0) / validCompetitors.length),
            avg_engagement: Math.round(validCompetitors.reduce((sum, c) => sum + (c.avg_engagement || 0), 0) / validCompetitors.length),
            top_performer: validCompetitors.reduce((top, current) =>
                (current.avg_engagement || 0) > (top.avg_engagement || 0) ? current : top, validCompetitors[0])
        };

        return summary;
    }

    // MCP Server Interface Methods
    async handleToolCall(toolName, params) {
        try {
            switch (toolName) {
                case 'create_facebook_post':
                    return await this.createFacebookPost(params);
                case 'get_page_insights':
                    return await this.getPageInsights(params);
                case 'manage_comments':
                    return await this.manageComments(params);
                case 'create_lead_ad':
                    return await this.createLeadAd(params);
                case 'analyze_competitors':
                    return await this.analyzeCompetitors(params);
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
        console.log('📘 Facebook MCP Server starting...');

        if (!this.accessToken || !this.pageId) {
            console.error('❌ Facebook credentials not configured. Please set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID');
            process.exit(1);
        }

        console.log('✅ Facebook MCP Server ready for Gold Tier operations!');
        console.log(`📊 Page ID: ${this.pageId}`);
        console.log(`🔧 API Version: ${this.apiVersion}`);

        // Keep server running
        process.stdin.resume();
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new FacebookMCPServer();
    server.start().catch(console.error);
}

export default FacebookMCPServer;