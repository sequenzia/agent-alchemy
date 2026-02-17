# Execution Plan

## Session Info
- **Execution ID**: exec-session-20260217-102648
- **Task Count**: 18
- **Max Parallel**: 5
- **Retries**: 3
- **Source Spec**: internal/specs/plugin-porting-SPEC.md

## Wave Schedule

### Wave 1 — Foundation (3 tasks)
- #30: Create port-tools plugin group scaffold
- #31: Define adapter file format specification
- #33: Create research agent definition

### Wave 2 — Core Components (2 tasks)
- #32: Research and create OpenCode platform adapter (← #31)
- #34: Implement porter skill with plugin selection wizard (← #30)

### Wave 3a — Conversion Engines, Batch 1 (5 tasks)
- #36: Implement skill conversion engine (← #31, #32, #34)
- #37: Implement agent conversion engine (← #31, #32, #34)
- #38: Integrate research subagent (← #33, #34)
- #40: Implement hook converter (← #31, #32, #34)
- #41: Implement reference file converter (← #34)

### Wave 3b — Conversion Engines, Batch 2 (2 tasks)
- #42: Implement MCP config converter (← #31, #32, #34)
- #35: Implement dependency graph pre-check (← #34)

### Wave 4 — Orchestration & Scoring (5 tasks)
- #39: Incompatibility resolver (← #36)
- #43: Converted file writer (← #36, #37, #40, #41, #42)
- #46: Fidelity scoring system (← #36, #37, #40, #41, #42)
- #47: Dry-run preview mode (← #35, #38)
- #48: Adapter version staleness checker (← #38, #32)

### Wave 5 — Output Generation (2 tasks)
- #44: Migration guide generator (← #43, #39)
- #45: Gap report generator (← #39)
