#!/usr/bin/env python3
"""Mirror AGENTS.md and skills/ into shared agent directory (~/.agents)."""

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def has_symlink_or_reparse_in_chain(path: Path, stop_at: Path | None = None) -> bool:
    curr = path if path.is_absolute() else Path.cwd() / path
    stop = stop_at.resolve() if stop_at else None
    while True:
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


def deploy(repo_root: Path, target_arg: str | None, link: bool) -> int:
    home_env = os.environ.get("HOME")
    home_dir = Path(home_env).resolve() if home_env else Path.home().resolve()

    target_input_str = target_arg or os.environ.get("AGENT_HOME")
    if not target_input_str:
        target_path = home_dir / ".agents"
        target_input_str = str(target_path)
        stop_at = home_dir
    else:
        target_path = Path(target_input_str)
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path
            stop_at = Path.cwd().resolve()
        else:
            stop_at = None

    if has_symlink_or_reparse_in_chain(target_path, stop_at=stop_at):
        sys.stderr.write(f"refusing symlinked AGENT_HOME: {target_input_str}\n")
        return 1

    try:
        canonical_target = get_canonical(target_path)
    except Exception as exc:
        sys.stderr.write(f"cannot resolve AGENT_HOME: {exc}\n")
        return 1

    # Check root or home target
    is_root = canonical_target == canonical_target.parent or (
        canonical_target.anchor and canonical_target == Path(canonical_target.anchor)
    )
    if is_root or canonical_target == home_dir:
        sys.stderr.write(f"refusing unsafe AGENT_HOME: {target_input_str}\n")
        return 1

    agents_source = repo_root / "AGENTS.md"
    skills_source = repo_root / "skills"
    if not agents_source.is_file():
        sys.stderr.write(f"AGENTS.md not found in {repo_root}\n")
        return 1
    if not skills_source.is_dir():
        sys.stderr.write(f"skills/ not found in {repo_root}\n")
        return 1

    target_agents = canonical_target / "AGENTS.md"
    if is_symlink_or_reparse(target_agents):
        sys.stderr.write(f"refusing symlinked destination: {target_agents}\n")
        return 1
    if target_agents.exists() and not target_agents.is_file():
        sys.stderr.write(f"destination is not a regular file: {target_agents}\n")
        return 1

    target_skills = canonical_target / "skills"
    if is_symlink_or_reparse(target_skills):
        sys.stderr.write(f"refusing symlinked destination: {target_skills}\n")
        return 1
    if target_skills.exists() and not target_skills.is_dir():
        sys.stderr.write(f"destination is not a directory: {target_skills}\n")
        return 1

    pi_dir = home_dir / ".pi" / "agent"
    pi_agents = pi_dir / "AGENTS.md"
    if link:
        if has_symlink_or_reparse_in_chain(pi_dir, stop_at=home_dir):
            sys.stderr.write(
                f"refusing symlinked destination: {pi_dir} (symlinked pi agent directory: {pi_dir})\n"
            )
            return 1
        if pi_dir.exists() and not pi_dir.is_dir():
            sys.stderr.write(f"destination is not a directory: {pi_dir}\n")
            return 1
        if pi_agents.exists() and not is_symlink_or_reparse(pi_agents):
            sys.stderr.write(
                f"refusing to overwrite real file {pi_agents} (not a symlink)\n"
            )
            return 1

    canonical_target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(agents_source, target_agents)
    print(f"copied: AGENTS.md -> {target_agents}")

    target_skills.mkdir(parents=True, exist_ok=True)
    source_items: dict[Path, Path] = {}
    for item in skills_source.rglob("*"):
        source_items[item.relative_to(skills_source)] = item

    # Remove stale files inside target_skills bottom-up
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
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    for rel, src in source_items.items():
        dst = target_skills / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    skill_count = sum(1 for p in target_skills.rglob("SKILL.md") if p.is_file())
    print(f"mirrored: skills/ -> {target_skills} ({skill_count} skills)")

    if link:
        pi_dir.mkdir(parents=True, exist_ok=True)
        if is_symlink_or_reparse(pi_agents):
            pi_agents.unlink()
        target_agents_abs = target_agents.resolve()
        pi_agents.symlink_to(target_agents_abs)
        print(f"linked: {pi_agents} -> {target_agents_abs}")

    print("done.")
    return 0


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
