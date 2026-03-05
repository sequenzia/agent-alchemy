"""Tests for the local filesystem source adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_tools.models import SkillContent
from agent_tools.sources.local import LocalSourceAdapter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def nested_skills_dir(tmp_path: Path) -> Path:
    """Create a directory with two nested skills."""
    skill_a = tmp_path / "skill-a"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text(
        "---\ndescription: A cool skill\n---\n# Skill A\nBody text.\n",
        encoding="utf-8",
    )
    (skill_a / "helpers.md").write_text("Helper content", encoding="utf-8")

    skill_b = tmp_path / "skill-b"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("# Skill B\nAnother skill description.\n", encoding="utf-8")

    return tmp_path


@pytest.fixture()
def flat_skill_dir(tmp_path: Path) -> Path:
    """Create a directory that itself is a single skill (flat layout)."""
    skill_dir = tmp_path / "my-flat-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\ndescription: Flat layout skill\n---\n# Flat\n",
        encoding="utf-8",
    )
    return skill_dir


@pytest.fixture()
def json_manifest_dir(tmp_path: Path) -> Path:
    """Create a skill with a JSON manifest."""
    skill = tmp_path / "json-skill"
    skill.mkdir()
    (skill / "manifest.json").write_text(
        '{"description": "JSON-based skill"}',
        encoding="utf-8",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Unit: Directory scanning logic
# ---------------------------------------------------------------------------


class TestListSkills:
    """Tests for list_skills directory scanning."""

    def test_nested_layout_discovers_skills(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        skills = adapter.list_skills()
        names = {s.name for s in skills}
        assert names == {"skill-a", "skill-b"}

    def test_flat_layout_discovers_skill(self, flat_skill_dir: Path) -> None:
        adapter = LocalSourceAdapter([flat_skill_dir])
        skills = adapter.list_skills()
        assert len(skills) == 1
        assert skills[0].name == "my-flat-skill"

    def test_returns_correct_metadata(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        skills = {s.name: s for s in adapter.list_skills()}
        skill_a = skills["skill-a"]
        assert skill_a.description == "A cool skill"
        assert skill_a.source == f"local:{nested_skills_dir}"
        assert skill_a.path == str(nested_skills_dir / "skill-a")

    def test_description_from_frontmatter(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        skills = {s.name: s for s in adapter.list_skills()}
        assert skills["skill-a"].description == "A cool skill"

    def test_description_fallback_to_body(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        skills = {s.name: s for s in adapter.list_skills()}
        # skill-b has no frontmatter; falls back to first non-heading line
        assert skills["skill-b"].description == "Another skill description."

    def test_json_manifest_description(self, json_manifest_dir: Path) -> None:
        adapter = LocalSourceAdapter([json_manifest_dir])
        skills = adapter.list_skills()
        assert len(skills) == 1
        assert skills[0].description == "JSON-based skill"

    def test_multiple_source_paths(self, nested_skills_dir: Path, flat_skill_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir, flat_skill_dir])
        skills = adapter.list_skills()
        names = {s.name for s in skills}
        assert names == {"skill-a", "skill-b", "my-flat-skill"}

    def test_empty_directory_returns_empty_list(self, tmp_path: Path) -> None:
        adapter = LocalSourceAdapter([tmp_path])
        assert adapter.list_skills() == []

    def test_nonexistent_path_warns_and_skips(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        missing = tmp_path / "does-not-exist"
        adapter = LocalSourceAdapter([missing])
        with caplog.at_level("WARNING"):
            skills = adapter.list_skills()
        assert skills == []
        assert "does not exist" in caplog.text

    def test_symlinked_directory_traversed(self, nested_skills_dir: Path, tmp_path: Path) -> None:
        link_path = tmp_path / "linked-skills"
        link_path.symlink_to(nested_skills_dir)
        adapter = LocalSourceAdapter([link_path])
        skills = adapter.list_skills()
        names = {s.name for s in skills}
        assert "skill-a" in names
        assert "skill-b" in names


# ---------------------------------------------------------------------------
# Unit: Search filtering
# ---------------------------------------------------------------------------


class TestSearch:
    """Tests for search substring matching."""

    def test_search_by_name(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        results = adapter.search("skill-a")
        assert len(results) == 1
        assert results[0].name == "skill-a"

    def test_search_by_description(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        results = adapter.search("cool")
        assert len(results) == 1
        assert results[0].name == "skill-a"

    def test_search_case_insensitive(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        results = adapter.search("COOL")
        assert len(results) == 1

    def test_search_no_match(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        results = adapter.search("zzz-nonexistent")
        assert results == []

    def test_search_matches_multiple(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        results = adapter.search("skill")
        assert len(results) == 2


# ---------------------------------------------------------------------------
# Unit: get_skill retrieval
# ---------------------------------------------------------------------------


class TestGetSkill:
    """Tests for get_skill content retrieval."""

    def test_get_existing_skill(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        content = adapter.get_skill("skill-a")
        assert isinstance(content, SkillContent)
        assert content.info.name == "skill-a"
        assert "SKILL.md" in content.files
        assert "helpers.md" in content.files

    def test_get_missing_skill_raises(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])
        with pytest.raises(KeyError, match="Skill not found"):
            adapter.get_skill("nonexistent-skill")


# ---------------------------------------------------------------------------
# Edge cases: Permission denied
# ---------------------------------------------------------------------------


class TestPermissionDenied:
    """Tests for permission-denied scenarios."""

    def test_permission_denied_on_directory(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        restricted = tmp_path / "restricted"
        restricted.mkdir()
        (restricted / "SKILL.md").write_text("# Restricted", encoding="utf-8")
        restricted.chmod(0o000)
        try:
            adapter = LocalSourceAdapter([restricted])
            with caplog.at_level("WARNING"):
                skills = adapter.list_skills()
            assert skills == []
            assert "Permission denied" in caplog.text
        finally:
            restricted.chmod(0o755)

    def test_permission_denied_on_subdirectory(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        good = tmp_path / "good-skill"
        good.mkdir()
        (good / "SKILL.md").write_text("# Good\nA good skill.\n", encoding="utf-8")

        bad = tmp_path / "bad-skill"
        bad.mkdir()
        (bad / "SKILL.md").write_text("# Bad", encoding="utf-8")
        bad.chmod(0o000)
        try:
            adapter = LocalSourceAdapter([tmp_path])
            with caplog.at_level("WARNING", logger="agent_tools.sources.local"):
                skills = adapter.list_skills()
            # Should still find the good skill
            names = {s.name for s in skills}
            assert "good-skill" in names
            assert "Permission denied" in caplog.text
        finally:
            bad.chmod(0o755)


# ---------------------------------------------------------------------------
# Edge case: Malformed manifest
# ---------------------------------------------------------------------------


class TestMalformedManifest:
    """Tests for malformed skill manifests."""

    def test_malformed_json_skipped_with_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        skill = tmp_path / "bad-json"
        skill.mkdir()
        (skill / "manifest.json").write_text("{invalid json", encoding="utf-8")
        adapter = LocalSourceAdapter([tmp_path])
        with caplog.at_level("WARNING"):
            skills = adapter.list_skills()
        # Malformed JSON returns empty description but is still listed
        # (the manifest exists, just description is empty)
        assert len(skills) == 1
        assert skills[0].description == ""


# ---------------------------------------------------------------------------
# Integration: End-to-end list from a test skill directory
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """Integration tests for full list -> search -> get workflow."""

    def test_full_workflow(self, nested_skills_dir: Path) -> None:
        adapter = LocalSourceAdapter([nested_skills_dir])

        # List all
        all_skills = adapter.list_skills()
        assert len(all_skills) == 2

        # Search
        search_results = adapter.search("cool")
        assert len(search_results) == 1
        assert search_results[0].name == "skill-a"

        # Get content
        content = adapter.get_skill("skill-a")
        assert "SKILL.md" in content.files
        assert "A cool skill" in content.files["SKILL.md"]
        assert content.info == search_results[0]

    def test_multiple_paths_integration(self, tmp_path: Path) -> None:
        """End-to-end: list skills from multiple local source paths."""
        dir1 = tmp_path / "source1"
        dir1.mkdir()
        s1 = dir1 / "alpha"
        s1.mkdir()
        (s1 / "SKILL.md").write_text("# Alpha\nAlpha skill.\n", encoding="utf-8")

        dir2 = tmp_path / "source2"
        dir2.mkdir()
        s2 = dir2 / "beta"
        s2.mkdir()
        (s2 / "SKILL.md").write_text("# Beta\nBeta skill.\n", encoding="utf-8")

        adapter = LocalSourceAdapter([dir1, dir2])
        skills = adapter.list_skills()
        names = {s.name for s in skills}
        assert names == {"alpha", "beta"}

        # Each skill has correct source
        sources = {s.name: s.source for s in skills}
        assert sources["alpha"] == f"local:{dir1}"
        assert sources["beta"] == f"local:{dir2}"
