#!/usr/bin/env python3
"""Mirror AGENTS.md and skills/ into shared agent directory (~/.agents)."""

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class ActionKind(Enum):
    MAKE_DIR = "make_dir"
    COPY_FILE = "copy_file"
    PRUNE_FILE = "prune_file"
    PRUNE_DIR = "prune_dir"


class DeploymentSafetyError(Exception):
    """Raised when a pre-flight deployment safety invariant is violated."""



@dataclass(frozen=True)
class MirrorAction:
    kind: ActionKind
    dst: Path
    src: Path | None = None


@dataclass(frozen=True)
class DeploymentTarget:
    canonical_target: Path
    pi_dir: Path | None = None
    pi_agents: Path | None = None


@dataclass(frozen=True)
class DeploymentPlan:
    canonical_target: Path
    agents_source: Path
    target_agents: Path
    skills_source: Path
    target_skills: Path
    mirror_actions: list[MirrorAction]
    skill_count: int
    pi_dir: Path | None = None
    pi_agents: Path | None = None


# ============================================================================
# Read-only Planning: Safety Inspection & Deployment Planning
# ============================================================================


def is_symlink_or_reparse(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        st = os.lstat(path)
        if hasattr(st, "st_file_attributes"):
            FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
            if st.st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT:
                return True
        return False
    except (OSError, FileNotFoundError):
        return False


def is_darwin_system_symlink(path: Path) -> bool:
    return (
        bool(path.anchor)
        and path.parent == Path(path.anchor)
        and path.name.lower() in ("tmp", "var", "etc")
    )


def has_symlink_or_reparse_in_chain(
    path: Path, stop_at: Path | None = None, is_darwin: bool | None = None
) -> bool:
    darwin = (sys.platform == "darwin") if is_darwin is None else is_darwin
    curr = path if (path.is_absolute() or path.anchor) else Path.cwd() / path
    stop = stop_at.resolve() if stop_at else None
    while True:
        if darwin and is_darwin_system_symlink(curr):
            break
        if is_symlink_or_reparse(curr):
            return True
        if stop and (curr == stop_at or (curr.exists() and curr.resolve() == stop)):
            break
        parent = curr.parent
        if parent == curr:
            break
        curr = parent
    return False


def get_canonical(path: Path) -> Path:
    raw = path if path.is_absolute() else Path.cwd() / path
    curr = raw
    parts: list[str] = []
    while not curr.exists():
        parts.insert(0, curr.name)
        parent = curr.parent
        if parent == curr:
            break
        curr = parent
    canonical = curr.resolve()
    for part in parts:
        canonical = canonical / part
    return canonical


def validate_deployment_safety(
    repo_root: Path, target_arg: str | None, link: bool
) -> DeploymentTarget:
    home_env = os.environ.get("HOME")
    home_dir = Path(home_env).resolve() if home_env else Path.home().resolve()

    target_input_str = target_arg or os.environ.get("AGENT_HOME")
    if not target_input_str:
        target_path = home_dir / ".agents"
        target_input_str = str(target_path)
        stop_at = home_dir
    else:
        target_path = Path(target_input_str)
        if not (target_path.is_absolute() or target_path.anchor):
            target_path = Path.cwd() / target_path
            stop_at = Path.cwd().resolve()
        else:
            stop_at = None

    if has_symlink_or_reparse_in_chain(target_path, stop_at=stop_at):
        raise DeploymentSafetyError(
            f"refusing symlinked AGENT_HOME: {target_input_str}\n"
        )

    try:
        canonical_target = get_canonical(target_path)
    except (OSError, RuntimeError) as exc:
        raise DeploymentSafetyError(f"cannot resolve AGENT_HOME: {exc}\n")

    is_root = canonical_target == canonical_target.parent or (
        canonical_target.anchor and canonical_target == Path(canonical_target.anchor)
    )
    if is_root or canonical_target == home_dir:
        raise DeploymentSafetyError(f"refusing unsafe AGENT_HOME: {target_input_str}\n")

    agents_source = repo_root / "AGENTS.md"
    skills_source = repo_root / "skills"
    if not agents_source.is_file():
        raise DeploymentSafetyError(f"AGENTS.md not found in {repo_root}\n")
    if not skills_source.is_dir():
        raise DeploymentSafetyError(f"skills/ not found in {repo_root}\n")

    target_agents = canonical_target / "AGENTS.md"
    if is_symlink_or_reparse(target_agents):
        raise DeploymentSafetyError(
            f"refusing symlinked destination: {target_agents}\n"
        )
    if target_agents.exists() and not target_agents.is_file():
        raise DeploymentSafetyError(
            f"destination is not a regular file: {target_agents}\n"
        )

    target_skills = canonical_target / "skills"
    if is_symlink_or_reparse(target_skills):
        raise DeploymentSafetyError(
            f"refusing symlinked destination: {target_skills}\n"
        )
    if target_skills.exists() and not target_skills.is_dir():
        raise DeploymentSafetyError(
            f"destination is not a directory: {target_skills}\n"
        )

    pi_dir = home_dir / ".pi" / "agent"
    pi_agents = pi_dir / "AGENTS.md"
    if link:
        if has_symlink_or_reparse_in_chain(pi_dir, stop_at=home_dir):
            raise DeploymentSafetyError(
                f"refusing symlinked destination: {pi_dir} (symlinked pi agent directory: {pi_dir})\n"
            )
        if pi_dir.exists() and not pi_dir.is_dir():
            raise DeploymentSafetyError(f"destination is not a directory: {pi_dir}\n")
        if pi_agents.exists() and not is_symlink_or_reparse(pi_agents):
            raise DeploymentSafetyError(
                f"refusing to overwrite real file {pi_agents} (not a symlink)\n"
            )

    return DeploymentTarget(
        canonical_target=canonical_target,
        pi_dir=pi_dir if link else None,
        pi_agents=pi_agents if link else None,
    )


def compute_mirror_actions(
    skills_source: Path, target_skills: Path
) -> list[MirrorAction]:
    actions: list[MirrorAction] = []
    source_items: dict[Path, Path] = {}
    for item in skills_source.rglob("*"):
        source_items[item.relative_to(skills_source)] = item

    if target_skills.exists():
        target_items = sorted(
            target_skills.rglob("*"), key=lambda p: len(p.parts), reverse=True
        )
        for item in target_items:
            if not (item.exists() or is_symlink_or_reparse(item)):
                continue
            rel = item.relative_to(target_skills)
            src = source_items.get(rel)
            type_mismatch = src is not None and (
                is_symlink_or_reparse(item)
                or (src.is_dir() != item.is_dir())
                or (src.is_file() != item.is_file())
            )
            if src is None or type_mismatch:
                if is_symlink_or_reparse(item) or item.is_file():
                    actions.append(MirrorAction(kind=ActionKind.PRUNE_FILE, dst=item))
                elif item.is_dir():
                    actions.append(MirrorAction(kind=ActionKind.PRUNE_DIR, dst=item))

    for rel, src in source_items.items():
        dst = target_skills / rel
        if src.is_dir():
            actions.append(MirrorAction(kind=ActionKind.MAKE_DIR, dst=dst, src=src))
        else:
            actions.append(MirrorAction(kind=ActionKind.COPY_FILE, dst=dst, src=src))

    return actions


def plan_deployment(
    repo_root: Path, target_arg: str | None, link: bool
) -> DeploymentPlan:
    target = validate_deployment_safety(repo_root, target_arg, link)
    agents_source = repo_root / "AGENTS.md"
    skills_source = repo_root / "skills"
    target_agents = target.canonical_target / "AGENTS.md"
    target_skills = target.canonical_target / "skills"

    actions = compute_mirror_actions(skills_source, target_skills)
    skill_count = sum(1 for p in skills_source.rglob("SKILL.md") if p.is_file())

    return DeploymentPlan(
        canonical_target=target.canonical_target,
        agents_source=agents_source,
        target_agents=target_agents,
        skills_source=skills_source,
        target_skills=target_skills,
        mirror_actions=actions,
        skill_count=skill_count,
        pi_dir=target.pi_dir,
        pi_agents=target.pi_agents,
    )


# ============================================================================
# Imperative Shell: Filesystem Mutations & CLI Execution
# ============================================================================


def execute_deployment(plan: DeploymentPlan) -> None:
    plan.canonical_target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(plan.agents_source, plan.target_agents)
    print(f"copied: AGENTS.md -> {plan.target_agents}")

    plan.target_skills.mkdir(parents=True, exist_ok=True)

    for action in plan.mirror_actions:
        if action.kind == ActionKind.PRUNE_FILE:
            action.dst.unlink(missing_ok=True)
        elif action.kind == ActionKind.PRUNE_DIR:
            shutil.rmtree(action.dst, ignore_errors=True)
        elif action.kind == ActionKind.MAKE_DIR:
            action.dst.mkdir(parents=True, exist_ok=True)
        elif action.kind == ActionKind.COPY_FILE:
            action.dst.parent.mkdir(parents=True, exist_ok=True)
            if action.src:
                shutil.copy2(action.src, action.dst)

    print(f"mirrored: skills/ -> {plan.target_skills} ({plan.skill_count} skills)")

    if plan.pi_dir and plan.pi_agents:
        plan.pi_dir.mkdir(parents=True, exist_ok=True)
        if is_symlink_or_reparse(plan.pi_agents):
            plan.pi_agents.unlink()
        target_agents_abs = plan.target_agents.resolve()
        plan.pi_agents.symlink_to(target_agents_abs)
        print(f"linked: {plan.pi_agents} -> {target_agents_abs}")

    print("done.")


def deploy(repo_root: Path, target_arg: str | None, link: bool) -> int:
    try:
        plan = plan_deployment(repo_root, target_arg, link)
        execute_deployment(plan)
        return 0
    except DeploymentSafetyError as exc:
        sys.stderr.write(str(exc))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror AGENTS.md and skills/ into shared agent folder."
    )
    parser.add_argument(
        "--link",
        action="store_true",
        help="Also link pi global instructions to target AGENTS.md",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional explicit destination path (overrides AGENT_HOME)",
    )
    args = parser.parse_args()
    return deploy(REPO_ROOT, args.target, args.link)


if __name__ == "__main__":
    sys.exit(main())
