#!/usr/bin/env sh
# deploy-agents.sh — upload AGENTS.md and skills/ to the shared agent folder (~/.agents).
#
# Usage:
#   scripts/deploy-agents.sh          # copy AGENTS.md + skills/ into ~/.agents
#   scripts/deploy-agents.sh --link   # also symlink ~/.pi/agent/AGENTS.md -> ~/.agents/AGENTS.md (pi global instructions)
#
# Source of truth is this repository. ~/.agents is a deployment target.
set -eu

REPO_ROOT=$(CDPATH= cd -P -- "$(dirname -- "$0")/.." && pwd)
TARGET_INPUT=${AGENT_HOME:-"$HOME/.agents"}

# Resolve the target before writing. This catches aliases such as $HOME/. and
# keeps --link targets absolute even when AGENT_HOME is relative.
case "$TARGET_INPUT" in
/*) TARGET_PATH=$TARGET_INPUT ;;
*) TARGET_PATH=$PWD/$TARGET_INPUT ;;
esac
if [ -L "$TARGET_PATH" ]; then
  echo "refusing symlinked AGENT_HOME: $TARGET_INPUT" >&2
  exit 1
fi
if [ -e "$TARGET_PATH" ]; then
  TARGET=$(CDPATH= cd -P -- "$TARGET_PATH" && pwd) || {
    echo "cannot resolve AGENT_HOME: $TARGET_INPUT" >&2
    exit 1
  }
else
  TARGET_PARENT=$(CDPATH= cd -P -- "$(dirname -- "$TARGET_PATH")" && pwd) || {
    echo "cannot resolve AGENT_HOME parent: $TARGET_INPUT" >&2
    exit 1
  }
  TARGET=$TARGET_PARENT/$(basename -- "$TARGET_PATH")
fi
HOME_REAL=$(CDPATH= cd -P -- "$HOME" && pwd)
case "$TARGET" in
"/" | "$HOME_REAL")
  echo "refusing unsafe AGENT_HOME: $TARGET_INPUT" >&2
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

if [ -L "$TARGET/AGENTS.md" ]; then
  echo "refusing symlinked destination: $TARGET/AGENTS.md" >&2
  exit 1
fi
if [ -L "$TARGET/skills" ]; then
  echo "refusing symlinked destination: $TARGET/skills" >&2
  exit 1
fi
if [ -e "$TARGET/skills" ] && [ ! -d "$TARGET/skills" ]; then
  echo "destination is not a directory: $TARGET/skills" >&2
  exit 1
fi
if [ "$LINK_PI" -eq 1 ]; then
  PI_DIR="$HOME/.pi/agent"
  if [ -L "$PI_DIR" ]; then
    echo "refusing symlinked pi agent directory: $PI_DIR" >&2
    exit 1
  fi
  if [ -e "$PI_DIR/AGENTS.md" ] && [ ! -L "$PI_DIR/AGENTS.md" ]; then
    echo "refusing to overwrite real file $PI_DIR/AGENTS.md (not a symlink)" >&2
    exit 1
  fi
fi

mkdir -p "$TARGET"
cp "$REPO_ROOT/AGENTS.md" "$TARGET/AGENTS.md"
echo "copied: AGENTS.md -> $TARGET/AGENTS.md"

# Mirror skills/: rsync --delete removes stale copies inside <target>/skills only.
mkdir -p "$TARGET/skills"
rsync -a --delete "$REPO_ROOT/skills/" "$TARGET/skills/"
echo "mirrored: skills/ -> $TARGET/skills ($(find "$TARGET/skills" -name SKILL.md | wc -l) skills)"

if [ "$LINK_PI" -eq 1 ]; then
  mkdir -p "$PI_DIR"
  ln -sfn "$TARGET/AGENTS.md" "$PI_DIR/AGENTS.md"
  echo "linked: $PI_DIR/AGENTS.md -> $TARGET/AGENTS.md"
fi

echo "done."
