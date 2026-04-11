# Render.com Deployment Configuration

## Service Settings

**Name:** ai-employee-whatsapp
**Environment:** Python 3
**Branch:** main
**Root Directory:** (leave empty)

## Build & Deploy

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python implementation/whatsapp_webhook.py
```

## Environment Variables

Add these in Render dashboard (Environment tab):

```bash
# WhatsApp Cloud API
WHATSAPP_ACCESS_TOKEN=EAALxnnACIoABRKUcn2x15eNZCUaZAdqCZCD5mkuiZCy4LkbyzABKxBx1VaPvPXthDMO0pSZCoNPdwl0ZC1C2d1JV7NpBn96I6Gdrrnl8QeROMQBFGTJsXZBkD0BUZADr3aFd5ZAdrUZBINFz7kzQbBEpdT7Ot6mHzzZCilTonQinf0zlfhfxQrkma5ZCUK4DDmupxFsIwZDZD
WHATSAPP_PHONE_NUMBER_ID=1004199756120385
WHATSAPP_BUSINESS_ACCOUNT_ID=1491297882449999
WHATSAPP_WEBHOOK_VERIFY_TOKEN=ai_employee_whatsapp_verify_2026

# LinkedIn
LINKEDIN_ACCESS_TOKEN=AQWO57LAdDComDNuYaz9IDxgcl_x8MQZsZ-6Al_rYI5Tp7bSfvKux5Kc3cJn2D-T0QIfFrLHV_NuY1lYjrLB2pKrcN1jYc1QYB5G-E0NPmgWBayrCmlu1gh-dTLOVrZI2C3yOxmG_geBpi8IvoWfFVUwcUJd11wEfX0bH4a2pmgLbo_hrv0dqgmOz9pNmxnCcFQxf1kLH3ZVV2aytHzv0hg5SiBrkRFcvk1MS857ZIQMjraPRU2WbJp5MXO-01npu8oaMI18lqyO0xTdR9mu6cdbjjtn3Dbm-eM-Q22_EHL1jzRYYc4qtqG1Fm8PoP6EXboqMy3aR2eWa7bPk67cCCFf1hv5Fw
LINKEDIN_PERSON_URN=urn:li:person:XbMGWdmblt

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=naheadj@gmail.com
SMTP_PASS=encgwiysqpyhtsji
EMAIL_FROM_ADDRESS=naheadj@gmail.com

# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=1057143350811799

# Server
PORT=8080
```

## Health Check Path

**Health Check Path:** `/health`

## Instance Type

- **Free:** Good for testing (sleeps after 15min)
- **Starter ($7/month):** Recommended for production (no sleep)
