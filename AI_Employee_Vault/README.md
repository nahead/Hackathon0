# AI Employee Vault - README

This is the Bronze tier implementation of a Personal AI Employee using Claude Code and Obsidian.

## Folder Structure

- **Inbox/**: Drop files here for processing
- **Needs_Action/**: Tasks that require AI attention
- **Done/**: Completed tasks and processed files
- **Plans/**: AI-generated plans for complex tasks
- **Logs/**: System logs and audit trails
- **Pending_Approval/**: Actions requiring human approval
- **Approved/**: Human-approved actions ready for execution
- **Rejected/**: Human-rejected actions

## Core Files

- **Dashboard.md**: Real-time system status and activity summary
- **Company_Handbook.md**: Rules and guidelines for AI behavior

## Getting Started

1. Install Python dependencies: `pip install watchdog pathlib`
2. Run the file system watcher: `python file_watcher.py`
3. Use Claude Code to process tasks: `claude --cwd AI_Employee_Vault`

## Bronze Tier Features

- File system monitoring
- Automated task processing
- Human-in-the-loop approvals
- Audit logging
- Dashboard updates

---
*Personal AI Employee v0.1 - Bronze Tier*