#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:?Usage: $0 <source-dir> (e.g., ported/20260310)}"

# Validate source directory structure
for subdir in full nested flat; do
  if [[ ! -d "$SOURCE_DIR/$subdir" ]]; then
    echo "Error: $SOURCE_DIR/$subdir does not exist"
    exit 1
  fi
done

ALL_DIR="$SOURCE_DIR/all"

# Warn-and-copy helper: prints a warning if the target already exists, then copies
warn_cp() {
  local src="$1" dest="$2" group="$3"
  if [[ -e "$dest" ]]; then
    echo "Warning: overwriting $(basename "$dest") (from $group)"
  fi
  cp -r "$src" "$dest"
}

# Create target directories
mkdir -p "$ALL_DIR/skills" "$ALL_DIR/agents" "$ALL_DIR/hooks" "$ALL_DIR/skills-nested" "$ALL_DIR/skills-flat"

# --- Process full/ variant ---
for group_dir in "$SOURCE_DIR/full"/*/; do
  group_name=$(basename "$group_dir")

  # Copy skill directories
  if [[ -d "$group_dir/skills" ]]; then
    for skill_dir in "$group_dir/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      skill_name=$(basename "$skill_dir")
      warn_cp "$skill_dir" "$ALL_DIR/skills/${skill_name}" "$group_name"
    done
  fi

  # Copy agent .md files
  if [[ -d "$group_dir/agents" ]]; then
    for agent_file in "$group_dir/agents"/*.md; do
      [[ -f "$agent_file" ]] || continue
      agent_name=$(basename "$agent_file" .md)
      warn_cp "$agent_file" "$ALL_DIR/agents/${agent_name}.md" "$group_name"
    done
  fi

  # Copy hooks preserving group structure
  if [[ -d "$group_dir/hooks" ]]; then
    mkdir -p "$ALL_DIR/hooks/$group_name"
    cp -r "$group_dir/hooks/"* "$ALL_DIR/hooks/$group_name/"
  fi
done

# --- Process nested/ variant ---
for group_dir in "$SOURCE_DIR/nested"/*/; do
  group_name=$(basename "$group_dir")

  if [[ -d "$group_dir/skills" ]]; then
    # Copy skill directories
    for skill_dir in "$group_dir/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      skill_name=$(basename "$skill_dir")
      warn_cp "$skill_dir" "$ALL_DIR/skills-nested/${skill_name}" "$group_name"
    done

    # Copy loose .md files
    for md_file in "$group_dir/skills"/*.md; do
      [[ -f "$md_file" ]] || continue
      filename=$(basename "$md_file")
      warn_cp "$md_file" "$ALL_DIR/skills-nested/${filename}" "$group_name"
    done
  fi
done

# --- Process flat/ variant ---
for group_dir in "$SOURCE_DIR/flat"/*/; do
  group_name=$(basename "$group_dir")

  if [[ -d "$group_dir/skills" ]]; then
    # Copy skill directories
    for skill_dir in "$group_dir/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      skill_name=$(basename "$skill_dir")
      warn_cp "$skill_dir" "$ALL_DIR/skills-flat/${skill_name}" "$group_name"
    done

    # Copy loose .md files
    for md_file in "$group_dir/skills"/*.md; do
      [[ -f "$md_file" ]] || continue
      filename=$(basename "$md_file")
      warn_cp "$md_file" "$ALL_DIR/skills-flat/${filename}" "$group_name"
    done
  fi
done

echo "Consolidated into $ALL_DIR/"
echo "  skills:        $(ls -1 "$ALL_DIR/skills" | wc -l | tr -d ' ') items"
echo "  agents:        $(ls -1 "$ALL_DIR/agents" | wc -l | tr -d ' ') items"
echo "  hooks:         $(ls -1 "$ALL_DIR/hooks" | wc -l | tr -d ' ') items"
echo "  skills-nested: $(ls -1 "$ALL_DIR/skills-nested" | wc -l | tr -d ' ') items"
echo "  skills-flat:   $(ls -1 "$ALL_DIR/skills-flat" | wc -l | tr -d ' ') items"
