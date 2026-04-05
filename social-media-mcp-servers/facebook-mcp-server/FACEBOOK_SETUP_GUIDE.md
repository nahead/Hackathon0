---
type: facebook_api_setup_guide
created: 2026-02-23T20:11:13.759872
status: setup_required
---

# Facebook Business API Setup Guide

## Step 1: Facebook Developer Account
1. Go to: https://developers.facebook.com/
2. Create Developer Account (if not exists)
3. Verify account with phone number

## Step 2: Create Facebook App
1. Click "Create App" → "Business" type
2. App Name: "AI Employee Social Manager"
3. Contact Email: Your business email
4. Business Account: Select or create

## Step 3: Configure App Permissions
Required permissions for business posting:
- **pages_manage_posts**: Post to business pages
- **pages_read_engagement**: Read post analytics
- **pages_show_list**: Access page information
- **business_management**: Manage business assets

## Step 4: Get API Credentials
1. Go to App Dashboard → Settings → Basic
2. Copy **App ID** and **App Secret**
3. Add to .env file:

```env
# Facebook API Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

## Step 5: Generate Access Token
1. Go to Graph API Explorer
2. Select your app
3. Add permissions: pages_manage_posts, pages_read_engagement
4. Generate token
5. Extend token to long-lived (60 days)

## Step 6: Get Page ID
1. Go to your Facebook Business Page
2. Settings → Page Info
3. Copy Page ID

## Step 7: Test API Connection
```bash
cd social-media-mcp-servers/facebook-mcp-server
npm install
npm start
```

## Current Status
- ✅ MCP server framework created
- ✅ Package.json configured
- ⚠️ Requires Facebook Developer setup
- ⚠️ Requires API credentials

## Business Use Cases
- Automated business post scheduling
- Customer engagement analytics
- Lead generation post optimization
- Brand awareness campaigns

---
*Facebook Integration Setup Guide - Gold Tier Phase 2B*
