#!/usr/bin/env python3
"""
Vault Repository Setup Script
Creates and initializes private GitHub repository for AI Employee vault sync
"""

import os
import subprocess
import json
from pathlib import Path

def setup_vault_repository():
    """Set up private GitHub repository for vault synchronization"""

    print("[*] Setting up AI Employee Vault Repository...")

    # Create vault structure
    vault_structure = {
        "Cloud_Drafts": "Draft responses created by cloud agent",
        "Pending_Approval": "Items awaiting human approval",
        "Approved": "Human-approved actions ready for execution",
        "Signals/Local": "Execution signals for local agent",
        "Reports/Cloud": "Cloud agent status and activity reports",
        "Processed": "Completed actions and their results"
    }

    # Create directories
    for folder, description in vault_structure.items():
        folder_path = Path(f"AI_Employee_Vault_Sync/{folder}")
        folder_path.mkdir(parents=True, exist_ok=True)

        # Create README in each folder
        readme_path = folder_path / "README.md"
        readme_content = f"""# {folder.split('/')[-1]}

{description}

---
*AI Employee Vault - Platinum Tier*
"""
        readme_path.write_text(readme_content)
        print(f"[+] Created: {folder}")

    # Create main vault README
    main_readme = Path("AI_Employee_Vault_Sync/README.md")
    main_readme_content = """# AI Employee Vault - Cloud Sync

This repository enables secure communication between your cloud AI Employee (Railway) and local AI Employee system.

## Structure

- **Cloud_Drafts/**: Draft responses created by cloud agent
- **Pending_Approval/**: Items awaiting human approval
- **Approved/**: Human-approved actions ready for execution
- **Signals/Local/**: Execution signals for local agent
- **Reports/Cloud/**: Cloud agent status and activity reports
- **Processed/**: Completed actions and their results

## Security

- Private repository with encrypted sync
- No sensitive credentials stored
- Human approval required for all external actions
- Complete audit trail maintained

---
*AI Employee Vault - Platinum Tier*
*24/7 Cloud + Local Architecture*
"""
    main_readme.write_text(main_readme_content)

    # Create .gitignore
    gitignore_path = Path("AI_Employee_Vault_Sync/.gitignore")
    gitignore_content = """# Security - Never commit these
*.env
*credentials*
*token*
*secret*
*key*
*password*

# Temporary files
*.tmp
*.log
.DS_Store
Thumbs.db

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Node
node_modules/
npm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
"""
    gitignore_path.write_text(gitignore_content)

    print("[+] Vault structure created successfully!")
    print("\n[*] Next steps:")
    print("1. Create private GitHub repository: 'ai-employee-vault'")
    print("2. Initialize git and push:")
    print("   cd AI_Employee_Vault_Sync")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initialize AI Employee Vault'")
    print("   git remote add origin https://github.com/YOUR_USERNAME/ai-employee-vault.git")
    print("   git push -u origin main")
    print("3. Add repository URL to Railway environment variables")

if __name__ == "__main__":
    setup_vault_repository()