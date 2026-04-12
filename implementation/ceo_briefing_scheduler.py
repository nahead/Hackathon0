#!/usr/bin/env python3
"""
CEO Briefing Scheduler
Generates weekly Monday morning CEO briefings automatically
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CEOBriefingScheduler')

VAULT_PATH = Path(__file__).parent.parent / "AI_Employee_Vault"
BRIEFINGS_PATH = VAULT_PATH / "CEO_Briefings"

def generate_ceo_briefing():
    """Generate CEO briefing using Claude Code"""
    logger.info("🎯 Generating CEO Briefing...")

    # Ensure briefings folder exists
    BRIEFINGS_PATH.mkdir(exist_ok=True)

    # Create briefing filename
    today = datetime.now()
    filename = f"CEO_Briefing_{today.strftime('%Y%m%d')}.md"
    filepath = BRIEFINGS_PATH / filename

    # Prompt for Claude Code
    prompt = f"""Generate a comprehensive Monday Morning CEO Briefing using the ceo-briefing skill.

Analyze:
1. Business_Goals.md for objectives and metrics
2. Done/ folder for completed tasks this week
3. Pending_Approval/ for items needing attention
4. Plans/ for upcoming work

Create briefing at: {filepath}

Include:
- Executive Summary
- Revenue Performance (weekly/monthly)
- Completed Accomplishments
- Bottlenecks Identified
- Proactive Suggestions (cost optimization, revenue opportunities)
- Upcoming Critical Dates
- Key Metrics Dashboard

Follow the template in AI_Employee_Vault/.claude/skills/ceo-briefing.md
"""

    try:
        # Call Claude Code to generate briefing
        result = subprocess.run(
            ['claude', '--cwd', str(VAULT_PATH), prompt],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            logger.info(f"✅ CEO Briefing generated: {filename}")

            # Update Dashboard
            update_dashboard_with_briefing(filename)

            return True
        else:
            logger.error(f"❌ Failed to generate briefing: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Error generating briefing: {e}")
        return False

def update_dashboard_with_briefing(briefing_filename):
    """Update Dashboard.md with new briefing link"""
    dashboard_path = VAULT_PATH / "Dashboard.md"

    if not dashboard_path.exists():
        return

    try:
        content = dashboard_path.read_text(encoding='utf-8')

        # Add briefing to Recent Achievements section
        briefing_line = f"- ✅ CEO Briefing generated: [[CEO_Briefings/{briefing_filename}]]"

        if "## 📈 Recent Achievements" in content:
            content = content.replace(
                "## 📈 Recent Achievements",
                f"## 📈 Recent Achievements\n{briefing_line}"
            )

            dashboard_path.write_text(content, encoding='utf-8')
            logger.info("✅ Dashboard updated with briefing link")

    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("CEO BRIEFING SCHEDULER")
    logger.info("="*70)

    success = generate_ceo_briefing()

    if success:
        logger.info("✅ CEO Briefing generation complete")
        sys.exit(0)
    else:
        logger.error("❌ CEO Briefing generation failed")
        sys.exit(1)
