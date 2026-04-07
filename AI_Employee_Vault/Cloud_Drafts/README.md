# Cloud Drafts Directory

This directory contains draft responses created by the Cloud Agent.

## Purpose
- Cloud agent monitors emails, files, and events 24/7
- Creates draft responses that require human approval
- No direct external actions - drafts only for security

## File Types
- `EMAIL_DRAFT_*.md` - Draft email responses
- `SOCIAL_DRAFT_*.md` - Draft social media posts
- `TASK_DRAFT_*.md` - Draft task assignments

## Workflow
1. Cloud agent detects new email/event
2. Creates draft response in this folder
3. Creates approval request in /Pending_Approval
4. Human reviews and moves to /Approved or /Rejected
5. Local agent executes approved actions

---
*Platinum Tier - Cloud Agent Draft Creation*