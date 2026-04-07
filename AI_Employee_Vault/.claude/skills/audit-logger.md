# Audit Logger

Log all AI Employee actions for audit trail and compliance.

## Usage
Use this skill to create detailed logs of all AI Employee actions and maintain audit trails.

## Instructions
You are the audit logging system for the AI Employee. Your responsibilities:

1. **Log all actions** taken by the AI Employee
2. **Maintain audit trails** for compliance
3. **Create structured log entries** with timestamps
4. **Track file movements** and processing decisions
5. **Record approval workflows** and human interactions

### Log Entry Format:
```json
{
  "timestamp": "2026-02-20T10:30:00Z",
  "action_type": "file_processed",
  "actor": "ai_employee",
  "source": "Needs_Action/FILE_example.md",
  "target": "Done/FILE_example.md",
  "details": "Analyzed document and moved to completed",
  "approval_required": false,
  "result": "success"
}
```

### Action Types to Log:
- file_processed
- dashboard_updated
- approval_requested
- task_completed
- error_occurred
- human_intervention

### Log Storage:
- Create daily log files: `Logs/YYYY-MM-DD.json`
- Append new entries to current day's log
- Maintain structured JSON format
- Include all relevant metadata

Log the current action and any recent activities that haven't been logged yet.