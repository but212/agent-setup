#!/usr/bin/env python3
"""Mirror AGENTS.md and skills/ into ~/.agents, or skills/ into Claude or Antigravity."""

import argparse
import os
import shutil
import stat
import sys
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class Tool(Enum):
    AGENTS = "agents"
    CLAUDE = "claude"
    ANTIGRAVITY = "antigravity"

    def __str__(self) -> str:
        return self.value


# Destination root relative to home. Only AGENTS deploys AGENTS.md; CLAUDE.md and
# GEMINI.md hold user-owned rules and are never written.
_TOOL_ROOTS = {
    Tool.AGENTS: ".agents",
    Tool.CLAUDE: ".claude",
    Tool.ANTIGRAVITY: ".gemini/config",
}


class DeploymentSafetyError(Exception):
    """Raised when a pre-flight deployment safety invariant is violated."""


def _is_link_or_reparse(path: Path) -> bool:
    """Check if path is a symlink or Windows reparse point (junction)."""
    if path.is_symlink():
        return True
    try:
        st = os.lstat(path)
        attrs = getattr(st, "st_file_attributes", 0)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        return bool(attrs & reparse_flag)
    except OSError:
        return False


@dataclass(frozen=True)
class AgentsFile:
    """AGENTS.md copy pair; present in a plan only for Tool.AGENTS."""

    source: Path
    target: Path


@dataclass(frozen=True)
class DeploymentPlan:
    """Immutable, fully validated deployment execution plan."""

    canonical_target: Path
    agents: AgentsFile | None
    skills_source: Path
    target_skills: Path
    lock_path: Path


def _resolve_target(tool: Tool, target_arg: str | None, home_dir: Path) -> Path:
    """Expand the destination: explicit path (agents only) or the tool's default root."""
    target_input = (
        (target_arg or os.environ.get("AGENT_HOME")) if tool is Tool.AGENTS else None
    )
    if not target_input:
        return home_dir / _TOOL_ROOTS[tool]

    if target_input == "~":
        target_path = home_dir
    elif target_input.startswith((f"~{os.sep}", "~/")):
        target_path = home_dir / target_input[2:]
    else:
        target_path = Path(target_input)
    return target_path if target_path.is_absolute() else Path.cwd() / target_path


def _reject_unsafe_target(
    target_path: Path, canonical_target: Path, repo_root: Path, home_dir: Path, tool: Tool
) -> None:
    """Refuse links, filesystem roots, home (or its ancestors), and the repository tree."""
    _reject_link(target_path)

    canonical_repo = repo_root.resolve()

    is_root = canonical_target == canonical_target.parent
    is_home = canonical_target == home_dir
    is_home_ancestor = canonical_target in home_dir.parents
    is_repo_or_inside = (
        canonical_target == canonical_repo or canonical_repo in canonical_target.parents
    )
    is_repo_ancestor = canonical_target in canonical_repo.parents

    if is_root or is_home or is_home_ancestor or is_repo_or_inside or is_repo_ancestor:
        label = "AGENT_HOME" if tool is Tool.AGENTS else "destination"
        raise DeploymentSafetyError(f"refusing unsafe {label}: {canonical_target}")


def _reject_link(path: Path) -> None:
    if _is_link_or_reparse(path):
        raise DeploymentSafetyError(
            f"destination must not be a symlink or junction: {path}"
        )


def _require_kind(path: Path, *, is_dir: bool) -> None:
    """An existing node must be a directory (is_dir) or a regular file."""
    if path.exists() and not (path.is_dir() if is_dir else path.is_file()):
        kind = "directory" if is_dir else "regular file"
        raise DeploymentSafetyError(f"destination is not a {kind}: {path}")


def _require_slot(path: Path, *, is_dir: bool) -> None:
    _reject_link(path)
    _require_kind(path, is_dir=is_dir)


def create_deployment_plan(
    repo_root: Path, target_arg: str | None, tool: Tool = Tool.AGENTS
) -> DeploymentPlan:
    """Validate environment, parameters, and boundary invariants into an immutable plan.

    An explicit target (argument or AGENT_HOME) applies to Tool.AGENTS only.
    """
    home_env = os.environ.get("HOME")
    home_dir = Path(home_env).resolve() if home_env else Path.home().resolve()

    target_path = _resolve_target(tool, target_arg, home_dir)
    canonical_target = target_path.resolve()

    _reject_unsafe_target(target_path, canonical_target, repo_root, home_dir, tool)
    _require_kind(canonical_target, is_dir=True)

    skills_source = repo_root / "skills"
    if not skills_source.is_dir():
        raise DeploymentSafetyError(f"skills/ not found in {repo_root}")

    agents = None
    if tool is Tool.AGENTS:
        agents_source = repo_root / "AGENTS.md"
        if not agents_source.is_file():
            raise DeploymentSafetyError(f"AGENTS.md not found in {repo_root}")
        target_agents = canonical_target / "AGENTS.md"
        _require_slot(target_agents, is_dir=False)
        agents = AgentsFile(source=agents_source, target=target_agents)

    target_skills = canonical_target / "skills"
    _require_slot(target_skills, is_dir=True)

    return DeploymentPlan(
        canonical_target=canonical_target,
        agents=agents,
        skills_source=skills_source,
        target_skills=target_skills,
        lock_path=canonical_target / ".deploy.lock",
    )


class DeploymentLock:
    """Mutual exclusion lock guard for deployment."""

    def __init__(self, lock_path: Path):
        self.lock_path = lock_path

    def __enter__(self):
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            try:
                holder = self.lock_path.read_text(encoding="utf-8").strip()
            except (OSError, UnicodeDecodeError):
                holder = ""
            if not holder.isdigit():
                holder = "unknown"
            raise DeploymentSafetyError(
                f"deployment lock already held at {self.lock_path} (pid {holder}); "
                "remove it if no deployment is running"
            ) from exc
        except OSError as exc:
            raise DeploymentSafetyError(
                f"failed to acquire deployment lock at {self.lock_path}: {exc}"
            ) from exc

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(f"{os.getpid()}\n")
        except BaseException as exc:
            with suppress(OSError):
                os.close(fd)
            with suppress(OSError):
                self.lock_path.unlink(missing_ok=True)
            if isinstance(exc, OSError):
                raise DeploymentSafetyError(
                    f"failed to acquire deployment lock at {self.lock_path}: {exc}"
                ) from exc
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with suppress(OSError):
            self.lock_path.unlink(missing_ok=True)


class DeploymentTransaction:
    """Encapsulates transactional staging, atomic commit, and rollback for DeploymentPlan."""

    def __init__(self, plan: DeploymentPlan):
        self.plan = plan
        self.target = plan.canonical_target
        self.lock = DeploymentLock(plan.lock_path)

        self.staging_agents = self.target / ".AGENTS.md.tmp"
        self.backup_agents = self.target / ".AGENTS.md.bak"

        self.staging_skills = self.target / ".skills.tmp"
        self.backup_skills = self.target / ".skills.bak"

        # Inverse operations of the target mutations applied so far; empty once committed.
        self._undo: list[Callable[[], None]] = []

    def __enter__(self):
        self.target.mkdir(parents=True, exist_ok=True)
        self.lock.__enter__()
        try:
            self._recover_interrupted()
            self._cleanup_scratch()
        except BaseException:
            self.lock.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                self._rollback()
        finally:
            try:
                self._cleanup_scratch()
            finally:
                self.lock.__exit__(exc_type, exc_val, exc_tb)

    def _recover_interrupted(self):
        """Restore backups orphaned by a run killed mid-swap (target missing, backup present)."""
        if self.backup_skills.is_dir() and not self.plan.target_skills.exists():
            os.replace(self.backup_skills, self.plan.target_skills)
        agents = self.plan.agents
        if (
            agents is not None
            and self.backup_agents.is_file()
            and not agents.target.exists()
        ):
            os.replace(self.backup_agents, agents.target)

    def _cleanup_scratch(self):
        with suppress(OSError):
            self.staging_agents.unlink(missing_ok=True)
        with suppress(OSError):
            self.backup_agents.unlink(missing_ok=True)
        shutil.rmtree(self.staging_skills, ignore_errors=True)
        shutil.rmtree(self.backup_skills, ignore_errors=True)

    def _rollback(self):
        while self._undo:
            with suppress(OSError):
                self._undo.pop()()

    def _stage_foreign_skill_entries(self):
        """Carry over top-level target skills/ entries not owned by the repository."""
        if not self.plan.target_skills.is_dir():
            return
        owned = {p.name for p in self.plan.skills_source.iterdir()}
        for entry in self.plan.target_skills.iterdir():
            if entry.name in owned:
                continue
            destination = self.staging_skills / entry.name
            if entry.is_dir() and not entry.is_symlink():
                shutil.copytree(entry, destination, symlinks=True)
            else:
                shutil.copy2(entry, destination, follow_symlinks=False)

    def commit(self) -> tuple[Path | None, int]:
        """Commit AGENTS.md (when planned) and skills/ atomically in two phases."""
        skill_count = self._stage()
        self._swap()
        self._undo.clear()

        agents = self.plan.agents
        return (agents.target if agents is not None else None), skill_count

    def _stage(self) -> int:
        """Phase 1: build staging copies; targets stay untouched. Returns the skill count."""
        agents = self.plan.agents
        if agents is not None:
            shutil.copy2(agents.source, self.staging_agents)

        shutil.copytree(self.plan.skills_source, self.staging_skills)
        skill_count = sum(
            1 for p in self.staging_skills.rglob("SKILL.md") if p.is_file()
        )
        self._stage_foreign_skill_entries()
        return skill_count

    def _swap(self):
        """Phase 2: move staged content into place, recording an undo for each step."""
        agents = self.plan.agents
        agents_existed = agents is not None and agents.target.exists()
        if agents_existed:
            shutil.copy2(agents.target, self.backup_agents)

        if self.plan.target_skills.exists():
            os.replace(self.plan.target_skills, self.backup_skills)
            self._undo.append(
                lambda: os.replace(self.backup_skills, self.plan.target_skills)
            )

        if agents is not None:
            os.replace(self.staging_agents, agents.target)
            if agents_existed:
                self._undo.append(lambda: os.replace(self.backup_agents, agents.target))
            else:
                self._undo.append(lambda: agents.target.unlink(missing_ok=True))

        os.replace(self.staging_skills, self.plan.target_skills)


def deploy(repo_root: Path, target_arg: str | None, tool: Tool = Tool.AGENTS) -> int:
    try:
        plan = create_deployment_plan(repo_root, target_arg, tool)
        with DeploymentTransaction(plan) as tx:
            target_agents, skill_count = tx.commit()
            if target_agents is not None:
                print(f"copied: AGENTS.md -> {target_agents}")
            print(f"mirrored: skills/ -> {plan.target_skills} ({skill_count} skills)")
            print("done.")
            return 0
    except DeploymentSafetyError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror AGENTS.md and skills/ into the shared agent folder "
        "(default), or skills/ only into Claude or Antigravity."
    )
    parser.add_argument(
        "--tool",
        type=Tool,
        choices=list(Tool),
        default=Tool.AGENTS,
        help="Deployment target (default: agents)",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional explicit destination path (agents only; overrides AGENT_HOME)",
    )
    args = parser.parse_args()
    if args.target is not None and args.tool is not Tool.AGENTS:
        parser.error("explicit target is only valid with --tool agents")
    return deploy(REPO_ROOT, args.target, args.tool)


if __name__ == "__main__":
    sys.exit(main())
