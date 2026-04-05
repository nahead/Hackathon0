
# 🐦 Twitter API Setup - Step by Step

## Step 1: Twitter Developer Account (Application Required)
1. Go to: https://developer.twitter.com/
2. Click "Apply for a developer account"
3. Use case: "Business automation and social media management"
4. Describe your use case in detail:
   - "Building AI-powered business automation system"
   - "Automated professional posting and customer engagement"
   - "Social media management for business growth"
5. Submit application
6. **Wait for approval** (usually 1-2 days)

## Step 2: Create Twitter App (After Approval)
1. Developer Portal → Projects & Apps
2. Create New Project
3. Project Name: "AI Employee Business Manager"
4. Use Case: "Making a bot"
5. Description: "Automated business social media management"

## Step 3: Create App in Project
1. App Name: "AI Employee Social Manager"
2. Environment: Development (can upgrade later)
3. Complete app creation

## Step 4: Configure App Settings (5 mins)
1. App Dashboard → Settings
2. App permissions: Read and Write
3. Type of App: Web App
4. Callback URLs: http://localhost:3000/auth/twitter/callback
5. Website URL: http://localhost:3000
6. Terms of Service: (your business terms)
7. Privacy Policy: (your business privacy policy)

## Step 5: Generate API Keys (3 mins)
1. App Dashboard → Keys and Tokens
2. Generate/Regenerate:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Bearer Token**
   - **Access Token**
   - **Access Token Secret**
3. **IMPORTANT**: Save all keys immediately

## Step 6: Test API Connection
```bash
# Test with curl using Bearer Token
curl -X GET "https://api.twitter.com/2/users/me" -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```

## Environment Variables (.env)
```env
# Twitter API Configuration
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

## ✅ Success Indicators
- Developer account approved
- App created with Read/Write permissions
- All 5 API keys generated
- Test API call returns user info

## ⚠️ Important Notes
- Twitter approval can take 1-2 days
- Be specific about business use case
- Keep API keys secure and private
- Monitor API usage limits

---
*Twitter API Setup Complete - Ready for Integration*
