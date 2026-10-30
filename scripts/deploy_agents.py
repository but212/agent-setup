#!/usr/bin/env python3
"""Mirror AGENTS.md and skills/ into shared agent directory (~/.agents)."""

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class DeploymentSafetyError(Exception):
    """Raised when a pre-flight deployment safety invariant is violated."""


@dataclass(frozen=True)
class DeploymentPlan:
    """Immutable, fully validated deployment execution plan."""

    repo_root: Path
    canonical_target: Path
    agents_source: Path
    skills_source: Path
    target_agents: Path
    target_skills: Path
    lock_path: Path


def create_deployment_plan(repo_root: Path, target_arg: str | None) -> DeploymentPlan:
    """Validate environment, parameters, and boundary invariants into an immutable plan."""
    home_env = os.environ.get("HOME")
    home_dir = Path(home_env).resolve() if home_env else Path.home().resolve()

    target_input = target_arg or os.environ.get("AGENT_HOME")
    if not target_input:
        target_path = home_dir / ".agents"
    else:
        if target_input == "~":
            target_path = home_dir
        elif target_input.startswith((f"~{os.sep}", "~/")):
            target_path = home_dir / target_input[2:]
        else:
            target_path = Path(target_input)
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path

    canonical_target = target_path.resolve()

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

    if canonical_target.exists() and not canonical_target.is_dir():
        raise DeploymentSafetyError(
            f"destination is not a directory: {canonical_target}\n"
        )

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

    lock_path = canonical_target / ".deploy.lock"

    return DeploymentPlan(
        repo_root=repo_root,
        canonical_target=canonical_target,
        agents_source=agents_source,
        skills_source=skills_source,
        target_agents=target_agents,
        target_skills=target_skills,
        lock_path=lock_path,
    )


class DeploymentLock:
    """Mutual exclusion lock guard for deployment."""

    def __init__(self, lock_path: Path):
        self.lock_path = lock_path

    def __enter__(self):
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise DeploymentSafetyError(
                f"deployment lock already held at {self.lock_path}\n"
            ) from exc
        except OSError as exc:
            raise DeploymentSafetyError(
                f"failed to acquire deployment lock at {self.lock_path}: {exc}\n"
            ) from exc

        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(f"{os.getpid()}\n")
        except BaseException as exc:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                self.lock_path.unlink(missing_ok=True)
            except OSError:
                pass
            if isinstance(exc, OSError):
                raise DeploymentSafetyError(
                    f"failed to acquire deployment lock at {self.lock_path}: {exc}\n"
                ) from exc
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass


class DeploymentTransaction:
    """Encapsulates transactional staging, atomic commit, and rollback for DeploymentPlan."""

    def __init__(self, plan: DeploymentPlan):
        self.plan = plan
        self.pid = os.getpid()
        self.target = plan.canonical_target
        self.lock = DeploymentLock(plan.lock_path)

        self.staging_agents = self.target / f".AGENTS.md.tmp.{self.pid}"
        self.backup_agents = self.target / f".AGENTS.md.bak.{self.pid}"

        self.staging_skills = self.target / f".skills.tmp.{self.pid}"
        self.backup_skills = self.target / f".skills.bak.{self.pid}"

        self._phase2_started = False
        self._target_agents_existed = False
        self._target_skills_existed = False
        self._target_agents_swapped = False
        self._target_skills_moved = False
        self._committed = False

    def __enter__(self):
        self.target.mkdir(parents=True, exist_ok=True)
        self.lock.__enter__()
        try:
            self._cleanup_scratch()
        except BaseException:
            self.lock.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None and not self._committed:
                self._rollback()
        finally:
            self._cleanup_scratch()
            self.lock.__exit__(exc_type, exc_val, exc_tb)

    def _cleanup_scratch(self):
        if self.staging_agents.exists():
            self.staging_agents.unlink(missing_ok=True)
        if self.backup_agents.exists():
            self.backup_agents.unlink(missing_ok=True)
        if self.staging_skills.exists():
            shutil.rmtree(self.staging_skills, ignore_errors=True)
        if self.backup_skills.exists():
            shutil.rmtree(self.backup_skills, ignore_errors=True)

    def _rollback(self):
        if not self._phase2_started:
            return

        # 1. Restore or clean AGENTS.md
        if self._target_agents_swapped:
            try:
                os.replace(self.backup_agents, self.plan.target_agents)
            except OSError:
                pass
        elif not self._target_agents_existed and self.plan.target_agents.exists():
            try:
                self.plan.target_agents.unlink(missing_ok=True)
            except OSError:
                pass

        # 2. Restore or clean skills/
        if self._target_skills_moved:
            try:
                if self.plan.target_skills.exists():
                    shutil.rmtree(self.plan.target_skills, ignore_errors=True)
                os.replace(self.backup_skills, self.plan.target_skills)
            except OSError:
                pass
        elif not self._target_skills_existed and self.plan.target_skills.exists():
            try:
                shutil.rmtree(self.plan.target_skills, ignore_errors=True)
            except OSError:
                pass

    def commit(self) -> tuple[Path, int]:
        """Commit AGENTS.md and skills/ atomically in two phases."""
        # Phase 1: Pure staging (targets untouched)
        shutil.copy2(self.plan.agents_source, self.staging_agents)
        shutil.copytree(self.plan.skills_source, self.staging_skills)
        skill_count = sum(
            1 for p in self.staging_skills.rglob("SKILL.md") if p.is_file()
        )

        # Phase 2: Swapping with rollback guards
        self._phase2_started = True
        self._target_agents_existed = self.plan.target_agents.exists()
        self._target_skills_existed = self.plan.target_skills.exists()

        if self._target_agents_existed:
            shutil.copy2(self.plan.target_agents, self.backup_agents)

        if self._target_skills_existed:
            os.replace(self.plan.target_skills, self.backup_skills)
            self._target_skills_moved = True

        os.replace(self.staging_agents, self.plan.target_agents)
        if self._target_agents_existed:
            self._target_agents_swapped = True

        os.replace(self.staging_skills, self.plan.target_skills)

        self._committed = True
        return self.plan.target_agents, skill_count


def deploy(repo_root: Path, target_arg: str | None) -> int:
    try:
        plan = create_deployment_plan(repo_root, target_arg)
        with DeploymentTransaction(plan) as tx:
            target_agents, skill_count = tx.commit()
            print(f"copied: AGENTS.md -> {target_agents}")
            print(f"mirrored: skills/ -> {plan.target_skills} ({skill_count} skills)")
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
