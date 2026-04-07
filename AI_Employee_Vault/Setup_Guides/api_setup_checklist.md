---
type: api_setup_checklist
created: 2026-02-23T20:26:20.147883
status: pending_setup
---

# 🚀 API Credentials Setup Checklist - Gold Tier Final Phase

## 📋 Setup Priority Order

### Phase 1: Facebook API (Easiest - Start Here)
- [ ] Create Facebook Developer account
- [ ] Create Facebook App for business
- [ ] Configure app permissions and settings
- [ ] Generate and extend access token
- [ ] Get Facebook Page ID
- [ ] Test API connection
- [ ] Update .env file with credentials

**Estimated Time**: 30 minutes
**Difficulty**: Easy
**Business Impact**: High (Facebook business posting)

### Phase 2: Instagram API (Medium - Requires Facebook)
- [ ] Convert Instagram to Business account
- [ ] Connect Instagram to Facebook Page
- [ ] Add Instagram Basic Display to Facebook App
- [ ] Configure Instagram permissions
- [ ] Generate Instagram access token
- [ ] Get Instagram Business Account ID
- [ ] Test Instagram API connection
- [ ] Update .env file with credentials

**Estimated Time**: 25 minutes
**Difficulty**: Medium (depends on Facebook setup)
**Business Impact**: High (Visual content automation)

### Phase 3: Twitter API (Hardest - Requires Approval)
- [ ] Apply for Twitter Developer account
- [ ] Wait for approval (1-2 days)
- [ ] Create Twitter App and Project
- [ ] Configure app permissions (Read/Write)
- [ ] Generate all 5 API keys/tokens
- [ ] Test Twitter API connection
- [ ] Update .env file with credentials

**Estimated Time**: 20 minutes setup + 1-2 days approval
**Difficulty**: Hard (approval required)
**Business Impact**: High (Professional engagement)

## 🎯 Success Metrics

### Facebook Integration Success
- ✅ Can post to business page programmatically
- ✅ Can read page analytics and engagement
- ✅ Long-lived token (60 days) working
- ✅ MCP server connects successfully

### Instagram Integration Success
- ✅ Can post images to business account
- ✅ Can manage Instagram Stories
- ✅ Can read engagement metrics
- ✅ Business account ID verified

### Twitter Integration Success
- ✅ Can post tweets programmatically
- ✅ Can read mentions and replies
- ✅ Can access user timeline
- ✅ All 5 API credentials working

## 🔧 Testing Commands

### Facebook Test
```bash
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_TOKEN"
```

### Instagram Test
```bash
curl -X GET "https://graph.facebook.com/v18.0/ACCOUNT_ID?fields=id,username&access_token=YOUR_TOKEN"
```

### Twitter Test
```bash
curl -X GET "https://api.twitter.com/2/users/me" -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```

## 📊 Current Status

### Completed Framework (100%)
- ✅ Facebook MCP server created
- ✅ Instagram MCP server created
- ✅ Twitter MCP server created
- ✅ Social media orchestrator ready
- ✅ Agent Skills configured
- ✅ .env templates prepared

### Pending API Setup (0%)
- ⚠️ Facebook API credentials needed
- ⚠️ Instagram API credentials needed
- ⚠️ Twitter API credentials needed

## 🎉 After API Setup Complete

### Gold Tier Will Be 95% Complete
- ✅ All social media platforms operational
- ✅ Cross-platform posting automation
- ✅ Real-time engagement monitoring
- ✅ Professional brand management
- ✅ Complete business intelligence

### Business Value Unlocked
- **80+ hours weekly** saved through social automation
- **Professional presence** across all major platforms
- **Real-time customer engagement** 24/7
- **Data-driven** social media optimization
- **Unified brand voice** across all channels

## 🚀 Next Steps After API Setup

1. **End-to-end testing** of all Gold Tier features
2. **Live social media posting** verification
3. **Cross-platform coordination** testing
4. **Final Gold Tier validation** (95% complete)
5. **Production deployment** preparation

---
*API Setup Checklist - Gold Tier Final Phase Ready*
