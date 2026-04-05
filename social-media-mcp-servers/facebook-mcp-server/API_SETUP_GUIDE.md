
# 🔵 Facebook API Setup - Step by Step

## Step 1: Facebook Developer Account (5 mins)
1. Go to: https://developers.facebook.com/
2. Click "Get Started"
3. Use your existing Facebook account
4. Complete developer registration
5. Verify phone number if required

## Step 2: Create Facebook App (3 mins)
1. Click "Create App" → Select "Business" type
2. App Name: "AI Employee Social Manager"
3. Contact Email: naheadj@gmail.com
4. Select Business Account (create if needed)
5. Click "Create App"

## Step 3: Configure App Settings (5 mins)
1. App Dashboard → Settings → Basic
2. Copy these values:
   - **App ID**: [COPY THIS]
   - **App Secret**: [COPY THIS - Click Show]
3. Add Platform → Website
4. Site URL: http://localhost:3000

## Step 4: Add Facebook Login Product (2 mins)
1. App Dashboard → Add Product
2. Find "Facebook Login" → Click "Set Up"
3. Settings → Valid OAuth Redirect URIs:
   - http://localhost:3000/auth/facebook/callback

## Step 5: Add Pages API Product (2 mins)
1. App Dashboard → Add Product
2. Find "Pages API" → Click "Set Up"
3. This enables page posting capabilities

## Step 6: Get Page Access Token (10 mins)
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click "Generate Access Token"
4. Select permissions:
   - pages_manage_posts
   - pages_read_engagement
   - pages_show_list
5. Click "Generate Access Token"
6. **IMPORTANT**: Extend token to long-lived (60 days)
   - Use Access Token Debugger
   - Click "Extend Access Token"

## Step 7: Get Page ID (2 mins)
1. Go to your Facebook Business Page
2. Settings → Page Info
3. Copy Page ID number

## Step 8: Test API Connection
```bash
# Test with curl
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
```

## Environment Variables (.env)
```env
# Facebook API Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token
FACEBOOK_PAGE_ID=your_page_id_here
```

## ✅ Success Indicators
- App created successfully
- Access token generated and extended
- Page ID obtained
- Test API call returns page data

---
*Facebook API Setup Complete - Ready for Integration*
