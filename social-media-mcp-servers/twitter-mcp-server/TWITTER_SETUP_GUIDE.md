---
type: twitter_api_setup_guide
created: 2026-02-23T20:11:13.765033
status: setup_required
---

# Twitter API v2 Setup Guide

## Step 1: Twitter Developer Account
1. Go to: https://developer.twitter.com/
2. Apply for Developer Account
3. Describe use case: "Business automation and social media management"
4. Wait for approval (usually 1-2 days)

## Step 2: Create Twitter App
1. Developer Portal → Projects & Apps
2. Create New App
3. App Name: "AI Employee Social Manager"
4. Description: "Automated business social media management"

## Step 3: Configure App Permissions
Required permissions:
- **Read**: Access tweets and user information
- **Write**: Post tweets and manage content
- **Direct Messages**: Handle customer inquiries (optional)

## Step 4: Get API Credentials
1. App Dashboard → Keys and Tokens
2. Generate and copy:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Bearer Token**
   - **Access Token**
   - **Access Token Secret**

```env
# Twitter API Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## Step 5: Test API Connection
```bash
cd social-media-mcp-servers/twitter-mcp-server
npm install
npm start
```

## Step 6: Verify Permissions
Test basic operations:
- Read timeline
- Post tweet
- Get user information
- Access analytics

## Business Use Cases
- **Thought Leadership**: Industry insights and expertise
- **Customer Engagement**: Respond to mentions and DMs
- **Brand Awareness**: Consistent business messaging
- **Lead Generation**: Strategic hashtag and content optimization

## Content Strategy
- **Professional Updates**: Business milestones and achievements
- **Industry Insights**: Share relevant business knowledge
- **Customer Success**: Highlight client testimonials
- **Engagement**: Participate in industry conversations

## Current Status
- ✅ MCP server framework created
- ✅ Package.json configured
- ⚠️ Requires Twitter Developer approval
- ⚠️ Requires API credentials

## Analytics Integration
- Tweet performance metrics
- Engagement rate tracking
- Follower growth analysis
- Optimal posting time identification

---
*Twitter Integration Setup Guide - Gold Tier Phase 2B*
