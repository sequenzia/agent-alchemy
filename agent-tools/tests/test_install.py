"""Tests for the install command — source resolution, file routing, and CLI integration."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from agent_tools.config import Config, SourceEntry
from agent_tools.harnesses.registry import HarnessNotFoundError, HarnessRegistry
from agent_tools.install import (
    SkillNotFoundError,
    SourceUnreachableError,
    check_skill_exists,
    copy_skill_to_harness,
    install_skill,
    resolve_skill,
)
from agent_tools.models import SkillContent, SkillInfo

runner = CliRunner()

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class FakeHarness:
    """A harness adapter that writes to a temporary directory."""

    def __init__(self, dest_root: Path, name: str = "fake-harness") -> None:
        self._dest_root = dest_root
        self._name = name

    def get_skill_path(self, skill_name: str) -> Path:
        return self._dest_root / "skills" / skill_name

    def get_agent_path(self, agent_name: str) -> Path:
        return self._dest_root / "agents" / agent_name

    def get_harness_name(self) -> str:
        return self._name

    def detect(self) -> bool:
        return False


@pytest.fixture()
def source_dir(tmp_path: Path) -> Path:
    """Create a source directory with two skills."""
    src = tmp_path / "source"
    src.mkdir()

    skill_a = src / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text(
        "---\ndescription: Skill A\n---\n# Skill A\n", encoding="utf-8"
    )
    (skill_a / "helpers.md").write_text("Helper content", encoding="utf-8")

    skill_b = src / "skill-b"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("# Skill B\nB description.\n", encoding="utf-8")

    return src


@pytest.fixture()
def dest_dir(tmp_path: Path) -> Path:
    """Create a destination directory for harness output."""
    dest = tmp_path / "dest"
    dest.mkdir()
    return dest


@pytest.fixture()
def registry(dest_dir: Path) -> HarnessRegistry:
    """Create a registry with a fake harness."""
    reg = HarnessRegistry()
    reg.register("fake", FakeHarness(dest_dir, name="Fake Harness"))
    return reg


@pytest.fixture()
def config(source_dir: Path) -> Config:
    """Create a config pointing to the test source."""
    return Config(
        default_harness="fake",
        sources=[SourceEntry(type="local", path=str(source_dir))],
    )


# ---------------------------------------------------------------------------
# Unit: Source resolution logic (try sources in order)
# ---------------------------------------------------------------------------


class TestResolveSkill:
    """Test resolve_skill tries sources in order."""

    def test_resolves_from_first_source(self, source_dir: Path) -> None:
        sources = [SourceEntry(type="local", path=str(source_dir))]
        content = resolve_skill("skill-a", sources)
        assert content.info.name == "skill-a"
        assert "SKILL.md" in content.files

    def test_resolves_from_second_source(self, tmp_path: Path) -> None:
        """If first source doesn't have the skill, check second."""
        empty = tmp_path / "empty-source"
        empty.mkdir()

        real = tmp_path / "real-source"
        real.mkdir()
        skill = real / "target-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Target\n", encoding="utf-8")

        sources = [
            SourceEntry(type="local", path=str(empty)),
            SourceEntry(type="local", path=str(real)),
        ]
        content = resolve_skill("target-skill", sources)
        assert content.info.name == "target-skill"

    def test_not_found_in_any_source(self, source_dir: Path) -> None:
        sources = [SourceEntry(type="local", path=str(source_dir))]
        with pytest.raises(SkillNotFoundError) as exc_info:
            resolve_skill("nonexistent", sources)
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.sources_tried

    def test_no_sources_configured(self) -> None:
        with pytest.raises(SkillNotFoundError) as exc_info:
            resolve_skill("anything", [])
        assert "no sources configured" in str(exc_info.value)

    def test_unreachable_source(self, tmp_path: Path) -> None:
        missing = tmp_path / "does-not-exist"
        sources = [SourceEntry(type="local", path=str(missing))]
        with pytest.raises(SourceUnreachableError) as exc_info:
            resolve_skill("any", sources)
        assert "does not exist" in str(exc_info.value)

    def test_unsupported_source_type_skipped(self, source_dir: Path) -> None:
        """Unsupported source types (e.g. git) are silently skipped."""
        sources = [
            SourceEntry(type="git", path="https://example.com/repo.git"),
            SourceEntry(type="local", path=str(source_dir)),
        ]
        content = resolve_skill("skill-a", sources)
        assert content.info.name == "skill-a"


# ---------------------------------------------------------------------------
# Unit: File routing per harness
# ---------------------------------------------------------------------------


class TestCopySkillToHarness:
    """Test copy_skill_to_harness routes files correctly."""

    def test_copies_files_to_harness_path(
        self, source_dir: Path, dest_dir: Path
    ) -> None:
        adapter = FakeHarness(dest_dir)
        info = SkillInfo(
            name="skill-a",
            description="Skill A",
            source=f"local:{source_dir}",
            path=str(source_dir / "skill-a"),
        )
        content = SkillContent(
            info=info,
            files={"SKILL.md": "# Skill A\n", "helpers.md": "Helper content"},
        )
        installed = copy_skill_to_harness(content, adapter)
        assert len(installed) >= 2

        dest_skill = dest_dir / "skills" / "skill-a"
        assert (dest_skill / "SKILL.md").exists()
        assert (dest_skill / "helpers.md").exists()

    def test_creates_destination_directories(
        self, source_dir: Path, dest_dir: Path
    ) -> None:
        adapter = FakeHarness(dest_dir)
        info = SkillInfo(
            name="skill-a",
            description="Skill A",
            source=f"local:{source_dir}",
            path=str(source_dir / "skill-a"),
        )
        content = SkillContent(info=info, files={"SKILL.md": "# A\n"})
        copy_skill_to_harness(content, adapter)
        assert (dest_dir / "skills" / "skill-a").is_dir()

    def test_multi_file_skill(self, tmp_path: Path, dest_dir: Path) -> None:
        """Skills with multiple files (including subdirs) are fully copied."""
        src = tmp_path / "multi-src"
        src.mkdir()
        skill = src / "multi-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Multi\n", encoding="utf-8")
        refs = skill / "references"
        refs.mkdir()
        (refs / "guide.md").write_text("Reference guide", encoding="utf-8")
        (refs / "patterns.md").write_text("Patterns", encoding="utf-8")

        adapter = FakeHarness(dest_dir)
        info = SkillInfo(
            name="multi-skill",
            description="Multi",
            source=f"local:{src}",
            path=str(skill),
        )
        content = SkillContent(info=info, files={})
        installed = copy_skill_to_harness(content, adapter)

        dest_skill = dest_dir / "skills" / "multi-skill"
        assert (dest_skill / "SKILL.md").exists()
        assert (dest_skill / "references" / "guide.md").exists()
        assert (dest_skill / "references" / "patterns.md").exists()
        assert len(installed) == 3

    def test_fallback_to_memory_content(self, dest_dir: Path) -> None:
        """When source dir doesn't exist, writes from in-memory files dict."""
        adapter = FakeHarness(dest_dir)
        info = SkillInfo(
            name="remote-skill",
            description="From remote",
            source="registry:example",
            path="/nonexistent/path",
        )
        content = SkillContent(
            info=info,
            files={"SKILL.md": "# Remote\n", "config.yaml": "key: value\n"},
        )
        installed = copy_skill_to_harness(content, adapter)
        assert len(installed) == 2
        dest_skill = dest_dir / "skills" / "remote-skill"
        assert (dest_skill / "SKILL.md").read_text(encoding="utf-8") == "# Remote\n"
        assert (dest_skill / "config.yaml").read_text(encoding="utf-8") == "key: value\n"


# ---------------------------------------------------------------------------
# Unit: check_skill_exists
# ---------------------------------------------------------------------------


class TestCheckSkillExists:
    """Test skill existence checking."""

    def test_not_installed(self, dest_dir: Path) -> None:
        adapter = FakeHarness(dest_dir)
        assert check_skill_exists("absent", adapter) is False

    def test_installed_with_files(self, dest_dir: Path) -> None:
        adapter = FakeHarness(dest_dir)
        skill_dir = dest_dir / "skills" / "present"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Present\n", encoding="utf-8")
        assert check_skill_exists("present", adapter) is True

    def test_empty_dir_not_considered_installed(self, dest_dir: Path) -> None:
        adapter = FakeHarness(dest_dir)
        skill_dir = dest_dir / "skills" / "empty"
        skill_dir.mkdir(parents=True)
        assert check_skill_exists("empty", adapter) is False


# ---------------------------------------------------------------------------
# Integration: Full install workflow (resolve -> route -> copy)
# ---------------------------------------------------------------------------


class TestInstallSkill:
    """Integration tests for install_skill end-to-end."""

    def test_full_install(
        self, config: Config, registry: HarnessRegistry, dest_dir: Path
    ) -> None:
        harness_name, installed = install_skill("skill-a", config, registry)
        assert harness_name == "fake"
        assert len(installed) >= 2

        dest_skill = dest_dir / "skills" / "skill-a"
        assert (dest_skill / "SKILL.md").exists()
        assert (dest_skill / "helpers.md").exists()

    def test_harness_override(
        self, config: Config, dest_dir: Path, tmp_path: Path
    ) -> None:
        alt_dest = tmp_path / "alt-dest"
        alt_dest.mkdir()
        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(dest_dir))
        registry.register("alt", FakeHarness(alt_dest, name="Alt Harness"))

        harness_name, installed = install_skill(
            "skill-a", config, registry, harness_override="alt"
        )
        assert harness_name == "alt"
        assert (alt_dest / "skills" / "skill-a" / "SKILL.md").exists()
        # Original dest should NOT have the skill
        assert not (dest_dir / "skills" / "skill-a").exists()

    def test_invalid_harness(self, config: Config) -> None:
        registry = HarnessRegistry()
        registry.register("valid", FakeHarness(Path("/tmp")))
        with pytest.raises(HarnessNotFoundError) as exc_info:
            install_skill("skill-a", config, registry, harness_override="bogus")
        assert "bogus" in str(exc_info.value)
        assert "valid" in str(exc_info.value)

    def test_skill_not_found(self, config: Config, registry: HarnessRegistry) -> None:
        with pytest.raises(SkillNotFoundError):
            install_skill("nonexistent-skill", config, registry)


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestInstallCLI:
    """Test the install CLI command via Typer runner."""

    def test_install_success(
        self, source_dir: Path, dest_dir: Path, tmp_path: Path
    ) -> None:
        from agent_tools import cli

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="fake",
            sources=[SourceEntry(type="local", path=str(source_dir))],
        )
        from agent_tools.config import save_config

        save_config(config, config_path=config_path)

        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(dest_dir, name="Fake Harness"))

        old_config = cli._config_path_override
        old_registry = cli._registry_override
        try:
            cli._config_path_override = config_path
            cli._registry_override = registry
            result = runner.invoke(cli.app, ["install", "skill-a"])
            assert result.exit_code == 0
            assert "Installed 'skill-a' into Fake Harness" in result.output
            assert "SKILL.md" in result.output
        finally:
            cli._config_path_override = old_config
            cli._registry_override = old_registry

    def test_install_not_found(
        self, source_dir: Path, dest_dir: Path, tmp_path: Path
    ) -> None:
        from agent_tools import cli
        from agent_tools.config import save_config

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="fake",
            sources=[SourceEntry(type="local", path=str(source_dir))],
        )
        save_config(config, config_path=config_path)

        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(dest_dir))

        old_config = cli._config_path_override
        old_registry = cli._registry_override
        try:
            cli._config_path_override = config_path
            cli._registry_override = registry
            result = runner.invoke(cli.app, ["install", "no-such-skill"])
            assert result.exit_code == 1
            output = result.output.lower()
            assert "not found" in output
        finally:
            cli._config_path_override = old_config
            cli._registry_override = old_registry

    def test_install_invalid_harness(
        self, source_dir: Path, tmp_path: Path
    ) -> None:
        from agent_tools import cli
        from agent_tools.config import save_config

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="fake",
            sources=[SourceEntry(type="local", path=str(source_dir))],
        )
        save_config(config, config_path=config_path)

        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(tmp_path))

        old_config = cli._config_path_override
        old_registry = cli._registry_override
        try:
            cli._config_path_override = config_path
            cli._registry_override = registry
            result = runner.invoke(cli.app, ["install", "--harness", "bogus", "skill-a"])
            assert result.exit_code == 1
            assert "bogus" in result.output.lower() or "invalid" in result.output.lower()
        finally:
            cli._config_path_override = old_config
            cli._registry_override = old_registry

    def test_install_already_exists_without_force(
        self, source_dir: Path, dest_dir: Path, tmp_path: Path
    ) -> None:
        from agent_tools import cli
        from agent_tools.config import save_config

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="fake",
            sources=[SourceEntry(type="local", path=str(source_dir))],
        )
        save_config(config, config_path=config_path)

        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(dest_dir, name="Fake Harness"))

        # Pre-install the skill
        skill_dest = dest_dir / "skills" / "skill-a"
        skill_dest.mkdir(parents=True)
        (skill_dest / "SKILL.md").write_text("# Old\n", encoding="utf-8")

        old_config = cli._config_path_override
        old_registry = cli._registry_override
        try:
            cli._config_path_override = config_path
            cli._registry_override = registry
            result = runner.invoke(cli.app, ["install", "skill-a"])
            assert result.exit_code == 1
            assert "already installed" in result.output.lower()
            assert "--force" in result.output
        finally:
            cli._config_path_override = old_config
            cli._registry_override = old_registry

    def test_install_with_force_overwrites(
        self, source_dir: Path, dest_dir: Path, tmp_path: Path
    ) -> None:
        from agent_tools import cli
        from agent_tools.config import save_config

        config_path = tmp_path / "config.toml"
        config = Config(
            default_harness="fake",
            sources=[SourceEntry(type="local", path=str(source_dir))],
        )
        save_config(config, config_path=config_path)

        registry = HarnessRegistry()
        registry.register("fake", FakeHarness(dest_dir, name="Fake Harness"))

        # Pre-install with old content
        skill_dest = dest_dir / "skills" / "skill-a"
        skill_dest.mkdir(parents=True)
        (skill_dest / "SKILL.md").write_text("# Old\n", encoding="utf-8")

        old_config = cli._config_path_override
        old_registry = cli._registry_override
        try:
            cli._config_path_override = config_path
            cli._registry_override = registry
            result = runner.invoke(cli.app, ["install", "--force", "skill-a"])
            assert result.exit_code == 0
            assert "Installed" in result.output
            # Verify content was overwritten
            new_content = (skill_dest / "SKILL.md").read_text(encoding="utf-8")
            assert "Skill A" in new_content
        finally:
            cli._config_path_override = old_config
            cli._registry_override = old_registry

    def test_install_no_args_shows_usage(self) -> None:
        from agent_tools import cli

        result = runner.invoke(cli.app, ["install"])
        assert result.exit_code == 0
        assert "usage" in result.output.lower() or "agent-tools install" in result.output.lower()
