#!/usr/bin/env python3
"""
Railway Configuration Helper
Generates the exact variables needed for Railway
"""

def show_railway_config():
    """Display Railway environment variables"""

    print("=" * 60)
    print("[*] RAILWAY ENVIRONMENT VARIABLES")
    print("=" * 60)

    variables = [
        ("VAULT_REPO_URL", "https://github.com/nahead/-ai-employee-vault.git"),
        ("GIT_USERNAME", "nahead"),
        ("GIT_TOKEN", "your-github-personal-access-token")
    ]

    print("\nAdd these to Railway Dashboard -> Variables:")
    print("-" * 40)

    for name, value in variables:
        if "TOKEN" in name:
            print(f"{name}: {value}")
            print("  -> Create at: github.com -> Settings -> Developer settings -> Personal access tokens")
            print("  -> Scope: 'repo' (Full control of private repositories)")
        else:
            print(f"{name}: {value}")

    print("\n[*] After adding variables, Railway will auto-redeploy")
    print("[*] Then run the live test below")

if __name__ == "__main__":
    show_railway_config()