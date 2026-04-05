#!/usr/bin/env node

/**
 * Unified Social Media Management System for Gold Tier AI Employee
 * Coordinates Facebook, Instagram, and Twitter operations with cross-platform analytics
 */

import FacebookMCPServer from '../facebook-mcp-server/index.js';
import InstagramMCPServer from '../instagram-mcp-server/index.js';
import TwitterMCPServer from '../twitter-mcp-server/index.js';
import Joi from 'joi';
import dotenv from 'dotenv';
import moment from 'moment';
import { CronJob } from 'cron';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class UnifiedSocialMediaManager {
    constructor() {
        this.facebookServer = new FacebookMCPServer();
        this.instagramServer = new InstagramMCPServer();
        this.twitterServer = new TwitterMCPServer();

        this.contentQueue = [];
        this.scheduledPosts = [];
        this.analytics = {};

        this.setupServer();
    }

    setupServer() {
        console.log('🌐 Starting Unified Social Media Manager for Gold Tier AI Employee...');

        // Initialize unified capabilities
        this.tools = [
            {
                name: 'cross_platform_post',
                description: 'Post content across multiple social media platforms simultaneously',
                inputSchema: {
                    type: 'object',
                    properties: {
                        content: {
                            type: 'object',
                            properties: {
                                text: { type: 'string', description: 'Base content text' },
                                image_url: { type: 'string', description: 'Image/media URL' },
                                hashtags: { type: 'array', items: { type: 'string' } }
                            },
                            required: ['text']
                        },
                        platforms: {
                            type: 'array',
                            items: { type: 'string', enum: ['facebook', 'instagram', 'twitter'] },
                            description: 'Target platforms for posting'
                        },
                        platform_customization: {
                            type: 'object',
                            properties: {
                                facebook: { type: 'object' },
                                instagram: { type: 'object' },
                                twitter: { type: 'object' }
                            }
                        }
                    },
                    required: ['content', 'platforms']
                }
            },
            {
                name: 'unified_analytics',
                description: 'Get comprehensive analytics across all social media platforms',
                inputSchema: {
                    type: 'object',
                    properties: {
                        time_period: {
                            type: 'string',
                            enum: ['1d', '7d', '30d'],
                            default: '7d'
                        },
                        metrics: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'Specific metrics to include'
                        },
                        include_competitor_analysis: { type: 'boolean', default: false }
                    }
                }
            },
            {
                name: 'content_calendar',
                description: 'Manage unified content calendar across all platforms',
                inputSchema: {
                    type: 'object',
                    properties: {
                        action: {
                            type: 'string',
                            enum: ['create', 'view', 'update', 'delete'],
                            description: 'Calendar action to perform'
                        },
                        calendar_data: {
                            type: 'object',
                            properties: {
                                start_date: { type: 'string' },
                                end_date: { type: 'string' },
                                content_items: { type: 'array' }
                            }
                        }
                    },
                    required: ['action']
                }
            },
            {
                name: 'engagement_automation',
                description: 'Automate engagement across all platforms (replies, likes, follows)',
                inputSchema: {
                    type: 'object',
                    properties: {
                        automation_type: {
                            type: 'string',
                            enum: ['monitor_mentions', 'auto_reply', 'engagement_boost'],
                            description: 'Type of automation to run'
                        },
                        platforms: {
                            type: 'array',
                            items: { type: 'string', enum: ['facebook', 'instagram', 'twitter'] }
                        },
                        settings: {
                            type: 'object',
                            properties: {
                                auto_reply_templates: { type: 'array' },
                                engagement_rules: { type: 'object' },
                                monitoring_keywords: { type: 'array' }
                            }
                        }
                    },
                    required: ['automation_type', 'platforms']
                }
            },
            {
                name: 'campaign_management',
                description: 'Create and manage multi-platform marketing campaigns',
                inputSchema: {
                    type: 'object',
                    properties: {
                        campaign_name: { type: 'string', description: 'Campaign identifier' },
                        campaign_type: {
                            type: 'string',
                            enum: ['product_launch', 'brand_awareness', 'lead_generation', 'engagement'],
                            description: 'Type of campaign'
                        },
                        duration_days: { type: 'number', description: 'Campaign duration' },
                        budget: { type: 'number', description: 'Total campaign budget' },
                        target_audience: { type: 'object', description: 'Audience targeting parameters' },
                        content_strategy: { type: 'object', description: 'Content plan for campaign' }
                    },
                    required: ['campaign_name', 'campaign_type', 'duration_days']
                }
            }
        ];
    }

    async crossPlatformPost(params) {
        const schema = Joi.object({
            content: Joi.object({
                text: Joi.string().required(),
                image_url: Joi.string().uri().optional(),
                hashtags: Joi.array().items(Joi.string()).optional()
            }).required(),
            platforms: Joi.array().items(Joi.string().valid('facebook', 'instagram', 'twitter')).required(),
            platform_customization: Joi.object().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const results = {};
            const baseContent = value.content;
            const customizations = value.platform_customization || {};

            // Post to each platform with platform-specific optimizations
            for (const platform of value.platforms) {
                try {
                    let platformResult;
                    const platformContent = this.optimizeContentForPlatform(baseContent, platform, customizations[platform]);

                    switch (platform) {
                        case 'facebook':
                            platformResult = await this.facebookServer.handleToolCall('create_facebook_post', {
                                message: platformContent.text,
                                image_url: platformContent.image_url,
                                ...customizations.facebook
                            });
                            break;

                        case 'instagram':
                            if (!platformContent.image_url) {
                                throw new Error('Instagram requires an image');
                            }
                            platformResult = await this.instagramServer.handleToolCall('create_instagram_post', {
                                image_url: platformContent.image_url,
                                caption: platformContent.text,
                                ...customizations.instagram
                            });
                            break;

                        case 'twitter':
                            platformResult = await this.twitterServer.handleToolCall('create_tweet', {
                                text: this.truncateForTwitter(platformContent.text),
                                ...customizations.twitter
                            });
                            break;

                        default:
                            throw new Error(`Unsupported platform: ${platform}`);
                    }

                    results[platform] = {
                        success: !platformResult.error,
                        data: platformResult,
                        content_used: platformContent
                    };

                } catch (platformError) {
                    console.error(`Error posting to ${platform}:`, platformError.message);
                    results[platform] = {
                        success: false,
                        error: platformError.message,
                        content_used: this.optimizeContentForPlatform(baseContent, platform, customizations[platform])
                    };
                }
            }

            const successCount = Object.values(results).filter(r => r.success).length;

            return {
                success: successCount > 0,
                total_platforms: value.platforms.length,
                successful_posts: successCount,
                failed_posts: value.platforms.length - successCount,
                results: results,
                campaign_id: `cross_platform_${Date.now()}`,
                posted_at: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error in cross-platform posting:', error);
            throw new Error(`Failed to post across platforms: ${error.message}`);
        }
    }

    optimizeContentForPlatform(baseContent, platform, customization = {}) {
        let optimizedContent = { ...baseContent };

        switch (platform) {
            case 'facebook':
                // Facebook allows longer content, add more context
                if (baseContent.hashtags) {
                    optimizedContent.text += '\n\n' + baseContent.hashtags.join(' ');
                }
                break;

            case 'instagram':
                // Instagram is visual-first, optimize hashtags
                if (baseContent.hashtags) {
                    optimizedContent.text += '\n\n' + baseContent.hashtags.slice(0, 30).join(' ');
                }
                break;

            case 'twitter':
                // Twitter has character limits, be concise
                optimizedContent.text = this.truncateForTwitter(baseContent.text);
                if (baseContent.hashtags && optimizedContent.text.length < 240) {
                    const remainingChars = 280 - optimizedContent.text.length - 1;
                    const hashtagString = baseContent.hashtags.join(' ');
                    if (hashtagString.length <= remainingChars) {
                        optimizedContent.text += ' ' + hashtagString;
                    }
                }
                break;
        }

        // Apply custom overrides
        return { ...optimizedContent, ...customization };
    }

    truncateForTwitter(text) {
        if (text.length <= 280) return text;
        return text.substring(0, 277) + '...';
    }

    async unifiedAnalytics(params = {}) {
        try {
            const timePeriod = params.time_period || '7d';
            const includeCompetitor = params.include_competitor_analysis || false;

            const analytics = {
                time_period: timePeriod,
                generated_at: new Date().toISOString(),
                platforms: {},
                unified_metrics: {},
                insights: []
            };

            // Gather analytics from each platform
            try {
                const facebookAnalytics = await this.facebookServer.handleToolCall('get_page_insights', {
                    period: timePeriod === '7d' ? 'week' : 'day'
                });
                analytics.platforms.facebook = facebookAnalytics;
            } catch (error) {
                analytics.platforms.facebook = { error: error.message };
            }

            try {
                const instagramAnalytics = await this.instagramServer.handleToolCall('get_instagram_insights', {
                    insight_type: 'account',
                    period: timePeriod === '7d' ? 'week' : 'day'
                });
                analytics.platforms.instagram = instagramAnalytics;
            } catch (error) {
                analytics.platforms.instagram = { error: error.message };
            }

            try {
                const twitterAnalytics = await this.twitterServer.handleToolCall('get_twitter_analytics', {
                    metric_type: 'account',
                    time_period: timePeriod
                });
                analytics.platforms.twitter = twitterAnalytics;
            } catch (error) {
                analytics.platforms.twitter = { error: error.message };
            }

            // Calculate unified metrics
            analytics.unified_metrics = this.calculateUnifiedMetrics(analytics.platforms);

            // Generate insights
            analytics.insights = this.generateUnifiedInsights(analytics.platforms, analytics.unified_metrics);

            return {
                success: true,
                analytics: analytics
            };

        } catch (error) {
            console.error('Error getting unified analytics:', error);
            throw new Error(`Failed to get unified analytics: ${error.message}`);
        }
    }

    calculateUnifiedMetrics(platformData) {
        const metrics = {
            total_followers: 0,
            total_engagement: 0,
            total_reach: 0,
            total_impressions: 0,
            engagement_rate: 0,
            top_performing_platform: null
        };

        let platformScores = {};

        Object.entries(platformData).forEach(([platform, data]) => {
            if (data.error) return;

            let platformMetrics = {};

            // Extract metrics based on platform structure
            if (platform === 'facebook' && data.page_info) {
                platformMetrics = {
                    followers: data.page_info.fan_count || 0,
                    engagement: data.summary?.page_post_engagements || 0,
                    reach: data.summary?.page_impressions || 0
                };
            } else if (platform === 'instagram' && data.account_info) {
                platformMetrics = {
                    followers: data.account_info.followers_count || 0,
                    engagement: data.summary?.impressions || 0,
                    reach: data.summary?.reach || 0
                };
            } else if (platform === 'twitter' && data.analytics?.account_metrics) {
                platformMetrics = {
                    followers: data.analytics.account_metrics.followers_count || 0,
                    engagement: data.analytics.recent_performance?.avg_engagement || 0,
                    reach: data.analytics.recent_performance?.total_tweets || 0
                };
            }

            metrics.total_followers += platformMetrics.followers || 0;
            metrics.total_engagement += platformMetrics.engagement || 0;
            metrics.total_reach += platformMetrics.reach || 0;

            platformScores[platform] = (platformMetrics.followers || 0) + (platformMetrics.engagement || 0);
        });

        // Find top performing platform
        metrics.top_performing_platform = Object.entries(platformScores)
            .reduce((a, b) => platformScores[a[0]] > platformScores[b[0]] ? a : b, ['none', 0])[0];

        // Calculate overall engagement rate
        metrics.engagement_rate = metrics.total_followers > 0 ?
            ((metrics.total_engagement / metrics.total_followers) * 100).toFixed(2) : 0;

        return metrics;
    }

    generateUnifiedInsights(platformData, unifiedMetrics) {
        const insights = [];

        // Platform performance insights
        if (unifiedMetrics.top_performing_platform !== 'none') {
            insights.push({
                type: 'performance',
                message: `${unifiedMetrics.top_performing_platform} is your top performing platform`,
                recommendation: `Focus more content and engagement efforts on ${unifiedMetrics.top_performing_platform}`
            });
        }

        // Engagement insights
        if (unifiedMetrics.engagement_rate < 2) {
            insights.push({
                type: 'engagement',
                message: 'Low engagement rate detected across platforms',
                recommendation: 'Consider posting more interactive content, using trending hashtags, and engaging with your audience'
            });
        } else if (unifiedMetrics.engagement_rate > 5) {
            insights.push({
                type: 'engagement',
                message: 'Excellent engagement rate across platforms',
                recommendation: 'Maintain current content strategy and consider scaling up posting frequency'
            });
        }

        // Cross-platform insights
        const activePlatforms = Object.keys(platformData).filter(p => !platformData[p].error);
        if (activePlatforms.length < 3) {
            insights.push({
                type: 'coverage',
                message: `Only ${activePlatforms.length} platforms are active`,
                recommendation: 'Consider expanding to all three platforms for maximum reach'
            });
        }

        return insights;
    }

    async contentCalendar(params) {
        const schema = Joi.object({
            action: Joi.string().valid('create', 'view', 'update', 'delete').required(),
            calendar_data: Joi.object().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const calendarFile = join(__dirname, 'content_calendar.json');

            switch (value.action) {
                case 'create':
                    const newCalendar = {
                        created_at: new Date().toISOString(),
                        ...value.calendar_data,
                        content_items: value.calendar_data?.content_items || []
                    };

                    writeFileSync(calendarFile, JSON.stringify(newCalendar, null, 2));

                    return {
                        success: true,
                        action: 'create',
                        calendar: newCalendar,
                        message: 'Content calendar created successfully'
                    };

                case 'view':
                    if (!existsSync(calendarFile)) {
                        return {
                            success: true,
                            action: 'view',
                            calendar: { content_items: [] },
                            message: 'No content calendar found'
                        };
                    }

                    const calendar = JSON.parse(readFileSync(calendarFile, 'utf8'));
                    return {
                        success: true,
                        action: 'view',
                        calendar: calendar,
                        upcoming_posts: this.getUpcomingPosts(calendar),
                        overdue_posts: this.getOverduePosts(calendar)
                    };

                case 'update':
                    if (!existsSync(calendarFile)) {
                        throw new Error('No content calendar exists to update');
                    }

                    const existingCalendar = JSON.parse(readFileSync(calendarFile, 'utf8'));
                    const updatedCalendar = { ...existingCalendar, ...value.calendar_data };
                    updatedCalendar.updated_at = new Date().toISOString();

                    writeFileSync(calendarFile, JSON.stringify(updatedCalendar, null, 2));

                    return {
                        success: true,
                        action: 'update',
                        calendar: updatedCalendar,
                        message: 'Content calendar updated successfully'
                    };

                case 'delete':
                    if (existsSync(calendarFile)) {
                        const fs = await import('fs');
                        fs.unlinkSync(calendarFile);
                    }

                    return {
                        success: true,
                        action: 'delete',
                        message: 'Content calendar deleted successfully'
                    };

                default:
                    throw new Error(`Unknown action: ${value.action}`);
            }

        } catch (error) {
            console.error('Error managing content calendar:', error);
            throw new Error(`Failed to manage content calendar: ${error.message}`);
        }
    }

    getUpcomingPosts(calendar) {
        const now = moment();
        return (calendar.content_items || [])
            .filter(item => moment(item.scheduled_time).isAfter(now))
            .sort((a, b) => moment(a.scheduled_time).diff(moment(b.scheduled_time)))
            .slice(0, 10);
    }

    getOverduePosts(calendar) {
        const now = moment();
        return (calendar.content_items || [])
            .filter(item => moment(item.scheduled_time).isBefore(now) && item.status !== 'posted')
            .sort((a, b) => moment(b.scheduled_time).diff(moment(a.scheduled_time)));
    }

    async engagementAutomation(params) {
        const schema = Joi.object({
            automation_type: Joi.string().valid('monitor_mentions', 'auto_reply', 'engagement_boost').required(),
            platforms: Joi.array().items(Joi.string().valid('facebook', 'instagram', 'twitter')).required(),
            settings: Joi.object().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const results = {};

            for (const platform of value.platforms) {
                try {
                    let automationResult;

                    switch (value.automation_type) {
                        case 'monitor_mentions':
                            automationResult = await this.monitorPlatformMentions(platform, value.settings);
                            break;
                        case 'auto_reply':
                            automationResult = await this.autoReplyPlatform(platform, value.settings);
                            break;
                        case 'engagement_boost':
                            automationResult = await this.boostEngagement(platform, value.settings);
                            break;
                        default:
                            throw new Error(`Unknown automation type: ${value.automation_type}`);
                    }

                    results[platform] = {
                        success: true,
                        data: automationResult
                    };

                } catch (platformError) {
                    results[platform] = {
                        success: false,
                        error: platformError.message
                    };
                }
            }

            return {
                success: true,
                automation_type: value.automation_type,
                platforms: value.platforms,
                results: results,
                executed_at: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error in engagement automation:', error);
            throw new Error(`Failed to run engagement automation: ${error.message}`);
        }
    }

    async monitorPlatformMentions(platform, settings) {
        switch (platform) {
            case 'facebook':
                return await this.facebookServer.handleToolCall('manage_comments', { action: 'list' });
            case 'instagram':
                return await this.instagramServer.handleToolCall('manage_instagram_comments', { action: 'list' });
            case 'twitter':
                return await this.twitterServer.handleToolCall('monitor_mentions', { action: 'list' });
            default:
                throw new Error(`Unsupported platform for mention monitoring: ${platform}`);
        }
    }

    async autoReplyPlatform(platform, settings) {
        // Simplified auto-reply implementation
        const templates = settings?.auto_reply_templates || [
            "Thank you for your comment! We appreciate your feedback.",
            "Thanks for reaching out! We'll get back to you soon.",
            "We're glad you're interested! Check out our latest updates."
        ];

        return {
            platform: platform,
            templates_configured: templates.length,
            auto_reply_enabled: true,
            message: `Auto-reply configured for ${platform} with ${templates.length} templates`
        };
    }

    async boostEngagement(platform, settings) {
        // Simplified engagement boost implementation
        return {
            platform: platform,
            engagement_actions: ['like_recent_comments', 'follow_relevant_accounts', 'share_trending_content'],
            boost_enabled: true,
            message: `Engagement boost activated for ${platform}`
        };
    }

    async campaignManagement(params) {
        const schema = Joi.object({
            campaign_name: Joi.string().required(),
            campaign_type: Joi.string().valid('product_launch', 'brand_awareness', 'lead_generation', 'engagement').required(),
            duration_days: Joi.number().positive().required(),
            budget: Joi.number().positive().optional(),
            target_audience: Joi.object().optional(),
            content_strategy: Joi.object().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const campaign = {
                id: `campaign_${Date.now()}`,
                name: value.campaign_name,
                type: value.campaign_type,
                duration_days: value.duration_days,
                budget: value.budget || 0,
                target_audience: value.target_audience || {},
                content_strategy: value.content_strategy || {},
                created_at: new Date().toISOString(),
                start_date: moment().format('YYYY-MM-DD'),
                end_date: moment().add(value.duration_days, 'days').format('YYYY-MM-DD'),
                status: 'created',
                platforms: ['facebook', 'instagram', 'twitter'],
                metrics: {
                    posts_scheduled: 0,
                    total_reach: 0,
                    total_engagement: 0,
                    leads_generated: 0
                }
            };

            // Save campaign
            const campaignFile = join(__dirname, `campaign_${campaign.id}.json`);
            writeFileSync(campaignFile, JSON.stringify(campaign, null, 2));

            return {
                success: true,
                campaign: campaign,
                next_steps: [
                    'Create content calendar for campaign',
                    'Set up tracking and analytics',
                    'Schedule initial posts',
                    'Monitor campaign performance'
                ],
                message: `Campaign "${value.campaign_name}" created successfully`
            };

        } catch (error) {
            console.error('Error creating campaign:', error);
            throw new Error(`Failed to create campaign: ${error.message}`);
        }
    }

    // MCP Server Interface Methods
    async handleToolCall(toolName, params) {
        try {
            switch (toolName) {
                case 'cross_platform_post':
                    return await this.crossPlatformPost(params);
                case 'unified_analytics':
                    return await this.unifiedAnalytics(params);
                case 'content_calendar':
                    return await this.contentCalendar(params);
                case 'engagement_automation':
                    return await this.engagementAutomation(params);
                case 'campaign_management':
                    return await this.campaignManagement(params);
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
        console.log('🌐 Unified Social Media Manager starting...');

        console.log('✅ Unified Social Media Manager ready for Gold Tier operations!');
        console.log('📊 Platforms: Facebook, Instagram, Twitter');
        console.log('🔧 Features: Cross-platform posting, Unified analytics, Campaign management');

        // Keep server running
        process.stdin.resume();
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const manager = new UnifiedSocialMediaManager();
    manager.start().catch(console.error);
}

export default UnifiedSocialMediaManager;