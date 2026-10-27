#!/usr/bin/env python3
"""Mirror AGENTS.md and skills/ into shared agent directory (~/.agents)."""

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class DeploymentSafetyError(Exception):
    """Raised when a pre-flight deployment safety invariant is violated."""


def validate_deployment_safety(repo_root: Path, target_arg: str | None) -> Path:
    home_env = os.environ.get("HOME")
    home_dir = Path(home_env).resolve() if home_env else Path.home().resolve()

    target_input = target_arg or os.environ.get("AGENT_HOME")
    if not target_input:
        target_path = home_dir / ".agents"
    else:
        target_path = Path(target_input)
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path

    # Canonicalize existing ancestor if target does not yet exist
    curr = target_path
    parts: list[str] = []
    while not curr.exists():
        parts.insert(0, curr.name)
        parent = curr.parent
        if parent == curr:
            break
        curr = parent
    canonical_target = curr.resolve()
    for part in parts:
        canonical_target = canonical_target / part

    is_root = canonical_target == canonical_target.parent or (
        bool(canonical_target.anchor)
        and canonical_target == Path(canonical_target.anchor)
    )
    canonical_repo = repo_root.resolve()
    is_in_repo = (
        canonical_target == canonical_repo or canonical_repo in canonical_target.parents
    )
    if is_root or canonical_target == home_dir or is_in_repo:
        raise DeploymentSafetyError(f"refusing unsafe AGENT_HOME: {target_input}\n")

    agents_source = repo_root / "AGENTS.md"
    skills_source = repo_root / "skills"
    if not agents_source.is_file():
        raise DeploymentSafetyError(f"AGENTS.md not found in {repo_root}\n")
    if not skills_source.is_dir():
        raise DeploymentSafetyError(f"skills/ not found in {repo_root}\n")

    target_agents = canonical_target / "AGENTS.md"
    if target_agents.exists() and not target_agents.is_file():
        raise DeploymentSafetyError(
            f"destination is not a regular file: {target_agents}\n"
        )

    target_skills = canonical_target / "skills"
    if target_skills.exists() and not target_skills.is_dir():
        raise DeploymentSafetyError(
            f"destination is not a directory: {target_skills}\n"
        )

    return canonical_target


def sync_skills(skills_source: Path, target_skills: Path) -> int:
    source_items = {
        item.relative_to(skills_source): item for item in skills_source.rglob("*")
    }

    if target_skills.exists():
        target_items = sorted(
            target_skills.rglob("*"), key=lambda p: len(p.parts), reverse=True
        )
        for item in target_items:
            if not item.exists():
                continue
            rel = item.relative_to(target_skills)
            src = source_items.get(rel)
            type_mismatch = src is not None and (src.is_dir() != item.is_dir())
            if src is None or type_mismatch:
                if item.is_file():
                    item.unlink(missing_ok=True)
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)

    target_skills.mkdir(parents=True, exist_ok=True)
    for rel, src in source_items.items():
        dst = target_skills / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    return sum(1 for p in skills_source.rglob("SKILL.md") if p.is_file())


def deploy(repo_root: Path, target_arg: str | None) -> int:
    try:
        canonical_target = validate_deployment_safety(repo_root, target_arg)
        canonical_target.mkdir(parents=True, exist_ok=True)

        target_agents = canonical_target / "AGENTS.md"
        shutil.copy2(repo_root / "AGENTS.md", target_agents)
        print(f"copied: AGENTS.md -> {target_agents}")

        target_skills = canonical_target / "skills"
        skill_count = sync_skills(repo_root / "skills", target_skills)
        print(f"mirrored: skills/ -> {target_skills} ({skill_count} skills)")
        print("done.")
        return 0
    except DeploymentSafetyError as exc:
        sys.stderr.write(str(exc))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mirror AGENTS.md and skills/ into shared agent folder."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Optional explicit destination path (overrides AGENT_HOME)",
    )
    args = parser.parse_args()
    return deploy(REPO_ROOT, args.target)


if __name__ == "__main__":
    sys.exit(main())
