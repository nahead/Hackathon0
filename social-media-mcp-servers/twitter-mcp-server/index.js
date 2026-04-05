#!/usr/bin/env node

/**
 * Twitter/X MCP Server for Gold Tier AI Employee
 * Provides comprehensive Twitter account management and marketing automation
 */

import axios from 'axios';
import Joi from 'joi';
import dotenv from 'dotenv';
import OAuth from 'oauth-1.0a';
import crypto from 'crypto';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class TwitterMCPServer {
    constructor() {
        this.bearerToken = process.env.TWITTER_BEARER_TOKEN;
        this.apiKey = process.env.TWITTER_API_KEY;
        this.apiSecret = process.env.TWITTER_API_SECRET;
        this.accessToken = process.env.TWITTER_ACCESS_TOKEN;
        this.accessTokenSecret = process.env.TWITTER_ACCESS_TOKEN_SECRET;
        this.baseUrl = 'https://api.twitter.com/2';

        // Setup OAuth 1.0a for authenticated requests
        this.oauth = OAuth({
            consumer: { key: this.apiKey, secret: this.apiSecret },
            signature_method: 'HMAC-SHA1',
            hash_function(base_string, key) {
                return crypto.createHmac('sha1', key).update(base_string).digest('base64');
            }
        });

        this.setupServer();
    }

    setupServer() {
        console.log('🐦 Starting Twitter/X MCP Server for Gold Tier AI Employee...');

        // Initialize server capabilities
        this.tools = [
            {
                name: 'create_tweet',
                description: 'Create and publish a tweet',
                inputSchema: {
                    type: 'object',
                    properties: {
                        text: { type: 'string', description: 'Tweet content (max 280 characters)' },
                        media_ids: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'Media IDs for images/videos'
                        },
                        reply_to: { type: 'string', description: 'Tweet ID to reply to' },
                        quote_tweet_id: { type: 'string', description: 'Tweet ID to quote' },
                        poll: {
                            type: 'object',
                            properties: {
                                options: { type: 'array', items: { type: 'string' } },
                                duration_minutes: { type: 'number', default: 1440 }
                            }
                        }
                    },
                    required: ['text']
                }
            },
            {
                name: 'create_thread',
                description: 'Create a Twitter thread with multiple tweets',
                inputSchema: {
                    type: 'object',
                    properties: {
                        tweets: {
                            type: 'array',
                            items: {
                                type: 'object',
                                properties: {
                                    text: { type: 'string' },
                                    media_ids: { type: 'array', items: { type: 'string' } }
                                }
                            },
                            description: 'Array of tweet objects for the thread'
                        },
                        thread_title: { type: 'string', description: 'Optional thread title' }
                    },
                    required: ['tweets']
                }
            },
            {
                name: 'get_twitter_analytics',
                description: 'Get Twitter account analytics and metrics',
                inputSchema: {
                    type: 'object',
                    properties: {
                        metric_type: {
                            type: 'string',
                            enum: ['account', 'tweet', 'engagement'],
                            default: 'account'
                        },
                        tweet_id: { type: 'string', description: 'Tweet ID for tweet-specific metrics' },
                        time_period: {
                            type: 'string',
                            enum: ['1d', '7d', '30d'],
                            default: '7d'
                        }
                    }
                }
            },
            {
                name: 'monitor_mentions',
                description: 'Monitor and manage Twitter mentions and replies',
                inputSchema: {
                    type: 'object',
                    properties: {
                        action: {
                            type: 'string',
                            enum: ['list', 'reply', 'like', 'retweet'],
                            description: 'Action to perform on mentions'
                        },
                        mention_id: { type: 'string', description: 'Mention tweet ID for actions' },
                        reply_text: { type: 'string', description: 'Reply message content' },
                        max_results: { type: 'number', default: 10, maximum: 100 }
                    },
                    required: ['action']
                }
            },
            {
                name: 'track_trends',
                description: 'Monitor trending topics and hashtags',
                inputSchema: {
                    type: 'object',
                    properties: {
                        location: { type: 'string', description: 'Location for trends (WOEID)', default: '1' },
                        keywords: {
                            type: 'array',
                            items: { type: 'string' },
                            description: 'Keywords to track in trends'
                        },
                        industry_focus: { type: 'string', description: 'Industry to focus trend analysis on' }
                    }
                }
            },
            {
                name: 'schedule_tweets',
                description: 'Schedule tweets for optimal engagement times',
                inputSchema: {
                    type: 'object',
                    properties: {
                        scheduled_tweets: {
                            type: 'array',
                            items: {
                                type: 'object',
                                properties: {
                                    text: { type: 'string' },
                                    scheduled_time: { type: 'string' },
                                    media_ids: { type: 'array', items: { type: 'string' } }
                                }
                            }
                        },
                        timezone: { type: 'string', default: 'UTC' },
                        auto_optimize: { type: 'boolean', default: true }
                    },
                    required: ['scheduled_tweets']
                }
            }
        ];
    }

    async makeAuthenticatedRequest(endpoint, method = 'GET', data = null) {
        try {
            const url = `${this.baseUrl}${endpoint}`;

            const requestData = {
                url: url,
                method: method
            };

            const token = {
                key: this.accessToken,
                secret: this.accessTokenSecret
            };

            const authHeader = this.oauth.toHeader(this.oauth.authorize(requestData, token));

            const config = {
                method,
                url,
                headers: {
                    ...authHeader,
                    'Content-Type': 'application/json'
                }
            };

            if (data && method !== 'GET') {
                config.data = data;
            }

            const response = await axios(config);
            return response.data;
        } catch (error) {
            console.error(`Twitter API error: ${error.response?.data?.detail || error.message}`);
            throw new Error(`Twitter API call failed: ${error.response?.data?.detail || error.message}`);
        }
    }

    async makeBearerTokenRequest(endpoint, params = {}) {
        try {
            const response = await axios.get(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Authorization': `Bearer ${this.bearerToken}`
                },
                params
            });
            return response.data;
        } catch (error) {
            console.error(`Twitter API error: ${error.response?.data?.detail || error.message}`);
            throw new Error(`Twitter API call failed: ${error.response?.data?.detail || error.message}`);
        }
    }

    async createTweet(params) {
        const schema = Joi.object({
            text: Joi.string().max(280).required(),
            media_ids: Joi.array().items(Joi.string()).optional(),
            reply_to: Joi.string().optional(),
            quote_tweet_id: Joi.string().optional(),
            poll: Joi.object({
                options: Joi.array().items(Joi.string()).min(2).max(4),
                duration_minutes: Joi.number().min(5).max(10080).default(1440)
            }).optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const tweetData = {
                text: value.text
            };

            if (value.media_ids && value.media_ids.length > 0) {
                tweetData.media = { media_ids: value.media_ids };
            }

            if (value.reply_to) {
                tweetData.reply = { in_reply_to_tweet_id: value.reply_to };
            }

            if (value.quote_tweet_id) {
                tweetData.quote_tweet_id = value.quote_tweet_id;
            }

            if (value.poll) {
                tweetData.poll = {
                    options: value.poll.options,
                    duration_minutes: value.poll.duration_minutes
                };
            }

            const result = await this.makeAuthenticatedRequest('/tweets', 'POST', tweetData);

            return {
                success: true,
                tweet_id: result.data.id,
                tweet_text: result.data.text,
                tweet_url: `https://twitter.com/user/status/${result.data.id}`,
                character_count: value.text.length,
                created_at: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error creating tweet:', error);
            throw new Error(`Failed to create tweet: ${error.message}`);
        }
    }

    async createThread(params) {
        const schema = Joi.object({
            tweets: Joi.array().items(Joi.object({
                text: Joi.string().max(280).required(),
                media_ids: Joi.array().items(Joi.string()).optional()
            })).min(2).required(),
            thread_title: Joi.string().optional()
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            const threadResults = [];
            let previousTweetId = null;

            for (let i = 0; i < value.tweets.length; i++) {
                const tweet = value.tweets[i];
                const tweetData = {
                    text: tweet.text
                };

                if (tweet.media_ids && tweet.media_ids.length > 0) {
                    tweetData.media = { media_ids: tweet.media_ids };
                }

                if (previousTweetId) {
                    tweetData.reply = { in_reply_to_tweet_id: previousTweetId };
                }

                const result = await this.makeAuthenticatedRequest('/tweets', 'POST', tweetData);

                threadResults.push({
                    tweet_id: result.data.id,
                    text: result.data.text,
                    position: i + 1
                });

                previousTweetId = result.data.id;

                // Add delay between tweets to avoid rate limiting
                if (i < value.tweets.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }

            return {
                success: true,
                thread_id: threadResults[0].tweet_id,
                thread_url: `https://twitter.com/user/status/${threadResults[0].tweet_id}`,
                tweets: threadResults,
                total_tweets: threadResults.length,
                thread_title: value.thread_title
            };

        } catch (error) {
            console.error('Error creating thread:', error);
            throw new Error(`Failed to create thread: ${error.message}`);
        }
    }

    async getTwitterAnalytics(params = {}) {
        try {
            const metricType = params.metric_type || 'account';
            const timePeriod = params.time_period || '7d';

            let analytics = {};

            switch (metricType) {
                case 'account':
                    // Get user info and recent tweets for analysis
                    const userInfo = await this.makeBearerTokenRequest('/users/me', {
                        'user.fields': 'public_metrics,created_at,description,location,verified'
                    });

                    const recentTweets = await this.makeBearerTokenRequest('/users/me/tweets', {
                        'tweet.fields': 'public_metrics,created_at,context_annotations',
                        max_results: 10
                    });

                    analytics = {
                        account_metrics: userInfo.data.public_metrics,
                        account_info: {
                            username: userInfo.data.username,
                            name: userInfo.data.name,
                            verified: userInfo.data.verified,
                            created_at: userInfo.data.created_at
                        },
                        recent_performance: this.calculateRecentPerformance(recentTweets.data || [])
                    };
                    break;

                case 'tweet':
                    if (!params.tweet_id) {
                        throw new Error('Tweet ID required for tweet analytics');
                    }

                    const tweetData = await this.makeBearerTokenRequest(`/tweets/${params.tweet_id}`, {
                        'tweet.fields': 'public_metrics,created_at,context_annotations,referenced_tweets'
                    });

                    analytics = {
                        tweet_id: params.tweet_id,
                        metrics: tweetData.data.public_metrics,
                        created_at: tweetData.data.created_at,
                        engagement_rate: this.calculateEngagementRate(tweetData.data.public_metrics)
                    };
                    break;

                case 'engagement':
                    // Get mentions and interactions
                    const mentions = await this.makeBearerTokenRequest('/users/me/mentions', {
                        'tweet.fields': 'public_metrics,created_at,author_id',
                        max_results: 20
                    });

                    analytics = {
                        recent_mentions: mentions.data?.length || 0,
                        mention_details: mentions.data || [],
                        engagement_summary: this.analyzeEngagement(mentions.data || [])
                    };
                    break;

                default:
                    throw new Error(`Unknown metric type: ${metricType}`);
            }

            return {
                success: true,
                metric_type: metricType,
                time_period: timePeriod,
                analytics: analytics,
                generated_at: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error getting Twitter analytics:', error);
            throw new Error(`Failed to get Twitter analytics: ${error.message}`);
        }
    }

    calculateRecentPerformance(tweets) {
        if (!tweets || tweets.length === 0) return { avg_engagement: 0, total_tweets: 0 };

        const totalEngagement = tweets.reduce((sum, tweet) => {
            const metrics = tweet.public_metrics;
            return sum + (metrics.like_count + metrics.retweet_count + metrics.reply_count + metrics.quote_count);
        }, 0);

        return {
            avg_engagement: Math.round(totalEngagement / tweets.length),
            total_tweets: tweets.length,
            avg_likes: Math.round(tweets.reduce((sum, t) => sum + t.public_metrics.like_count, 0) / tweets.length),
            avg_retweets: Math.round(tweets.reduce((sum, t) => sum + t.public_metrics.retweet_count, 0) / tweets.length)
        };
    }

    calculateEngagementRate(metrics) {
        const totalEngagement = metrics.like_count + metrics.retweet_count + metrics.reply_count + metrics.quote_count;
        const impressions = metrics.impression_count || 1;
        return ((totalEngagement / impressions) * 100).toFixed(2);
    }

    analyzeEngagement(mentions) {
        return {
            total_mentions: mentions.length,
            avg_mention_engagement: mentions.length > 0 ?
                Math.round(mentions.reduce((sum, m) => sum + (m.public_metrics?.like_count || 0), 0) / mentions.length) : 0,
            recent_activity: mentions.slice(0, 5).map(m => ({
                id: m.id,
                text: m.text.substring(0, 100) + '...',
                author_id: m.author_id,
                created_at: m.created_at
            }))
        };
    }

    async monitorMentions(params) {
        const schema = Joi.object({
            action: Joi.string().valid('list', 'reply', 'like', 'retweet').required(),
            mention_id: Joi.string().optional(),
            reply_text: Joi.string().optional(),
            max_results: Joi.number().min(1).max(100).default(10)
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            switch (value.action) {
                case 'list':
                    const mentions = await this.makeBearerTokenRequest('/users/me/mentions', {
                        'tweet.fields': 'public_metrics,created_at,author_id,context_annotations',
                        'user.fields': 'username,name,verified',
                        expansions: 'author_id',
                        max_results: value.max_results
                    });

                    return {
                        success: true,
                        action: 'list',
                        mentions: mentions.data || [],
                        users: mentions.includes?.users || [],
                        count: mentions.data?.length || 0
                    };

                case 'reply':
                    if (!value.mention_id || !value.reply_text) {
                        throw new Error('Mention ID and reply text required for reply action');
                    }

                    const replyResult = await this.createTweet({
                        text: value.reply_text,
                        reply_to: value.mention_id
                    });

                    return {
                        success: true,
                        action: 'reply',
                        reply_tweet_id: replyResult.tweet_id,
                        original_mention_id: value.mention_id
                    };

                case 'like':
                    if (!value.mention_id) {
                        throw new Error('Mention ID required for like action');
                    }

                    await this.makeAuthenticatedRequest('/users/me/likes', 'POST', {
                        tweet_id: value.mention_id
                    });

                    return {
                        success: true,
                        action: 'like',
                        liked_tweet_id: value.mention_id
                    };

                case 'retweet':
                    if (!value.mention_id) {
                        throw new Error('Mention ID required for retweet action');
                    }

                    await this.makeAuthenticatedRequest('/users/me/retweets', 'POST', {
                        tweet_id: value.mention_id
                    });

                    return {
                        success: true,
                        action: 'retweet',
                        retweeted_tweet_id: value.mention_id
                    };

                default:
                    throw new Error(`Unknown action: ${value.action}`);
            }

        } catch (error) {
            console.error('Error monitoring mentions:', error);
            throw new Error(`Failed to monitor mentions: ${error.message}`);
        }
    }

    async trackTrends(params = {}) {
        try {
            // Note: Twitter API v2 doesn't have direct trends endpoint
            // This is a simplified implementation using search
            const location = params.location || '1'; // Worldwide
            const keywords = params.keywords || [];

            let trends = [];

            if (keywords.length > 0) {
                // Search for specific keywords
                for (const keyword of keywords) {
                    try {
                        const searchResult = await this.makeBearerTokenRequest('/tweets/search/recent', {
                            query: keyword,
                            'tweet.fields': 'public_metrics,created_at,context_annotations',
                            max_results: 10
                        });

                        const keywordMetrics = this.analyzeTrendKeyword(searchResult.data || [], keyword);
                        trends.push(keywordMetrics);
                    } catch (searchError) {
                        console.warn(`Could not search for keyword ${keyword}:`, searchError.message);
                    }
                }
            } else {
                // General trending analysis (simplified)
                trends = [
                    { keyword: 'trending_analysis', note: 'Requires Twitter API v1.1 for full trends data' }
                ];
            }

            return {
                success: true,
                location: location,
                trends: trends,
                keywords_tracked: keywords,
                industry_focus: params.industry_focus,
                generated_at: new Date().toISOString()
            };

        } catch (error) {
            console.error('Error tracking trends:', error);
            throw new Error(`Failed to track trends: ${error.message}`);
        }
    }

    analyzeTrendKeyword(tweets, keyword) {
        const totalEngagement = tweets.reduce((sum, tweet) => {
            const metrics = tweet.public_metrics;
            return sum + (metrics.like_count + metrics.retweet_count + metrics.reply_count);
        }, 0);

        return {
            keyword: keyword,
            tweet_count: tweets.length,
            total_engagement: totalEngagement,
            avg_engagement: tweets.length > 0 ? Math.round(totalEngagement / tweets.length) : 0,
            recent_tweets: tweets.slice(0, 3).map(t => ({
                id: t.id,
                text: t.text.substring(0, 100) + '...',
                metrics: t.public_metrics
            }))
        };
    }

    async scheduleTweets(params) {
        const schema = Joi.object({
            scheduled_tweets: Joi.array().items(Joi.object({
                text: Joi.string().max(280).required(),
                scheduled_time: Joi.string().required(),
                media_ids: Joi.array().items(Joi.string()).optional()
            })).required(),
            timezone: Joi.string().default('UTC'),
            auto_optimize: Joi.boolean().default(true)
        });

        const { error, value } = schema.validate(params);
        if (error) {
            throw new Error(`Validation error: ${error.details[0].message}`);
        }

        try {
            // This is a simplified scheduling implementation
            // In production, you'd use a job scheduler like cron or a service like Buffer/Hootsuite
            const scheduledTweets = value.scheduled_tweets.map((tweet, index) => ({
                id: `scheduled_${Date.now()}_${index}`,
                text: tweet.text,
                scheduled_time: tweet.scheduled_time,
                media_ids: tweet.media_ids || [],
                status: 'scheduled',
                timezone: value.timezone
            }));

            return {
                success: true,
                scheduled_tweets: scheduledTweets,
                total_scheduled: scheduledTweets.length,
                timezone: value.timezone,
                auto_optimize: value.auto_optimize,
                message: 'Tweets scheduled successfully',
                note: 'Requires external scheduling service for actual posting'
            };

        } catch (error) {
            console.error('Error scheduling tweets:', error);
            throw new Error(`Failed to schedule tweets: ${error.message}`);
        }
    }

    // MCP Server Interface Methods
    async handleToolCall(toolName, params) {
        try {
            switch (toolName) {
                case 'create_tweet':
                    return await this.createTweet(params);
                case 'create_thread':
                    return await this.createThread(params);
                case 'get_twitter_analytics':
                    return await this.getTwitterAnalytics(params);
                case 'monitor_mentions':
                    return await this.monitorMentions(params);
                case 'track_trends':
                    return await this.trackTrends(params);
                case 'schedule_tweets':
                    return await this.scheduleTweets(params);
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
        console.log('🐦 Twitter/X MCP Server starting...');

        if (!this.bearerToken || !this.apiKey || !this.accessToken) {
            console.error('❌ Twitter credentials not configured. Please set TWITTER_BEARER_TOKEN, TWITTER_API_KEY, and TWITTER_ACCESS_TOKEN');
            process.exit(1);
        }

        console.log('✅ Twitter/X MCP Server ready for Gold Tier operations!');
        console.log(`🔧 API Version: v2`);
        console.log(`📊 Authentication: OAuth 1.0a + Bearer Token`);

        // Keep server running
        process.stdin.resume();
    }
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
    const server = new TwitterMCPServer();
    server.start().catch(console.error);
}

export default TwitterMCPServer;