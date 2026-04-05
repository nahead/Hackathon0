#!/usr/bin/env python3
"""
Railway Deployment Helper
Automates Railway deployment setup
"""

import os
import subprocess
import sys
from pathlib import Path

def print_step(step, message):
    """Print formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {message}")
    print('='*60)

def run_command(cmd, description):
    """Run command and handle errors"""
    print(f"\n→ {description}")
    print(f"  Command: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Success")
            if result.stdout:
                print(f"  Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  ✗ Failed")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def check_prerequisites():
    """Check if prerequisites are installed"""
    print_step(1, "Checking Prerequisites")

    checks = {
        "Node.js": "node --version",
        "npm": "npm --version",
        "Git": "git --version",
        "Python": "python --version"
    }

    all_ok = True
    for name, cmd in checks.items():
        if run_command(cmd, f"Checking {name}"):
            print(f"  ✓ {name} installed")
        else:
            print(f"  ✗ {name} not found")
            all_ok = False

    return all_ok

def install_railway_cli():
    """Install Railway CLI"""
    print_step(2, "Installing Railway CLI")

    # Check if already installed
    if run_command("railway --version", "Checking Railway CLI"):
        print("  ✓ Railway CLI already installed")
        return True

    print("\n  Installing Railway CLI via npm...")
    return run_command("npm install -g @railway/cli", "Installing Railway CLI")

def login_to_railway():
    """Login to Railway"""
    print_step(3, "Railway Login")

    print("\n  Opening browser for Railway login...")
    print("  Please authorize the CLI in your browser")

    return run_command("railway login", "Logging in to Railway")

def create_vault_repo():
    """Guide user to create vault repository"""
    print_step(4, "Vault Repository Setup")

    print("\n  You need to create a GitHub repository for vault sync:")
    print("  1. Go to: https://github.com/new")
    print("  2. Repository name: ai-employee-vault")
    print("  3. Make it PRIVATE")
    print("  4. Don't initialize with README")
    print("  5. Create repository")
    print("\n  Then create a Personal Access Token:")
    print("  1. Go to: https://github.com/settings/tokens")
    print("  2. Generate new token (classic)")
    print("  3. Name: AI Employee Vault Sync")
    print("  4. Select scope: repo (all)")
    print("  5. Generate and copy the token")

    input("\n  Press Enter when you've created the repository and token...")

    repo_url = input("\n  Enter your vault repository URL: ")
    git_username = input("  Enter your GitHub username: ")
    git_token = input("  Enter your GitHub token: ")

    return repo_url, git_username, git_token

def initialize_railway_project():
    """Initialize Railway project"""
    print_step(5, "Initialize Railway Project")

    print("\n  Creating new Railway project...")
    print("  Project name: ai-employee-platinum")

    return run_command("railway init", "Initializing Railway project")

def set_environment_variables(repo_url, git_username, git_token):
    """Set Railway environment variables"""
    print_step(6, "Configure Environment Variables")

    variables = {
        "AGENT_TYPE": "cloud",
        "RAILWAY_ENVIRONMENT": "production",
        "SMTP_USER": "naheadj@gmail.com",
        "VAULT_REPO_URL": repo_url,
        "GIT_USERNAME": git_username,
        "GIT_TOKEN": git_token
    }

    print("\n  Setting environment variables...")

    for key, value in variables.items():
        if key == "GIT_TOKEN":
            print(f"  Setting {key}=***hidden***")
        else:
            print(f"  Setting {key}={value}")

        cmd = f'railway variables set {key}="{value}"'
        run_command(cmd, f"Setting {key}")

    print("\n  ⚠️  IMPORTANT: Set SMTP_PASS manually:")
    print("  railway variables set SMTP_PASS=your-gmail-app-password")

def deploy_to_railway():
    """Deploy to Railway"""
    print_step(7, "Deploy to Railway")

    print("\n  Deploying application to Railway...")
    print("  This may take a few minutes...")

    return run_command("railway up --detach", "Deploying to Railway")

def show_status():
    """Show deployment status"""
    print_step(8, "Deployment Status")

    run_command("railway status", "Checking deployment status")

    print("\n  To view logs:")
    print("  railway logs --follow")

    print("\n  To get your app URL:")
    print("  railway domain")

def main():
    """Main deployment flow"""
    print("\n" + "="*60)
    print("🚂 RAILWAY DEPLOYMENT HELPER - PLATINUM TIER")
    print("="*60)

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Please install missing prerequisites first")
        return

    # Step 2: Install Railway CLI
    if not install_railway_cli():
        print("\n❌ Failed to install Railway CLI")
        return

    # Step 3: Login to Railway
    if not login_to_railway():
        print("\n❌ Failed to login to Railway")
        return

    # Step 4: Create vault repository
    repo_url, git_username, git_token = create_vault_repo()

    # Step 5: Initialize Railway project
    if not initialize_railway_project():
        print("\n❌ Failed to initialize Railway project")
        return

    # Step 6: Set environment variables
    set_environment_variables(repo_url, git_username, git_token)

    # Step 7: Deploy
    if not deploy_to_railway():
        print("\n❌ Deployment failed")
        return

    # Step 8: Show status
    show_status()

    print("\n" + "="*60)
    print("✅ RAILWAY DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Set SMTP_PASS: railway variables set SMTP_PASS=your-password")
    print("2. Monitor logs: railway logs --follow")
    print("3. Test health: curl $(railway domain)/health")
    print("4. Complete Platinum demo (see RAILWAY_DEPLOYMENT_GUIDE.md)")
    print("\n🎉 Your AI Employee is now running 24/7 on Railway!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
