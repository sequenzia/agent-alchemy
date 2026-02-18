# Dependency Graph

## Conversion Order

| Wave | Component ID | Type | Group | Name | Dependencies |
|------|-------------|------|-------|------|-------------|
| 1 | skill-core-tools-language-patterns | skill | core-tools | language-patterns | none |
| 1 | skill-core-tools-project-conventions | skill | core-tools | project-conventions | none |
| 1 | skill-dev-tools-architecture-patterns | skill | dev-tools | architecture-patterns | none |
| 1 | skill-dev-tools-code-quality | skill | dev-tools | code-quality | none |
| 1 | skill-dev-tools-changelog-format | skill | dev-tools | changelog-format | none |
| 1 | skill-git-tools-git-commit | skill | git-tools | git-commit | none |
| 1 | skill-tdd-tools-analyze-coverage | skill | tdd-tools | analyze-coverage | none |
| 1 | skill-sdd-tools-create-tasks | skill | sdd-tools | create-tasks | none |
| 1 | agent-core-tools-code-architect | agent | core-tools | code-architect | none |
| 1 | agent-dev-tools-code-reviewer | agent | dev-tools | code-reviewer | none |
| 1 | agent-dev-tools-changelog-manager | agent | dev-tools | changelog-manager | none |
| 1 | agent-dev-tools-docs-writer | agent | dev-tools | docs-writer | none |
| 1 | agent-tdd-tools-test-reviewer | agent | tdd-tools | test-reviewer | none |
| 2 | agent-core-tools-code-explorer | agent | core-tools | code-explorer | project-conventions |
| 2 | agent-core-tools-code-synthesizer | agent | core-tools | code-synthesizer | project-conventions |
| 2 | agent-tdd-tools-test-writer | agent | tdd-tools | test-writer | language-patterns, project-conventions |
| 2 | skill-dev-tools-release-python-package | skill | dev-tools | release-python-package | changelog-manager |
| 2 | skill-sdd-tools-analyze-spec | skill | sdd-tools | analyze-spec | none (cycle-broken) |
| 2 | hooks-core-tools-hooks | hooks | core-tools | hooks | none |
| 2 | hooks-sdd-tools-hooks | hooks | sdd-tools | hooks | none |
| 3 | skill-core-tools-deep-analysis | skill | core-tools | deep-analysis | code-explorer, code-synthesizer |
| 3 | skill-tdd-tools-generate-tests | skill | tdd-tools | generate-tests | language-patterns, project-conventions, test-writer |
| 3 | skill-sdd-tools-execute-tasks | skill | sdd-tools | execute-tasks | none (cycle-broken) |
| 3 | agent-sdd-tools-task-executor | agent | sdd-tools | task-executor | execute-tasks |
| 3 | agent-sdd-tools-spec-analyzer | agent | sdd-tools | spec-analyzer | analyze-spec |
| 3 | agent-sdd-tools-researcher | agent | sdd-tools | researcher | none |
| 4 | skill-core-tools-codebase-analysis | skill | core-tools | codebase-analysis | deep-analysis |
| 4 | skill-dev-tools-feature-dev | skill | dev-tools | feature-dev | deep-analysis, architecture-patterns, code-quality, code-architect, code-reviewer |
| 4 | skill-dev-tools-docs-manager | skill | dev-tools | docs-manager | deep-analysis, docs-writer |
| 4 | skill-sdd-tools-create-spec | skill | sdd-tools | create-spec | deep-analysis, researcher |
| 4 | skill-tdd-tools-tdd-cycle | skill | tdd-tools | tdd-cycle | language-patterns, project-conventions, generate-tests |
| 4 | agent-tdd-tools-tdd-executor | agent | tdd-tools | tdd-executor | tdd-cycle |
| 4 | skill-sdd-tools-create-tdd-tasks | skill | sdd-tools | create-tdd-tasks | tdd-tools |
| 4 | skill-sdd-tools-execute-tdd-tasks | skill | sdd-tools | execute-tdd-tasks | tdd-executor, task-executor |

## Dependency Edges

| Source | Target | Dependency Type |
|--------|--------|----------------|
| codebase-analysis | deep-analysis | skill-to-skill |
| feature-dev | deep-analysis | cross-plugin |
| feature-dev | architecture-patterns | skill-to-skill |
| feature-dev | code-quality | skill-to-skill |
| feature-dev | code-architect | skill-to-agent (cross-plugin) |
| feature-dev | code-reviewer | skill-to-agent |
| docs-manager | deep-analysis | cross-plugin |
| docs-manager | docs-writer | skill-to-agent |
| create-spec | deep-analysis | cross-plugin |
| create-spec | researcher | skill-to-agent |
| deep-analysis | code-explorer | skill-to-agent |
| deep-analysis | code-synthesizer | skill-to-agent |
| tdd-cycle | language-patterns | cross-plugin |
| tdd-cycle | project-conventions | cross-plugin |
| tdd-cycle | generate-tests (refs) | reference-include |
| generate-tests | language-patterns | cross-plugin |
| generate-tests | project-conventions | cross-plugin |
| generate-tests | test-writer | skill-to-agent |
| execute-tasks | task-executor | skill-to-agent (circular) |
| analyze-spec | spec-analyzer | skill-to-agent (circular) |
| execute-tdd-tasks | tdd-executor | skill-to-agent (cross-plugin) |
| execute-tdd-tasks | task-executor | skill-to-agent |
| release-python-package | changelog-manager | skill-to-agent |
| code-explorer | project-conventions | agent-to-skill |
| code-synthesizer | project-conventions | agent-to-skill |
| test-writer | language-patterns | agent-to-skill (cross-plugin) |
| test-writer | project-conventions | agent-to-skill (cross-plugin) |
| spec-analyzer | analyze-spec | agent-to-skill (circular) |
| task-executor | execute-tasks | agent-to-skill (circular) |
| create-tdd-tasks | tdd-tools | cross-plugin (check) |

## Circular References

- analyze-spec -> spec-analyzer -> analyze-spec
- execute-tasks -> task-executor -> execute-tasks
- tdd-cycle -> tdd-executor -> tdd-cycle (expected)

## External Dependencies

| Source | External Dependency | Type |
|--------|-------------------|------|
| agent-sdd-tools-researcher | MCP server: context7 (mcp__context7__resolve-library-id, mcp__context7__query-docs) | MCP server |

## Classification Counts

| Classification | Count |
|---------------|-------|
| Internal | 35 |
| External-selected | 0 |
| External-missing | 0 |
| External | 1 |
| System | many |
