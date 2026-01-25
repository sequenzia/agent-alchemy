---
description: Analyze an existing PRD for inconsistencies, missing information, ambiguities, and structure issues
allowed_tools:
  - AskUserQuestion
  - Task
  - Read
  - Glob
arguments:
  - name: prd-path
    description: Path to the PRD file to analyze
    required: true
---

# PRD Analyzer - Analyze Command

You are initiating the PRD analysis workflow. This process will analyze an existing PRD for quality issues and optionally guide the user through resolving them interactively.

## Workflow

### Step 1: Validate File

Verify the PRD file exists at the provided path. If not found:
- Check if user provided relative path and try common locations
- Use Glob to search for similar filenames
- Ask user for correct path if needed

### Step 2: Read PRD Content

Read the entire PRD file using the Read tool.

### Step 3: Detect Depth Level

Analyze the PRD content to detect its depth level:

**Full-Tech Indicators** (check first):
- Contains `API Specifications` section OR `### 7.4 API` or similar
- Contains API endpoint definitions (`POST /api/`, `GET /api/`, etc.)
- Contains `Testing Strategy` section
- Contains data model schemas

**Detailed Indicators**:
- Uses numbered sections (`## 1.`, `### 2.1`)
- Contains `Technical Architecture` section
- Contains user stories (`**US-001**:` or similar format)
- Contains acceptance criteria

**High-Level Indicators**:
- Contains feature table with Priority column
- Executive summary focus
- No user stories or acceptance criteria
- Shorter document (~50-100 lines)

**Detection Priority**:
1. If Full-Tech indicators found → Full-Tech
2. Else if Detailed indicators found → Detailed
3. Else if High-Level indicators found → High-Level
4. Default → Detailed

### Step 4: Check Settings

Check for settings at `.claude/prd-tools.local.md` to get:
- Author name (if configured)
- Any custom preferences

### Step 5: Determine Report Path

The analysis report should be saved in the same directory as the PRD with `.analysis.md` suffix:

- PRD: `specs/PRD-User-Auth.md`
- Report: `specs/PRD-User-Auth.analysis.md`

Extract the PRD filename and construct the report path.

### Step 6: Launch Analyzer Agent

Launch the PRD Analyzer Agent using the Task tool with subagent_type `prd-tools:prd-analyzer`.

Provide this context in the prompt:

```
Analyze the PRD at: {prd_path}

PRD Content:
{full_prd_content}

Detected Depth Level: {depth_level}
Report Output Path: {report_path}
Author: {author_from_settings or "Not specified"}

Instructions:
1. Load the analysis skill and reference files
2. Perform systematic analysis based on the depth level
3. Generate the analysis report
4. Present findings summary
5. Ask if user wants to enter update mode
6. If yes, guide through interactive resolution
7. Update report with final resolution status
```

### Step 7: Handoff Complete

Once you have launched the Analyzer Agent, your role is complete. The agent will handle:
- Loading analysis criteria for the depth level
- Performing comprehensive analysis
- Generating and saving the report
- Interactive update mode (if requested)
- Updating the PRD with approved changes

## Example Usage

```
/prd-tools:analyze specs/PRD-User-Authentication.md
```

This will:
1. Read the PRD at the specified path
2. Detect it's a Detailed-level PRD
3. Analyze for issues across all four categories
4. Save report to `specs/PRD-User-Authentication.analysis.md`
5. Offer interactive resolution mode

## Notes

- Always read the full PRD before launching the analyzer
- Depth detection determines which criteria apply
- Report is always saved alongside the PRD
- The analyzer agent handles all user interaction for resolution
