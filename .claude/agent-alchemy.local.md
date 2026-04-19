---
author: Stephen Sequenzia
spec-output-path: internal/specs/
deep-analysis:
  - direct-approval: true
  - cross-skill-approval: false
execute-tasks:
  - max_parallel: 5
tdd:
  framework: auto                    # auto | pytest | jest | vitest
  coverage-threshold: 80             # Minimum coverage percentage (0-100)
  strictness: normal                 # strict | normal | relaxed
  test-review-threshold: 70          # Minimum test quality score (0-100)
  test-review-on-generate: false     # Run test-reviewer after generate-tests
interview-me:
  default-depth: detailed            # overview | detailed | deep-dive
  default-output-type: report-detailed  # report-detailed | report-summary | implementation-plan | something-else
  output-directory: internal/interviews/
  proactive-research-budget: 3       # 0 disables proactive research
  enable-context-argument: true
  slug-collision-strategy: timestamp-suffix  # timestamp-suffix | prompt
---