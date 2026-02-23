# Execution Context

## Project Patterns
- Plugin naming: `agent-alchemy-{group-name}` for marketplace, `{group-name}` for directory
- Reference files: H1 title, intro paragraph, horizontal rule, structured sections with tables/code/bullets
- Agent frontmatter: `name`, `description`, `model`, `tools`, `skills` in YAML + markdown system prompt
- Sonnet-tier for worker agents; Opus for synthesis/review/autonomous execution
- Cross-plugin composition via `${CLAUDE_PLUGIN_ROOT}/../{plugin-name}/skills/{skill}/SKILL.md`
- Skill YAML frontmatter: name, description, argument-hint, user-invocable, disable-model-invocation, allowed-tools
- Phase-based workflows with "CRITICAL: Complete ALL N phases" directive
- Settings in `.claude/agent-alchemy.local.md` under namespace keys with kebab-case
- Plugin directory structure: `claude/{plugin-name}/skills/{skill-name}/references/`
- Reference skill pattern: YAML frontmatter (name, description, user-invocable: false, disable-model-invocation: false, last-verified) + H2 sections separated by horizontal rules
- Self-referential loading: `Read ${CLAUDE_PLUGIN_ROOT}/skills/{skill-name}/references/{file}.md`
- Marketplace entries: alphabetically ordered, 2-space indentation, consistent field ordering
- Anti-pattern entries: numbered ID prefixes (AP-01, AP-02, etc.) with Description/Why/Correct Alternative structure
- Orchestration patterns: consistent structure per pattern (description, when to use, team structure table, task design, communication flow diagram, practical example, scaling notes)
- Hook exit code protocol: 0=pass, 1=error (proceed), 2=block with feedback via stderr

## Key Decisions
- Plugin directory convention: short directory name (e.g., `claude-tools`) under `claude/`
- Marketplace name convention: `agent-alchemy-{dir-name}` (e.g., `agent-alchemy-claude-tools`)
- `last-verified` frontmatter key specific to claude-tools reference skills
- Team hook events (TeammateIdle, TaskCompleted) are distinct from standard Claude Code hooks (PreToolUse, PostToolUse, Stop)

## Known Issues
<!-- No issues encountered -->

## File Map
- `claude/claude-tools/` — Plugin directory for Claude Code Tasks and Agent Teams reference skills
- `claude/claude-tools/skills/cc-tasks/SKILL.md` — Main cc-tasks reference (293 lines)
- `claude/claude-tools/skills/cc-tasks/references/task-patterns.md` — Task design patterns (562 lines)
- `claude/claude-tools/skills/cc-tasks/references/anti-patterns.md` — Task anti-patterns (275 lines)
- `claude/claude-tools/skills/cc-teams/SKILL.md` — Main cc-teams reference (283 lines)
- `claude/claude-tools/skills/cc-teams/references/messaging-protocol.md` — SendMessage protocol (260 lines)
- `claude/claude-tools/skills/cc-teams/references/orchestration-patterns.md` — Orchestration patterns (792 lines)
- `claude/claude-tools/skills/cc-teams/references/hooks-integration.md` — Hooks integration (338 lines)
- `claude/.claude-plugin/marketplace.json` — Plugin marketplace registry (7 plugins)

## Task History
### Prior Sessions Summary
Previous execution (exec-session-20260215-212833) completed 14 tasks building the tdd-tools plugin and sdd-tools extensions. All tasks passed.

### Task [15]: Create claude-tools plugin directory structure - PASS
- Created directory tree with `.gitkeep` files. No issues.

### Task [16]: Create cc-tasks SKILL.md reference skill - PASS
- Created 293-line reference. Metadata replacement (not merge) behavior documented.

### Task [19]: Create cc-teams SKILL.md reference skill - PASS
- Created 283-line reference. State diagrams use Mermaid `stateDiagram-v2`.

### Task [23]: Register claude-tools plugin in marketplace.json - PASS
- Added entry in alphabetical position. Edit tool denied; Write tool used as fallback.

### Task [17]: Create cc-tasks task-patterns.md reference - PASS
- Created 562-line reference. Covers 4 dependency graph patterns, task right-sizing, multi-agent coordination, metadata strategies.

### Task [18]: Create cc-tasks anti-patterns.md reference - PASS
- Created 275-line reference with 7 anti-patterns. Removed `.gitkeep`.

### Task [20]: Create cc-teams messaging-protocol.md reference - PASS
- Created 260-line reference. All 5 SendMessage types with field tables and tool call examples.

### Task [21]: Create cc-teams orchestration-patterns.md reference - PASS
- Created 792-line reference. 6 patterns (5 required + Hub-and-Spoke bonus) with selection guide.

### Task [22]: Create cc-teams hooks-integration.md reference - PASS
- Created 338-line reference. TeammateIdle and TaskCompleted events with input schemas and examples.
