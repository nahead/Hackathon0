#!/bin/bash
# Quick setup script for vault repository

echo "=== AI Employee Vault - GitHub Setup ==="
echo ""
echo "Step 1: Create GitHub Repository"
echo "Go to: https://github.com/new"
echo "Name: ai-employee-vault"
echo "Private: Yes (recommended)"
echo "Click: Create repository"
echo ""
echo "Step 2: Copy your repository URL"
echo "Example: https://github.com/YOUR_USERNAME/ai-employee-vault.git"
echo ""
read -p "Enter your vault repository URL: " REPO_URL

cd AI_Employee_Vault

# Add remote
git remote add origin "$REPO_URL"

# Push to GitHub
echo ""
echo "Pushing vault to GitHub..."
git push -u origin main

echo ""
echo "✅ Vault pushed successfully!"
echo ""
echo "Next: Create GitHub token at https://github.com/settings/tokens"
echo "Scopes needed: repo (full control)"
