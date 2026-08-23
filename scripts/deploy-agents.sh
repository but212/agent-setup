#!/usr/bin/env sh
# deploy-agents.sh — upload AGENTS.md and skills/ to the shared agent folder (~/.agents).
#
# Usage:
#   scripts/deploy-agents.sh          # copy AGENTS.md + skills/ into ~/.agents
#   scripts/deploy-agents.sh --link   # also symlink ~/.pi/agent/AGENTS.md -> ~/.agents/AGENTS.md (pi global instructions)
#
# Source of truth is this repository. ~/.agents is a deployment target.
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGET=${AGENT_HOME:-"$HOME/.agents"}

case "$TARGET" in
"/" | "$HOME")
  echo "refusing unsafe AGENT_HOME: $TARGET" >&2
  exit 1
  ;;
esac

LINK_PI=0
for arg in "$@"; do
  case $arg in
  --link) LINK_PI=1 ;;
  *)
    echo "unknown option: $arg" >&2
    exit 2
    ;;
  esac
done

[ -f "$REPO_ROOT/AGENTS.md" ] || {
  echo "AGENTS.md not found in $REPO_ROOT" >&2
  exit 1
}
[ -d "$REPO_ROOT/skills" ] || {
  echo "skills/ not found in $REPO_ROOT" >&2
  exit 1
}

mkdir -p "$TARGET"

cp "$REPO_ROOT/AGENTS.md" "$TARGET/AGENTS.md"
echo "copied: AGENTS.md -> $TARGET/AGENTS.md"

# Mirror skills/: rsync --delete removes stale copies inside <target>/skills only.
mkdir -p "$TARGET/skills"
rsync -a --delete "$REPO_ROOT/skills/" "$TARGET/skills/"
echo "mirrored: skills/ -> $TARGET/skills ($(find "$TARGET/skills" -name SKILL.md | wc -l) skills)"

if [ "$LINK_PI" -eq 1 ]; then
  PI_DIR="$HOME/.pi/agent"
  mkdir -p "$PI_DIR"
  if [ -e "$PI_DIR/AGENTS.md" ] && [ ! -L "$PI_DIR/AGENTS.md" ]; then
    echo "refusing to overwrite real file $PI_DIR/AGENTS.md (not a symlink)" >&2
    exit 1
  fi
  ln -sfn "$TARGET/AGENTS.md" "$PI_DIR/AGENTS.md"
  echo "linked: $PI_DIR/AGENTS.md -> $TARGET/AGENTS.md"
fi

echo "done."
