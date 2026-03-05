# Execution Context

## Project Patterns
- Plugin naming: `agent-alchemy-{group-name}` for marketplace, `{group-name}` for directory
- Python projects use `uv` for package management, `ruff` for linting, `pytest` for testing
- Type hints on all functions and public APIs
- `uv init --lib` creates src layout; auto-adds workspace member to root pyproject.toml
- Typer sub-apps via `app.add_typer()` with `callback(invoke_without_command=True)`
- Shared venv at root level (`.venv/`) due to workspace membership
- `runtime_checkable` Protocol pattern for both SourceAdapter and HarnessAdapter
- Custom exceptions store structured attributes alongside human-readable message
- TOML config uses `tomllib` (stdlib 3.11+) for reading, simple serializer for writing
- Module-level `_override` variables for test-time dependency injection (config path, registry)
- Typer CLI: options must come BEFORE positional args in group callbacks
- GitSourceAdapter delegates scanning to LocalSourceAdapter after clone/fetch
- RegistrySourceAdapter uses stdlib `urllib.request` (no external HTTP deps)
- Harness file placement: Claude Code `.claude/`, OpenCode `.opencode/`, Cursor `.cursor/`, Codex `.codex/`

## Key Decisions
- This session builds the `agent-tools` CLI — a Python/Typer project for cross-harness skill management
- Package management: `uv` (not pip/poetry)
- CLI framework: Typer
- Linting: `ruff`
- Config storage: TOML at `~/.config/agent-tools/config.toml`
- Protocol pattern (not ABC) for adapter interfaces
- No external HTTP dependency — stdlib `urllib.request` for registry
- `create_default_registry()` factory for pre-populated harness registry

## Known Issues
- `--python-pin` flag doesn't exist in uv 0.9.21
- Concurrent file edits on `sources/__init__.py` required re-read during Wave 3

## File Map
- `agent-tools/pyproject.toml` - CLI project config with Typer dependency, entry point, ruff/pytest config
- `agent-tools/src/agent_tools/cli.py` - Main CLI entry point with 4 subcommand groups
- `agent-tools/src/agent_tools/__init__.py` - Package init with version
- `agent-tools/src/agent_tools/config.py` - Config model, TOML serialization, load/save
- `agent-tools/src/agent_tools/models.py` - SkillInfo and SkillContent frozen dataclasses
- `agent-tools/src/agent_tools/install.py` - Install logic: resolve_skill, copy_skill_to_harness
- `agent-tools/src/agent_tools/discovery.py` - Skill discovery: aggregate_skills, search_skills, format_skills_table
- `agent-tools/src/agent_tools/harnesses/` - HarnessAdapter Protocol + registry + 4 adapters (claude_code, opencode, cursor, codex)
- `agent-tools/src/agent_tools/sources/` - SourceAdapter Protocol + local, git, registry adapters
- `agent-tools/tests/` - 10 CLI + 21 config + 14 harness + 22 local + 23 install + 28 discovery + 42 adapter + 35 git + 44 registry tests

## Task History
### Prior Sessions Summary
Previous executions built tdd-tools, sdd-tools extensions, and claude-tools reference skills (28 tasks total, all passed). Waves 1-2 of this session scaffolded the CLI project and built config, harness interface, and local source adapter (4 tasks, all passed).

### Task [33]: Implement install command - PASS
- Files: install.py, cli.py, test_install.py (23 tests)
- Learnings: Typer group callbacks parse positional args first; options must precede positional args. Module-level `_registry_override` for test DI.

### Task [34]: Implement list and search commands - PASS
- Files: discovery.py, cli.py, test_discovery.py (28 tests)
- Learnings: Source aggregation collects errors separately for resilient multi-source querying. Table formatting with computed column widths.

### Task [35]: Implement harness adapters for all 4 platforms - PASS
- Files: claude_code.py, opencode.py, cursor.py, codex.py, __init__.py, test_harness_adapters.py (42 tests)
- Learnings: Each adapter takes `project_root: Path | None`. `create_default_registry()` factory for convenience.

### Task [36]: Implement git repository source adapter - PASS
- Files: git.py, test_git_source.py (35 tests), sources/__init__.py
- Learnings: Delegates scanning to LocalSourceAdapter. SSH URL regex split into protocol and shorthand patterns. Cache staleness via `.fetch_timestamp` marker.

### Task [37]: Implement registry/marketplace source adapter - PASS
- Files: registry.py, test_registry_source.py (44 tests), sources/__init__.py
- Learnings: stdlib `urllib.request` for HTTP. Custom exception hierarchy. Offline fallback reads stale cache. Integration tests use stdlib `http.server.HTTPServer`.
