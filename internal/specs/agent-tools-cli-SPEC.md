# agent-tools-cli PRD

**Version**: 1.0
**Author**: Stephen Sequenzia
**Date**: 2026-03-05
**Status**: Draft
**Spec Type**: New product
**Spec Depth**: High-level overview
**Description**: A Python-based CLI tool named `agent-tools` that simplifies discovering and importing skills and subagents into AI coding harnesses, removing the complexity of retrieval and correct file placement across different platforms.

---

## Executive Summary

`agent-tools` is a Python CLI built with Typer that serves as a universal skill/subagent installer for AI coding harnesses. It solves two key pain points: discovering skills scattered across multiple sources (local paths, git repos, registries) and routing them to the correct file locations for each target harness (Claude Code, OpenCode, Cursor/Windsurf, Codex).

## Problem Statement

### The Problem

Developers who want to use shared skills and subagents in their AI coding harness face a fragmented experience. Skills live in disparate locations — local directories, git repositories, and registries — with no unified way to find them. Once found, each harness expects files in different locations with different conventions, making manual installation error-prone and time-consuming.

### Current State

Users must manually discover skills through word-of-mouth, documentation, or browsing repositories. They then need to understand the target harness's file structure conventions and manually copy or symlink files into the correct locations. This process varies for every harness and has no tooling support.

### Impact

The lack of a standard installation workflow creates friction that limits skill adoption. Developers either avoid using shared skills entirely or spend unnecessary time on manual setup, reducing the value of the growing skill ecosystem.

## Proposed Solution

### Overview

A CLI tool (`agent-tools`) that provides three core commands: `config` for setting up sources and preferences, `list`/`search` for discovering available skills, and `install` for importing skills into any supported harness with automatic file placement.

### Key Features

| Feature | Description | Priority |
|---------|-------------|----------|
| `install` | Import a skill or subagent into a target harness with automatic file routing | P0 |
| `list` / `search` | Discover available skills across all configured sources | P0 |
| `config` | Configure skill sources (local, git, registry), default harness, and preferences | P0 |
| Multi-source support | Retrieve skills from local filesystem, git repositories, and registry/marketplace | P1 |
| Harness abstraction layer | Extensible architecture for adding new harness support | P1 |

## Success Metrics

| Metric | Current | Target | How Measured |
|--------|---------|--------|--------------|
| Skill install success rate | N/A | 100% across all 4 harnesses | Automated tests per harness |
| Time to first install | N/A | Under 1 minute for new users | User testing / onboarding flow |
| Supported harnesses | 0 | 4 (Claude Code, OpenCode, Cursor/Windsurf, Codex) | Feature completion |
| New harness integration effort | N/A | < 1 day to add a new harness | Measured by contributor experience |

## User Personas

### Primary User: Skill Consumer

- **Role**: Developer using an AI coding harness who wants to leverage community or team skills
- **Goals**: Quickly find and install skills into their preferred harness without learning each platform's file conventions
- **Pain Points**: Skills are scattered across sources; each harness has different installation paths and conventions; no single tool handles discovery and installation

## Scope

### In Scope

- CLI tool with `install`, `list`/`search`, and `config` commands
- Support for 4 harnesses: Claude Code, OpenCode, Cursor/Windsurf, Codex
- Multi-source skill retrieval: local filesystem, git repositories, registry/marketplace
- Configurable default harness and source preferences
- Extensible harness abstraction for future platform support

### Out of Scope

- Format conversion between harness-specific skill formats
- Publishing or authoring tools for skill creators
- Version pinning, upgrading, or dependency resolution
- GUI or web interface

## Implementation Phases

### Phase 1: Foundation

**Goal**: Establish project structure, configuration system, and harness abstraction layer

- Project scaffolding with Typer CLI framework
- `config` command for managing sources and default harness
- Harness abstraction interface (base class/protocol for file placement logic)
- Local filesystem source adapter

### Phase 2: Core Commands

**Goal**: Deliver the primary install and discovery workflows

- `install` command with automatic file routing per harness
- `list` / `search` commands across configured sources
- Harness implementations for Claude Code, OpenCode, Cursor/Windsurf, Codex
- Git repository source adapter

### Phase 3: Multi-Source & Polish

**Goal**: Complete source support and refine the user experience

- Registry/marketplace source adapter
- Improved search with filtering and metadata display
- Error handling and user-friendly messaging
- Documentation and onboarding guide

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Harness structural differences | High | High | Abstraction layer isolates harness-specific logic; research each harness's conventions upfront |
| No standard skill discovery mechanism | Medium | High | Define a lightweight skill manifest format for indexable metadata |
| Scope creep toward full package manager | Medium | Medium | Strict v1 scope boundaries; defer versioning and dependency resolution |
| Codex documentation gaps | Low | Medium | Investigate Codex file conventions early; fall back to community knowledge |

## Dependencies

- **Harness documentation**: Understanding each harness's file structure and plugin conventions (research required)
- **Typer framework**: Python CLI framework — stable, well-documented
- **Git access**: For git repository source adapter (requires git CLI or library)
- **Registry format**: If a central registry is planned, its API/format must be defined

## Open Questions

- What metadata format should skills expose for discovery (e.g., a manifest file)?
- Is there an existing or planned registry/marketplace, or should the tool define one?
- What are the exact file placement conventions for Codex?

## Stakeholder Sign-off

| Role | Name | Status |
|------|------|--------|
| Product | Stephen Sequenzia | Pending |
| Engineering | | Pending |

---

*Document generated by SDD Tools*
