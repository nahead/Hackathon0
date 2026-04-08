# LinkedIn OAuth Setup Guide

Complete step-by-step guide to get LinkedIn posting working.

## 📋 Overview

You need 2 things:
1. **LINKEDIN_ACCESS_TOKEN** - For API authentication
2. **LINKEDIN_PERSON_URN** - Your LinkedIn profile ID

---

## 🚀 Method 1: Quick Setup (Recommended)

### Important: Enable LinkedIn Posting Permission First

Before starting, you need to enable posting permission in LinkedIn Developer Portal:

1. Go to: https://www.linkedin.com/developers/apps
2. Click on your app (or create new app if needed)
3. Go to **"Products"** tab
4. Find **"Share on LinkedIn"** product
5. Click **"Request access"**
6. Fill out the form and submit
7. **Wait for approval** (can take 1-3 days)

**Note:** Without this approval, you'll get "invalid_scope_error"

### Step 1: Open Authorization URL (After Approval)

Copy this URL and open in your browser:

```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=777mj195y7yyos&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20email%20w_member_social
```

**If you get "invalid_scope_error":** The app doesn't have posting permission yet. Wait for LinkedIn approval.

**Alternative (Get credentials without posting):**
Use this URL to at least get your access token and person URN:
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=777mj195y7yyos&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20email
```

### Step 2: Authorize the App

1. Login to LinkedIn (if not already logged in)
2. Click **"Allow"** to authorize the application
3. You will be redirected to: `http://localhost:8080/callback?code=XXXXX`
4. **Copy the code** from the URL (the part after `code=`)

Example:
```
http://localhost:8080/callback?code=AQTxxx...xxx
                                    ^^^^^^^^^^^^
                                    Copy this part
```

### Step 3: Exchange Code for Access Token

Run this command (replace YOUR_CODE with the code you copied, and get CLIENT_SECRET from your .env file):

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "client_id=777mj195y7yyos" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

**Note:** Get YOUR_CLIENT_SECRET from your .env file (LINKEDIN_CLIENT_SECRET value)

**Response will look like:**
```json
{
  "access_token": "AQV8xxx...xxx",
  "expires_in": 5184000
}
```

**Copy the access_token value!**

### Step 4: Get Your Person URN

Run this command (replace YOUR_ACCESS_TOKEN):

```bash
curl -X GET https://api.linkedin.com/v2/userinfo \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response will look like:**
```json
{
  "sub": "abc123xyz",
  "name": "Your Name",
  "email": "your@email.com"
}
```

**Copy the "sub" value!**

Your Person URN is: `urn:li:person:abc123xyz`

---

## 💻 Local Setup

Update your `.env` file:

```bash
LINKEDIN_ACCESS_TOKEN=AQV8xxx...xxx
LINKEDIN_PERSON_URN=urn:li:person:abc123xyz
```

Test it:
```bash
DRY_RUN=false python test_linkedin_poster.py
```

---

## ☁️ Cloud Setup (Render.com)

### Step 1: Go to Render Dashboard

1. Open: https://dashboard.render.com
2. Login to your account
3. Find your service: **ai-employee-cloud**

### Step 2: Add Environment Variables

1. Click on your service
2. Go to **"Environment"** tab (left sidebar)
3. Click **"Add Environment Variable"**

Add these 2 variables:

**Variable 1:**
- Key: `LINKEDIN_ACCESS_TOKEN`
- Value: `AQV8xxx...xxx` (your access token)

**Variable 2:**
- Key: `LINKEDIN_PERSON_URN`
- Value: `urn:li:person:abc123xyz` (your person URN)

### Step 3: Save and Deploy

1. Click **"Save Changes"**
2. Service will automatically redeploy (takes 2-3 minutes)
3. Check logs to verify deployment

---

## ✅ Verification

### Local Test:
```bash
# Move a post to Approved folder
mv AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/

# Post it (for real)
DRY_RUN=false python test_linkedin_poster.py
```

### Cloud Test:
1. Create a LinkedIn post approval file
2. Push to GitHub
3. Cloud will automatically post it within 5 minutes
4. Check your LinkedIn profile!

---

## 🔧 Troubleshooting

### "Invalid authorization code"
- Code expires in 30 seconds
- Get a new code and try again quickly

### "Invalid access token"
- Token expires after 60 days
- Generate a new token using Step 1-3

### "403 Forbidden"
- Check if w_member_social scope is included
- Verify Person URN is correct format

---

## 📝 Notes

- Access token expires after **60 days**
- You'll need to refresh it after expiry
- Keep credentials secure (never commit to git)
- Free tier allows unlimited posts

---

## 🎯 Quick Commands

```bash
# Generate content
python test_linkedin_content.py

# Approve a post
mv AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md AI_Employee_Vault/Approved/

# Post locally (dry run)
DRY_RUN=true python test_linkedin_poster.py

# Post locally (for real)
DRY_RUN=false python test_linkedin_poster.py
```

---

## 🌐 Cloud Workflow

Once credentials are set on Render.com:

1. Create LinkedIn posts locally
2. Move to Approved/ folder
3. Push to GitHub
4. Cloud automatically posts within 5 minutes
5. Check Done/ folder for confirmation

**Completely automated and FREE!**
