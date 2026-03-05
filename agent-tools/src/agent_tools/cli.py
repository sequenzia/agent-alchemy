"""CLI entry point for agent-tools."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer

from agent_tools.config import (
    add_source,
    load_config,
    remove_source,
    save_config,
    validate_harness,
)
from agent_tools.discovery import (
    VALID_FORMATS,
    VALID_SKILL_TYPES,
    aggregate_skills,
    filter_skills,
    find_skill_by_name,
    format_skill_info,
    format_skills_json,
    format_skills_rich_table,
    format_skills_yaml,
    get_valid_source_paths,
    search_skills,
)
from agent_tools.harnesses.registry import HarnessNotFoundError, HarnessRegistry
from agent_tools.install import (
    DestinationNotWritableError,
    SkillNotFoundError,
    SourceUnreachableError,
    check_skill_exists,
    install_skill,
    resolve_harness,
)
from agent_tools.models import SkillInfo
from agent_tools.output import Console, Verbosity, get_console, set_console


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from agent_tools import __version__

        typer.echo(f"agent-tools {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="agent-tools",
    help="Universal skill/subagent installer for AI coding harnesses.",
    no_args_is_help=True,
)


@app.callback()
def app_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug-level output."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output."),
    version: Optional[bool] = typer.Option(  # noqa: UP007
        None, "--version", callback=_version_callback, is_eager=True, help="Show version."
    ),
) -> None:
    """Universal skill/subagent installer for AI coding harnesses."""
    if verbose and quiet:
        typer.echo("Error: --verbose and --quiet cannot be used together.", err=True)
        raise typer.Exit(code=1)

    if verbose:
        verbosity = Verbosity.VERBOSE
    elif quiet:
        verbosity = Verbosity.QUIET
    else:
        verbosity = Verbosity.NORMAL

    set_console(Console(verbosity=verbosity))


config_app = typer.Typer(help="Manage sources and default harness configuration.")
app.add_typer(config_app, name="config")

install_app = typer.Typer(help="Install skills and subagents into a target harness.")
app.add_typer(install_app, name="install")

list_app = typer.Typer(help="List available skills across configured sources.")
app.add_typer(list_app, name="list")

search_app = typer.Typer(help="Search for skills by name or keyword.")
app.add_typer(search_app, name="search")

info_app = typer.Typer(help="Show full metadata for a specific skill.")
app.add_typer(info_app, name="info")

# Allow overriding the config path for testing
_config_path_override: Path | None = None

# Allow overriding the harness registry for testing
_registry_override: HarnessRegistry | None = None


def _get_config_path() -> Path | None:
    """Return the config path override (if set) for the current invocation."""
    return _config_path_override


def _get_registry() -> HarnessRegistry:
    """Return the harness registry (override or default empty)."""
    if _registry_override is not None:
        return _registry_override
    return HarnessRegistry()


@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context) -> None:
    """Manage sources and default harness configuration."""
    if ctx.invoked_subcommand is None:
        get_console().info("Config management. Use --help to see available subcommands.")


@config_app.command("set")
def config_set(
    key: str = typer.Argument(help="Configuration key to set."),
    value: str = typer.Argument(help="Value to assign."),
) -> None:
    """Set a configuration value."""
    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    console = get_console()
    if key == "default_harness":
        error = validate_harness(value)
        if error:
            console.error(error, hint="Valid harnesses: claude-code, opencode, cursor, codex")
            raise typer.Exit(code=1)
        config.default_harness = value
    else:
        console.error(
            f"Unknown config key '{key}'.",
            hint="Valid keys: default_harness",
        )
        raise typer.Exit(code=1)

    save_config(config, config_path=config_path)
    console.success(f"Set {key} = {value}")


@config_app.command("get")
def config_get(
    key: str = typer.Argument(help="Configuration key to retrieve."),
) -> None:
    """Get a configuration value."""
    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    console = get_console()
    if key == "default_harness":
        console.plain_always(config.default_harness)
    elif key == "sources":
        if not config.sources:
            console.info("No sources configured.")
        else:
            for s in config.sources:
                console.plain_always(f"  [{s.type}] {s.path}")
    else:
        console.error(
            f"Unknown config key '{key}'.",
            hint="Valid keys: default_harness, sources",
        )
        raise typer.Exit(code=1)


@config_app.command("list")
def config_list() -> None:
    """Show all current configuration."""
    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    console = get_console()
    console.plain_always(f"default_harness = {config.default_harness}")
    console.plain_always("")
    console.plain_always("sources:")
    if not config.sources:
        console.plain_always("  (none)")
    else:
        for s in config.sources:
            console.plain_always(f"  [{s.type}] {s.path}")


@config_app.command("add-source")
def config_add_source(
    source_type: str = typer.Argument(help="Source type (e.g. 'local', 'git', 'registry')."),
    path: str = typer.Argument(help="Filesystem path or URL for the source."),
) -> None:
    """Add a skill source."""
    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    console = get_console()

    # Warn if local path doesn't exist but still save
    if source_type == "local" and not Path(path).exists():
        console.warning(f"Path '{path}' does not exist.")

    config = add_source(config, source_type, path)
    save_config(config, config_path=config_path)
    console.success(f"Added source: [{source_type}] {path}")


@config_app.command("remove-source")
def config_remove_source(
    path: str = typer.Argument(help="Path of the source to remove."),
) -> None:
    """Remove a skill source by path."""
    config_path = _get_config_path()
    config = load_config(config_path=config_path)
    config, removed = remove_source(config, path)
    save_config(config, config_path=config_path)

    console = get_console()
    if removed:
        console.success(f"Removed source: {path}")
    else:
        console.warning(f"No source found with path: {path}")


@install_app.callback(invoke_without_command=True)
def install_callback(
    ctx: typer.Context,
    skill_name: str = typer.Argument(None, help="Name of the skill to install."),
    harness: str = typer.Option(
        None, "--harness", help="Target harness (overrides default)."
    ),
    source: str = typer.Option(
        None, "--source", help="Specific source to search (not yet implemented)."
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite if skill already installed."
    ),
) -> None:
    """Install a skill or subagent into a target harness."""
    if ctx.invoked_subcommand is not None:
        return

    if skill_name is None:
        typer.echo("Usage: agent-tools install <skill-name> [--harness <name>]")
        typer.echo("Run 'agent-tools install --help' for more information.")
        return

    config_path = _get_config_path()
    config = load_config(config_path=config_path)
    registry = _get_registry()

    console = get_console()

    # Validate harness name early
    harness_name = harness or config.default_harness
    try:
        adapter = resolve_harness(harness_name, registry)
    except HarnessNotFoundError as e:
        available = ", ".join(e.available) if e.available else "(none)"
        console.error(
            f"Invalid harness '{e.name}'.",
            hint=f"Available harnesses: {available}",
        )
        raise typer.Exit(code=1) from None

    # Check if already installed
    if not force and check_skill_exists(skill_name, adapter):
        console.warning(
            f"Skill '{skill_name}' is already installed in "
            f"{adapter.get_harness_name()}."
        )
        console.info("Use --force to overwrite.")
        raise typer.Exit(code=1)

    # Perform installation
    try:
        used_harness, installed_files = install_skill(
            skill_name, config, registry, harness_override=harness
        )
    except SkillNotFoundError as e:
        console.error(
            str(e),
            hint="Check skill name spelling or add more sources with "
            "'agent-tools config add-source'.",
        )
        raise typer.Exit(code=1) from None
    except SourceUnreachableError as e:
        console.error(
            str(e),
            hint="Check network connection or verify the source path exists.",
        )
        raise typer.Exit(code=1) from None
    except DestinationNotWritableError as e:
        console.error(
            str(e),
            hint="Check file permissions on the destination directory.",
        )
        raise typer.Exit(code=1) from None

    # Display success summary
    harness_display = adapter.get_harness_name()
    console.success(f"Installed '{skill_name}' into {harness_display}:")
    for rel_path, dest_path in installed_files:
        console.info(f"  {rel_path} -> {dest_path}")


@list_app.callback(invoke_without_command=True)
def list_callback(
    ctx: typer.Context,
    source: str = typer.Option(None, "--source", "-s", help="Filter to a specific source path."),
    skill_type: str = typer.Option(
        None, "--type", "-t", help="Filter by type: skill or agent."
    ),
    harness: str = typer.Option(
        None, "--harness", help="Show only skills compatible with this harness."
    ),
    fmt: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or yaml."
    ),
) -> None:
    """List available skills across configured sources."""
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    # Validate --type flag
    if skill_type is not None and skill_type not in VALID_SKILL_TYPES:
        console.error(
            f"Invalid type '{skill_type}'.",
            hint=f"Valid types: {', '.join(VALID_SKILL_TYPES)}",
        )
        raise typer.Exit(code=1)

    # Validate --format flag
    if fmt not in VALID_FORMATS:
        console.error(
            f"Invalid format '{fmt}'.",
            hint=f"Valid formats: {', '.join(VALID_FORMATS)}",
        )
        raise typer.Exit(code=1)

    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    if not config.sources:
        console.info("No sources configured.")
        console.info("Run 'agent-tools config add-source' to add one.")
        return

    # Validate --source flag
    if source is not None:
        valid_paths = get_valid_source_paths(config)
        if source not in valid_paths:
            console.error(
                f"Unknown source '{source}'.",
                hint=f"Valid sources: {', '.join(valid_paths)}",
            )
            raise typer.Exit(code=1)

    skills, errors = aggregate_skills(config, source_filter=source)

    # Print warnings for unreachable sources
    for err in errors:
        console.warning(
            f"Could not query source [{err.source.type}] "
            f"{err.source.path}: {err.error}"
        )

    # Apply filters
    skills = filter_skills(skills, skill_type=skill_type, harness=harness)

    if not skills:
        filter_desc = _describe_filters(skill_type=skill_type, harness=harness, source=source)
        if filter_desc:
            console.info(f"No skills found matching filters: {filter_desc}.")
            console.info("Try broadening your filters or check available options.")
        else:
            console.info("No skills found.")
        return

    output = _format_output(skills, fmt)
    _emit_output(output, fmt, console)
    if fmt == "table":
        console.info(f"\n{len(skills)} skill(s) found.")


@search_app.callback(invoke_without_command=True)
def search_callback(
    ctx: typer.Context,
    query: str = typer.Argument(
        None, help="Search query to match against skill names and descriptions."
    ),
    source: str = typer.Option(None, "--source", "-s", help="Filter to a specific source path."),
    skill_type: str = typer.Option(
        None, "--type", "-t", help="Filter by type: skill or agent."
    ),
    harness: str = typer.Option(
        None, "--harness", help="Show only skills compatible with this harness."
    ),
    fmt: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or yaml."
    ),
) -> None:
    """Search for skills by name or keyword."""
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    if query is None:
        console.info("Usage: agent-tools search <query> [--source <path>]")
        console.info("Run 'agent-tools search --help' for more information.")
        return

    # Validate --type flag
    if skill_type is not None and skill_type not in VALID_SKILL_TYPES:
        console.error(
            f"Invalid type '{skill_type}'.",
            hint=f"Valid types: {', '.join(VALID_SKILL_TYPES)}",
        )
        raise typer.Exit(code=1)

    # Validate --format flag
    if fmt not in VALID_FORMATS:
        console.error(
            f"Invalid format '{fmt}'.",
            hint=f"Valid formats: {', '.join(VALID_FORMATS)}",
        )
        raise typer.Exit(code=1)

    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    if not config.sources:
        console.info("No sources configured.")
        console.info("Run 'agent-tools config add-source' to add one.")
        return

    # Validate --source flag
    if source is not None:
        valid_paths = get_valid_source_paths(config)
        if source not in valid_paths:
            console.error(
                f"Unknown source '{source}'.",
                hint=f"Valid sources: {', '.join(valid_paths)}",
            )
            raise typer.Exit(code=1)

    skills, errors = search_skills(config, query, source_filter=source)

    # Print warnings for unreachable sources
    for err in errors:
        console.warning(
            f"Could not query source [{err.source.type}] "
            f"{err.source.path}: {err.error}"
        )

    # Apply filters
    skills = filter_skills(skills, skill_type=skill_type, harness=harness)

    if not skills:
        filter_desc = _describe_filters(
            skill_type=skill_type, harness=harness, source=source, query=query
        )
        if filter_desc:
            console.info(f"No skills found matching filters: {filter_desc}.")
            console.info("Try broadening your filters or check available options.")
        else:
            console.info(f"No skills found matching '{query}'.")
        return

    output = _format_output(skills, fmt)
    _emit_output(output, fmt, console)
    if fmt == "table":
        console.info(f"\n{len(skills)} skill(s) found matching '{query}'.")


@info_app.callback(invoke_without_command=True)
def info_callback(
    ctx: typer.Context,
    name: str = typer.Argument(None, help="Name of the skill to show details for."),
    source: str = typer.Option(None, "--source", "-s", help="Filter to a specific source path."),
    fmt: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, or yaml."
    ),
) -> None:
    """Show full metadata for a specific skill."""
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    if name is None:
        console.info("Usage: agent-tools info <skill-name>")
        console.info("Run 'agent-tools info --help' for more information.")
        return

    # Validate --format flag
    if fmt not in VALID_FORMATS:
        console.error(
            f"Invalid format '{fmt}'.",
            hint=f"Valid formats: {', '.join(VALID_FORMATS)}",
        )
        raise typer.Exit(code=1)

    config_path = _get_config_path()
    config = load_config(config_path=config_path)

    if not config.sources:
        console.info("No sources configured.")
        console.info("Run 'agent-tools config add-source' to add one.")
        return

    skill = find_skill_by_name(config, name, source_filter=source)
    if skill is None:
        console.error(
            f"Skill '{name}' not found.",
            hint="Run 'agent-tools list' to see available skills.",
        )
        raise typer.Exit(code=1)

    if fmt == "json":
        _emit_output(format_skills_json([skill]), fmt, console)
    elif fmt == "yaml":
        _emit_output(format_skills_yaml([skill]), fmt, console)
    else:
        _emit_output(format_skill_info(skill), fmt, console)


def _emit_output(output: str, fmt: str, console: Console) -> None:
    """Emit formatted output, using print() for machine-readable formats.

    JSON and YAML bypass Rich to avoid line wrapping that would
    break machine-readable formatting.
    """
    if fmt in ("json", "yaml"):
        print(output)  # noqa: T201
    else:
        console.plain_always(output)


def _format_output(skills: list[SkillInfo], fmt: str) -> str:
    """Format skills according to the specified output format."""
    if fmt == "json":
        return format_skills_json(skills)
    if fmt == "yaml":
        return format_skills_yaml(skills)
    return format_skills_rich_table(skills)


def _describe_filters(
    *,
    skill_type: str | None = None,
    harness: str | None = None,
    source: str | None = None,
    query: str | None = None,
) -> str:
    """Build a human-readable description of active filters."""
    parts: list[str] = []
    if query:
        parts.append(f"query='{query}'")
    if skill_type:
        parts.append(f"type={skill_type}")
    if harness:
        parts.append(f"harness={harness}")
    if source:
        parts.append(f"source={source}")
    return ", ".join(parts)


def _check_python_version() -> None:
    """Exit gracefully if Python version is below 3.10."""
    if sys.version_info < (3, 10):
        typer.echo(
            f"Error: agent-tools requires Python 3.10 or later. "
            f"Current version: {sys.version_info.major}.{sys.version_info.minor}",
            err=True,
        )
        raise SystemExit(1)


def main() -> None:
    """Main entry point with version check, clean Ctrl+C, and top-level exception handling."""
    _check_python_version()
    try:
        app()
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C with no stack trace
        from agent_tools.output import reset_console

        reset_console()
        raise SystemExit(130)
    except Exception as exc:
        # Catch unhandled exceptions at top level with bug report suggestion
        from agent_tools.output import format_bug_report

        sys.stderr.write(format_bug_report(exc) + "\n")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
