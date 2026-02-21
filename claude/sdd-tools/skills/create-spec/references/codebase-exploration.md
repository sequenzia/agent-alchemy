# Codebase Exploration Procedure

This reference describes the standalone codebase exploration workflow for `create-spec` when building specs for new features in existing products. It replaces external deep-analysis with lightweight parallel exploration using `codebase-explorer` agents.

## Overview

The exploration has four steps:
1. **Quick Reconnaissance** — Map the project structure and identify key characteristics
2. **Plan Focus Areas** — Determine 2-3 exploration themes based on the feature and reconnaissance
3. **Parallel Exploration** — Spawn `codebase-explorer` agents via the `Task` tool
4. **Synthesis** — Merge all findings into structured "Codebase Context"

---

## Step 1: Quick Reconnaissance

Before spawning agents, gather high-level project context yourself:

1. **Map project structure** — Run `Glob` patterns to understand the directory layout:
   - `*` (root files)
   - `src/**` or `lib/**` or `app/**` (source directories)
   - `**/*.config.*`, `**/tsconfig.*`, `**/pyproject.toml`, `**/package.json` (config files)

2. **Read key files** — Read the most informative files (stop after finding 2-3):
   - `CLAUDE.md` or `README.md` (project documentation)
   - `package.json` / `pyproject.toml` / `Cargo.toml` (dependencies and scripts)
   - Main entry points (`src/index.*`, `src/main.*`, `app/page.*`, `manage.py`)

3. **Identify characteristics** — From what you've read, note:
   - Language and framework
   - Architecture style (monolith, microservices, monorepo, etc.)
   - Directory structure pattern (feature-based, layer-based, etc.)
   - Key dependencies

This reconnaissance takes 3-5 tool calls and provides the orientation agents need.

---

## Step 2: Plan Focus Areas

Based on the user's feature description and your reconnaissance findings, determine 2-3 exploration focus areas. Common focus areas include:

- **Architecture & Patterns** — Module structure, design patterns, service organization, middleware/plugin systems
- **Feature-Relevant Code** — Existing similar features, code the new feature will touch or extend, integration points
- **Data Models & APIs** — Schemas, database models, API endpoints, data flow pipelines
- **Testing & Infrastructure** — Test patterns, CI/CD setup, deployment configuration

Choose focus areas that are most relevant to the specific feature being specified. For example:
- A new API endpoint → "Existing API patterns", "Data models", "Authentication/middleware"
- A new UI feature → "Component patterns", "State management", "Similar UI features"
- A new background job → "Existing job infrastructure", "Data pipelines", "Error handling patterns"

---

## Step 3: Parallel Exploration

Spawn 2-3 `codebase-explorer` agents in a **single message** using the `Task` tool. Each agent gets:

```
Task:
  subagent_type: "codebase-explorer"
  description: "Explore {focus area name}"
  prompt: |
    Feature being specified: {user's feature description from Phase 2}

    Project context:
    - Language/framework: {from reconnaissance}
    - Architecture: {from reconnaissance}
    - Project root: {working directory path}

    Your focus area: {specific focus area}

    Explore this focus area thoroughly. Look for:
    - {specific things to look for based on focus area}
    - {specific things to look for based on focus area}

    Reconnaissance summary:
    {brief summary of what was found in Step 1}
```

All agents run concurrently. Wait for all to complete before proceeding.

---

## Step 4: Synthesis

After all agents return their findings, merge them into a structured "Codebase Context":

```markdown
## Codebase Context

### Project Overview
- Language/Framework: {from recon}
- Architecture: {from recon}
- Key Dependencies: {from recon}

### Architecture Patterns
{Merged from architecture-focused exploration}

### Relevant Existing Code
{Merged from feature-relevant exploration — files, patterns, similar features}

### Data Models
{Merged from data-focused exploration — schemas, models, APIs}

### Integration Points
{Where the new feature connects to existing code}

### Conventions & Standards
{Naming, testing, error handling patterns observed}
```

Store this internally as "Codebase Context" for use in interview rounds and spec compilation.

---

## Error Handling

- **If an agent fails**: Continue with successful agents' findings. Partial context is still valuable.
- **If all agents fail**: Use reconnaissance findings only. The spec can still be created with manual user input about the codebase.
- **Always offer skip option**: Before starting exploration, use `AskUserQuestion` to let the user skip if they prefer:

```yaml
AskUserQuestion:
  questions:
    - header: "Codebase Exploration"
      question: "I'd like to explore the codebase to understand existing patterns and conventions. This helps create a more accurate spec. Would you like me to proceed?"
      options:
        - label: "Explore codebase (Recommended)"
          description: "Parallel exploration of architecture, patterns, and relevant code"
        - label: "Skip exploration"
          description: "Continue without codebase analysis — I'll provide context manually"
      multiSelect: false
```

If the user skips, proceed directly to Phase 3 Round 1 with no codebase context.
