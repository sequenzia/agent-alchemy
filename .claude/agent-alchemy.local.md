---
author: Steph Sequenzia
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
---