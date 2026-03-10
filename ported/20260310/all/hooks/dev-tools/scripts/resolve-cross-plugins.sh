#!/bin/bash
# resolve-cross-plugins.sh — session_start hook for cross-plugin dependency resolution.
#
# Creates short-name symlinks so sibling plugin references work in the plugin
# cache. In the local monorepo, ../short-name/ resolves naturally to sibling
# directories. In the cache, the extra version subdirectory and org-prefixed
# names break that convention. This script bridges the gap by creating symlinks
# at the plugin-name directory level.
#
# Usage: bash resolve-cross-plugins.sh

# Never block session start — exit cleanly on any error
trap 'exit 0' ERR

# Optional debug logging: set AGENT_ALCHEMY_HOOK_DEBUG=1 to enable
debug() {
  if [ "${AGENT_ALCHEMY_HOOK_DEBUG:-}" = "1" ]; then
    echo "[resolve-cross-plugins] $*" >> "${AGENT_ALCHEMY_HOOK_LOG:-/tmp/agent-alchemy-hooks.log}"
  fi
}

# Determine the plugin root from the script's location
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

[ -z "$PLUGIN_ROOT" ] && exit 0

# Only run in the plugin cache (not local monorepo development)
[[ "$PLUGIN_ROOT" != *"/plugins/cache/"* ]] && { debug "Not in cache, skipping"; exit 0; }

# PLUGIN_ROOT = .../org/full-plugin-name/version
plugin_name_dir=$(dirname "$PLUGIN_ROOT")
org_dir=$(dirname "$plugin_name_dir")
org_name=$(basename "$org_dir")
prefix="${org_name}-"

debug "PLUGIN_ROOT=$PLUGIN_ROOT"
debug "org_dir=$org_dir org_name=$org_name"

# Registry for looking up installed versions
registry="$HOME/.agents/plugins/installed_plugins.json"

for sibling_dir in "$org_dir"/*/; do
  [ ! -d "$sibling_dir" ] && continue
  sibling_name=$(basename "$sibling_dir")

  # Strip org prefix to get short name: "agent-alchemy-claude-tools" -> "claude-tools"
  short_name="${sibling_name#$prefix}"
  [ "$short_name" = "$sibling_name" ] && continue

  target="$plugin_name_dir/$short_name"

  # Skip if a real (non-symlink) directory exists with this name
  [ -d "$target" ] && [ ! -L "$target" ] && continue

  # Resolve version: prefer installed_plugins.json, fall back to sort -V
  install_path=""
  if [ -f "$registry" ] && command -v jq >/dev/null 2>&1; then
    install_path=$(jq -r --arg key "${sibling_name}@${org_name}" \
      '.plugins[$key][0].installPath // empty' "$registry" 2>/dev/null)
  fi

  if [ -z "$install_path" ] || [ ! -d "$install_path" ]; then
    install_path=$(ls -1d "${sibling_dir}"*/ 2>/dev/null | sort -V | tail -1)
    [ -n "$install_path" ] && install_path="${install_path%/}"
  fi

  [ -z "$install_path" ] || [ ! -d "$install_path" ] && continue

  version=$(basename "$install_path")
  ln -sfn "../${sibling_name}/${version}" "$target" 2>/dev/null || true
  debug "Created symlink: $short_name -> ../${sibling_name}/${version}"
done

debug "Done"
exit 0
