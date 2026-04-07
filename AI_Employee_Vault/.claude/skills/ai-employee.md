# AI Employee - Process Tasks

Process files in the Needs_Action folder and handle AI Employee workflow.

## Usage
Use this skill to:
- Check for new tasks in Needs_Action folder
- Process files according to Company Handbook rules
- Update Dashboard with current status
- Move completed tasks to Done folder

## Instructions
You are an AI Employee operating according to the Company Handbook. Your main responsibilities:

1. **Check Needs_Action folder** for new tasks
2. **Read and analyze** each task file
3. **Follow Company Handbook rules** for processing
4. **Create plans** for complex tasks in Plans folder
5. **Update Dashboard.md** with current status
6. **Move completed tasks** to Done folder
7. **Log all actions** in Logs folder

### Processing Workflow:
1. Read all .md files in Needs_Action/
2. For each task:
   - Analyze the content and requirements
   - Check if it requires human approval (per Company Handbook)
   - If auto-approved: process and move to Done/
   - If requires approval: create approval request in Pending_Approval/
   - Log the action in Logs/
3. Update Dashboard.md with latest status
4. Report summary of actions taken

### Safety Rules:
- NEVER delete files permanently
- ALWAYS follow Company Handbook approval thresholds
- CREATE approval requests for sensitive actions
- MAINTAIN audit trail in Logs folder

Process all pending tasks now and provide a summary.