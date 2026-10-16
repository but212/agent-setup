#!/usr/bin/env sh
# deploy-agents.sh — upload AGENTS.md and skills/ to shared agent folder (~/.agents).
#
# Usage:
#   scripts/deploy-agents.sh          # copy AGENTS.md + skills/ into ~/.agents
#   scripts/deploy-agents.sh --link   # also symlink ~/.pi/agent/AGENTS.md -> ~/.agents/AGENTS.md
set -eu

REPO_ROOT=$(CDPATH= cd -P -- "$(dirname -- "$0")/.." && pwd)
PYTHON_CMD="python3"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD="python"
fi

exec "$PYTHON_CMD" "$REPO_ROOT/scripts/deploy_agents.py" "$@"
