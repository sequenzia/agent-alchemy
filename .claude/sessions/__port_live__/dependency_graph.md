# Dependency Graph

## Conversion Order

| Wave | Component ID | Type | Group | Name | Dependencies |
|------|-------------|------|-------|------|-------------|
| 1 | skill-core-tools-language-patterns | skill | core-tools | language-patterns | none |
| 1 | skill-core-tools-project-conventions | skill | core-tools | project-conventions | none |
| 1 | skill-core-tools-technical-diagrams | skill | core-tools | technical-diagrams | none |
| 1 | skill-dev-tools-architecture-patterns | skill | dev-tools | architecture-patterns | none |
| 1 | skill-dev-tools-changelog-format | skill | dev-tools | changelog-format | none |
| 1 | skill-dev-tools-code-quality | skill | dev-tools | code-quality | none |
| 1 | skill-dev-tools-project-learnings | skill | dev-tools | project-learnings | none |
| 1 | skill-dev-tools-document-changes | skill | dev-tools | document-changes | none |
| 1 | agent-dev-tools-bug-investigator | agent | dev-tools | bug-investigator | none |
| 1 | agent-dev-tools-code-reviewer | agent | dev-tools | code-reviewer | none |
| 1 | agent-dev-tools-changelog-manager | agent | dev-tools | changelog-manager | none |
| 1 | hooks-core-tools-hooks | hooks | core-tools | hooks | none |
| 2 | agent-core-tools-code-explorer | agent | core-tools | code-explorer | skill-core-tools-project-conventions, skill-core-tools-language-patterns |
| 2 | agent-core-tools-code-synthesizer | agent | core-tools | code-synthesizer | skill-core-tools-project-conventions, skill-core-tools-language-patterns |
| 2 | agent-core-tools-code-architect | agent | core-tools | code-architect | none (placed in W2 for grouping) |
| 2 | agent-dev-tools-docs-writer | agent | dev-tools | docs-writer | skill-core-tools-technical-diagrams |
| 2 | skill-dev-tools-release-python-package | skill | dev-tools | release-python-package | agent-dev-tools-changelog-manager |
| 3 | skill-core-tools-deep-analysis | skill | core-tools | deep-analysis | agent-core-tools-code-explorer, agent-core-tools-code-synthesizer |
| 3 | skill-dev-tools-bug-killer | skill | dev-tools | bug-killer | skill-dev-tools-code-quality, skill-dev-tools-project-learnings, agent-core-tools-code-explorer, agent-dev-tools-bug-investigator |
| 4 | skill-core-tools-codebase-analysis | skill | core-tools | codebase-analysis | skill-core-tools-deep-analysis, skill-core-tools-technical-diagrams, agent-core-tools-code-architect, agent-core-tools-code-explorer |
| 4 | skill-dev-tools-docs-manager | skill | dev-tools | docs-manager | skill-core-tools-deep-analysis, agent-core-tools-code-explorer, agent-dev-tools-docs-writer |
| 4 | skill-dev-tools-feature-dev | skill | dev-tools | feature-dev | skill-core-tools-deep-analysis, skill-core-tools-language-patterns, skill-dev-tools-architecture-patterns, skill-dev-tools-code-quality, skill-dev-tools-changelog-format, agent-core-tools-code-architect, agent-dev-tools-code-reviewer |

## Dependency Edges

| Source | Target | Dependency Type |
|--------|--------|----------------|
| skill-core-tools-codebase-analysis | skill-core-tools-deep-analysis | skill-to-skill |
| skill-core-tools-codebase-analysis | skill-core-tools-technical-diagrams | skill-to-skill |
| skill-core-tools-codebase-analysis | agent-core-tools-code-architect | agent-reference |
| skill-core-tools-codebase-analysis | agent-core-tools-code-explorer | agent-reference |
| skill-core-tools-deep-analysis | agent-core-tools-code-explorer | agent-reference |
| skill-core-tools-deep-analysis | agent-core-tools-code-synthesizer | agent-reference |
| agent-core-tools-code-explorer | skill-core-tools-project-conventions | agent-to-skill |
| agent-core-tools-code-explorer | skill-core-tools-language-patterns | agent-to-skill |
| agent-core-tools-code-synthesizer | skill-core-tools-project-conventions | agent-to-skill |
| agent-core-tools-code-synthesizer | skill-core-tools-language-patterns | agent-to-skill |
| skill-dev-tools-bug-killer | skill-dev-tools-code-quality | skill-to-skill |
| skill-dev-tools-bug-killer | skill-dev-tools-project-learnings | skill-to-skill |
| skill-dev-tools-bug-killer | agent-core-tools-code-explorer | cross-plugin |
| skill-dev-tools-bug-killer | agent-dev-tools-bug-investigator | agent-reference |
| skill-dev-tools-docs-manager | skill-core-tools-deep-analysis | cross-plugin |
| skill-dev-tools-docs-manager | agent-core-tools-code-explorer | cross-plugin |
| skill-dev-tools-docs-manager | agent-dev-tools-docs-writer | agent-reference |
| skill-dev-tools-feature-dev | skill-dev-tools-architecture-patterns | skill-to-skill |
| skill-dev-tools-feature-dev | skill-dev-tools-code-quality | skill-to-skill |
| skill-dev-tools-feature-dev | skill-dev-tools-changelog-format | skill-to-skill |
| skill-dev-tools-feature-dev | skill-core-tools-deep-analysis | cross-plugin |
| skill-dev-tools-feature-dev | skill-core-tools-language-patterns | cross-plugin |
| skill-dev-tools-feature-dev | agent-core-tools-code-architect | cross-plugin |
| skill-dev-tools-feature-dev | agent-dev-tools-code-reviewer | agent-reference |
| agent-dev-tools-docs-writer | skill-core-tools-technical-diagrams | cross-plugin |
| skill-dev-tools-release-python-package | agent-dev-tools-changelog-manager | agent-reference |
| hooks-core-tools-hooks | auto-approve-da-session.sh | hook-to-script |

## Circular References

No circular references detected.

## External Dependencies

| Source | External Dependency | Type |
|--------|-------------------|------|
| hooks-core-tools-hooks | bash ${CLAUDE_PLUGIN_ROOT}/hooks/auto-approve-da-session.sh | bash script |
| agent-dev-tools-changelog-manager | gh CLI (GitHub CLI) | system tool |

## Classification Counts

| Classification | Count |
|---------------|-------|
| Internal | 26 |
| External-selected | 0 |
| External-missing | 0 |
| External | 2 |
| System | 0 |
