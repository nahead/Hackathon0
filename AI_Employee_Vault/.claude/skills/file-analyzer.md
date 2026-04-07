# File Analyzer

Analyze files and determine appropriate processing actions.

## Usage
Use this skill to analyze files that have been dropped into the system and determine what actions should be taken.

## Instructions
You are analyzing files for the AI Employee system. For each file:

1. **Examine the file content** (if it's a readable format)
2. **Determine the file type** and purpose
3. **Assess priority level** (urgent, important, normal)
4. **Suggest appropriate actions** based on content
5. **Check if human approval is needed** per Company Handbook
6. **Create a processing plan** if the task is complex

### Analysis Framework:
- **Document files** (.pdf, .docx, .txt): Read and summarize content
- **Image files** (.jpg, .png): Describe and categorize
- **Data files** (.csv, .xlsx): Analyze structure and content
- **Code files** (.py, .js, etc.): Review and document purpose
- **Unknown formats**: Identify and recommend handling

### Output Format:
For each file, provide:
- File type and format
- Content summary
- Recommended actions
- Priority level
- Approval requirements
- Processing timeline

Analyze all files in the current context and provide detailed recommendations.