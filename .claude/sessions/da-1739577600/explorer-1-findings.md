## Explorer 1: Plugin Architecture & Composition Patterns

### Key Findings

**Inventory:** 70 markdown files, 20 skills, 12 agents, 5 plugin groups, 33 reference files

**Plugin Versions:** core-tools 0.1.1, dev-tools 0.1.1, git-tools 0.1.0, sdd-tools 0.1.2, tdd-tools 0.1.0

### Composition Patterns

1. **Skill Composition via Prompt Injection** — Skills compose by reading other skills' SKILL.md files using `${CLAUDE_PLUGIN_ROOT}`. Cross-plugin loading uses relative paths like `/../core-tools/`.

2. **Hub-and-Spoke Team Coordination** — deep-analysis spawns N explorer agents (Sonnet) + 1 synthesizer (Opus). Explorers work independently, synthesizer merges with Bash investigation.

3. **Phase Workflows with Completeness Enforcement** — Multi-phase skills use `CRITICAL: Complete ALL N phases` directives. Found in feature-dev (7), create-spec (6), tdd-cycle (7).

4. **Progressive Knowledge Loading** — Large knowledge bases externalized into references/ subdirectories. Largest: test-patterns.md (776 lines), test-rubric.md (530 lines).

5. **Agent Tool Restrictions** — Read-only agents (code-explorer, code-architect, code-reviewer) vs full-capability (task-executor, tdd-executor, test-writer).

6. **AskUserQuestion Enforcement** — All interactive skills mandate AskUserQuestion for user interaction.

7. **Model Tiering** — Opus for synthesis/architecture/review, Sonnet for parallel workers, Haiku for simple tasks.

### Cross-Plugin Dependency Graph
- deep-analysis loaded by: codebase-analysis, feature-dev, docs-manager, create-spec
- language-patterns + project-conventions loaded by: feature-dev, tdd-cycle, generate-tests, and as agent skills
- 11 files use ${CLAUDE_PLUGIN_ROOT}, 10 files use subagent_type

### Marketplace Registry
- Located at claude/.claude-plugin/marketplace.json
- No individual plugin.json files — uses centralized marketplace with source field pointing to subdirectories

### Challenges Identified
1. ${CLAUDE_PLUGIN_ROOT} resolution is implicit — not documented
2. Potential circular dependency risk with deep-analysis
3. Agent tool restrictions not cross-validated against task requirements
4. Large reference files (776 lines) may approach context limits
5. No schema validation layer for marketplace.json
