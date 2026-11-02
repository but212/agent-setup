import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class DeployAgentsTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="agent-setup-deploy-")
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "skills" / "example").mkdir(parents=True)
        shutil.copy2(
            ROOT / "scripts" / "deploy_agents.py",
            self.repo / "scripts" / "deploy_agents.py",
        )
        shutil.copy2(ROOT / "AGENTS.md", self.repo / "AGENTS.md")
        (self.repo / "skills" / "example" / "SKILL.md").write_text(
            "example\n", encoding="utf-8"
        )
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def run_deploy(self, target, *, cwd=None):
        environment = os.environ.copy()
        environment.update({"AGENT_HOME": str(target), "HOME": str(self.home)})
        command = [
            sys.executable,
            str(self.repo / "scripts" / "deploy_agents.py"),
        ]
        return subprocess.run(
            command,
            cwd=cwd or self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def run_tool(self, *args, agent_home=None):
        environment = os.environ.copy()
        environment.pop("AGENT_HOME", None)
        environment["HOME"] = str(self.home)
        if agent_home is not None:
            environment["AGENT_HOME"] = str(agent_home)
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts" / "deploy_agents.py"), *args],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_default_tool_deploys_to_home_agents(self):
        result = self.run_tool()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / ".agents" / "AGENTS.md").is_file())
        self.assertTrue(
            (self.home / ".agents" / "skills" / "example" / "SKILL.md").is_file()
        )

    def test_claude_tool_deploys_skills_only_and_keeps_claude_md(self):
        claude_md = self.home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir()
        claude_md.write_text("user rules\n", encoding="utf-8")

        result = self.run_tool("--tool", "claude")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(
            (self.home / ".claude" / "skills" / "example" / "SKILL.md").is_file()
        )
        self.assertEqual(claude_md.read_text(encoding="utf-8"), "user rules\n")
        self.assertFalse((self.home / ".claude" / "AGENTS.md").exists())
        self.assertFalse((self.home / ".claude" / ".deploy.lock").exists())

    def test_antigravity_tool_deploys_skills_only_and_keeps_gemini_md(self):
        gemini_md = self.home / ".gemini" / "GEMINI.md"
        gemini_md.parent.mkdir()
        gemini_md.write_text("user rules\n", encoding="utf-8")

        result = self.run_tool("--tool", "antigravity")

        self.assertEqual(result.returncode, 0, result.stderr)
        root = self.home / ".gemini" / "config"
        self.assertTrue((root / "skills" / "example" / "SKILL.md").is_file())
        self.assertFalse((root / "AGENTS.md").exists())
        self.assertEqual(gemini_md.read_text(encoding="utf-8"), "user rules\n")

    def test_claude_tool_preserves_foreign_skills(self):
        foreign = self.home / ".claude" / "skills" / "synced"
        foreign.mkdir(parents=True)
        (foreign / "SKILL.md").write_text("foreign\n", encoding="utf-8")

        result = self.run_tool("--tool", "claude")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (foreign / "SKILL.md").read_text(encoding="utf-8"), "foreign\n"
        )

    def test_agent_home_is_ignored_for_non_agents_tool(self):
        other = self.root / "other"

        result = self.run_tool("--tool", "claude", agent_home=other)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(other.exists())
        self.assertTrue(
            (self.home / ".claude" / "skills" / "example" / "SKILL.md").is_file()
        )

    def test_positional_target_with_non_agents_tool_is_usage_error(self):
        result = self.run_tool("--tool", "claude", str(self.root / "other"))

        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "other").exists())
        self.assertFalse((self.home / ".claude").exists())

    def test_unknown_tool_is_usage_error(self):
        result = self.run_tool("--tool", "bogus")

        self.assertEqual(result.returncode, 2)

    def test_plan_for_skills_only_tool_has_no_agents_paths(self):
        from unittest.mock import patch

        from scripts.deploy_agents import Tool, create_deployment_plan

        with patch.dict(os.environ, {"HOME": str(self.home)}):
            plan = create_deployment_plan(self.repo, None, Tool.CLAUDE)

        self.assertIsNone(plan.agents)
        self.assertEqual(plan.canonical_target, (self.home / ".claude").resolve())
        self.assertEqual(plan.target_skills, plan.canonical_target / "skills")

    def test_plan_for_agents_tool_pairs_source_and_target(self):
        from scripts.deploy_agents import create_deployment_plan

        target = self.root / "paired_target"
        plan = create_deployment_plan(self.repo, str(target))

        self.assertEqual(plan.agents.source, self.repo / "AGENTS.md")
        self.assertEqual(plan.agents.target, target.resolve() / "AGENTS.md")

    def test_unsafe_skills_only_destination_message_names_path_not_none(self):
        environment = os.environ.copy()
        environment.pop("AGENT_HOME", None)
        environment["HOME"] = str(self.repo)

        result = subprocess.run(
            [
                sys.executable,
                str(self.repo / "scripts" / "deploy_agents.py"),
                "--tool",
                "claude",
            ],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("None", result.stderr)
        self.assertIn(str((self.repo / ".claude").resolve()), result.stderr)
        self.assertFalse((self.repo / ".claude").exists())

    def test_skills_only_tool_does_not_require_agents_md_in_repo(self):
        from unittest.mock import patch

        from scripts.deploy_agents import Tool, create_deployment_plan

        (self.repo / "AGENTS.md").unlink()
        with patch.dict(os.environ, {"HOME": str(self.home)}):
            plan = create_deployment_plan(self.repo, None, Tool.ANTIGRAVITY)

        self.assertEqual(
            plan.canonical_target, (self.home / ".gemini" / "config").resolve()
        )

    def test_skills_only_failure_preserves_original_skills(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            Tool,
            create_deployment_plan,
        )

        original = self.home / ".claude" / "skills" / "example"
        original.mkdir(parents=True)
        (original / "SKILL.md").write_text("original\n", encoding="utf-8")
        with patch.dict(os.environ, {"HOME": str(self.home)}):
            plan = create_deployment_plan(self.repo, None, Tool.CLAUDE)

        orig_replace = os.replace

        def fail_on_skills_swap(src, dst):
            if str(src).endswith(".skills.tmp"):
                raise OSError("Simulated swap failure")
            return orig_replace(src, dst)

        with (
            patch("os.replace", side_effect=fail_on_skills_swap),
            self.assertRaises(OSError),
            DeploymentTransaction(plan) as tx,
        ):
            tx.commit()

        self.assertEqual(
            (original / "SKILL.md").read_text(encoding="utf-8"), "original\n"
        )
        self.assertEqual([p.name for p in plan.canonical_target.glob(".*")], [])

    def test_deploy_rejects_resolved_home_alias_before_write(self):
        result = self.run_deploy(self.home / ".")

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_deploy_rejects_agents_directory_before_write(self):
        target = self.root / "target"
        target.mkdir()
        (target / "AGENTS.md").mkdir()

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((target / "AGENTS.md" / "AGENTS.md").exists())

    def test_deploy_replaces_owned_skill_and_cleans_stale_inside_it(self):
        target = self.root / "target"
        (target / "skills" / "example").mkdir(parents=True)
        stale = target / "skills" / "example" / "stale.txt"
        stale.write_text("stale", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stale.exists())
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())
        self.assertEqual(
            (target / "AGENTS.md").read_text(encoding="utf-8"),
            (self.repo / "AGENTS.md").read_text(encoding="utf-8"),
        )

    def test_deploy_preserves_foreign_skill_entries(self):
        target = self.root / "target"
        foreign_dir = target / "skills" / "foreign"
        foreign_dir.mkdir(parents=True)
        (foreign_dir / "SKILL.md").write_text("foreign\n", encoding="utf-8")
        foreign_file = target / "skills" / "note.txt"
        foreign_file.write_text("keep", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            (foreign_dir / "SKILL.md").read_text(encoding="utf-8"), "foreign\n"
        )
        self.assertEqual(foreign_file.read_text(encoding="utf-8"), "keep")
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())

    def test_deploy_reconciles_conflicting_node_types(self):
        target = self.root / "target"
        (target / "skills").mkdir(parents=True)
        # Create a regular file where 'example' directory should be
        conflicting_file = target / "skills" / "example"
        conflicting_file.write_text("conflict", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())
        self.assertEqual(
            (target / "skills" / "example" / "SKILL.md").read_text(encoding="utf-8"),
            "example\n",
        )

    def test_safe_target_is_mirrored_without_external_deletion(self):
        target = self.root / "target"
        (target / "skills" / "example").mkdir(parents=True)
        stale = target / "skills" / "example" / "stale.txt"
        stale.write_text("stale", encoding="utf-8")

        external_dir = self.root / "external"
        external_dir.mkdir(parents=True)
        sentinel = external_dir / "keep.txt"
        sentinel.write_text("keep-me", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stale.exists())
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())
        self.assertEqual(
            (target / "AGENTS.md").read_text(encoding="utf-8"),
            (self.repo / "AGENTS.md").read_text(encoding="utf-8"),
        )
        self.assertTrue(sentinel.exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep-me")

    def test_deploy_rejects_target_inside_repo_root(self):
        result = self.run_deploy(self.repo)
        self.assertEqual(result.returncode, 1)

        nested_target = self.repo / "nested"
        result_nested = self.run_deploy(nested_target)
        self.assertEqual(result_nested.returncode, 1)

    def test_deploy_fails_when_lock_held(self):
        target = self.root / "target"
        target.mkdir(parents=True)
        lock_file = target / ".deploy.lock"
        lock_file.write_text("99999\n", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("99999", result.stderr)
        self.assertIn(str(lock_file), result.stderr)

    def test_deploy_lock_held_with_unreadable_pid_reports_unknown(self):
        target = self.root / "target"
        target.mkdir(parents=True)
        (target / ".deploy.lock").write_bytes(b"\xff\xfe not a pid")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown", result.stderr)

    def test_deploy_removes_stale_scratch_from_prior_run(self):
        target = self.root / "target"
        (target / ".skills.tmp" / "junk").mkdir(parents=True)
        (target / ".skills.bak").mkdir()
        (target / ".AGENTS.md.tmp").write_text("stale", encoding="utf-8")
        (target / ".AGENTS.md.bak").write_text("stale", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([p.name for p in target.glob(".*")], [])
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())

    def test_deploy_rejects_filesystem_root(self):
        # Rejected by the combined guard; is_root is not isolated here because
        # the home-ancestor check also covers the root when HOME is under it.
        from scripts.deploy_agents import DeploymentSafetyError, create_deployment_plan

        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(self.repo, Path(self.root.anchor).as_posix())

    def test_deploy_releases_lock_on_success(self):
        target = self.root / "target"
        result = self.run_deploy(target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((target / ".deploy.lock").exists())

    def test_deploy_failure_preserves_original_targets(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "target"
        target.mkdir(parents=True)
        original_agents = target / "AGENTS.md"
        original_agents.write_text("original agents\n", encoding="utf-8")
        target_skills = target / "skills"
        (target_skills / "example").mkdir(parents=True)
        original_skill = target_skills / "example" / "SKILL.md"
        original_skill.write_text("original content\n", encoding="utf-8")

        plan = create_deployment_plan(self.repo, str(target))

        with (
            patch("shutil.copytree", side_effect=OSError("Simulated disk full")),
            self.assertRaises(OSError),
            DeploymentTransaction(plan) as tx,
        ):
            tx.commit()

        self.assertTrue(original_agents.exists())
        self.assertEqual(
            original_agents.read_text(encoding="utf-8"), "original agents\n"
        )
        self.assertTrue(original_skill.exists())
        self.assertEqual(
            original_skill.read_text(encoding="utf-8"), "original content\n"
        )
        staging_files = [p.name for p in target.glob(".*")]
        self.assertEqual(staging_files, [])

    def test_deployment_transaction_rollback_cleans_new_target_on_failure(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "new_target"
        plan = create_deployment_plan(self.repo, str(target))

        orig_replace = os.replace

        def fail_on_skills_swap(src, dst):
            if "skills" in str(dst) and not str(src).endswith(".bak"):
                raise OSError("Simulated swap failure")
            return orig_replace(src, dst)

        with (
            patch("os.replace", side_effect=fail_on_skills_swap),
            self.assertRaises(OSError),
            DeploymentTransaction(plan) as tx,
        ):
            tx.commit()

        self.assertFalse(plan.agents.target.exists())
        self.assertFalse(plan.target_skills.exists())
        staging_files = [p.name for p in target.glob(".*")]
        self.assertEqual(staging_files, [])

    def test_create_deployment_plan_returns_valid_plan(self):
        from scripts.deploy_agents import create_deployment_plan

        target = self.root / "valid_plan_target"
        plan = create_deployment_plan(self.repo, str(target))
        self.assertEqual(plan.canonical_target, target.resolve())
        self.assertEqual(plan.agents.target, target.resolve() / "AGENTS.md")
        self.assertEqual(plan.target_skills, target.resolve() / "skills")
        self.assertEqual(plan.lock_path, target.resolve() / ".deploy.lock")

    def test_deployment_transaction_commit_and_rollback(self):
        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "tx_target"
        plan = create_deployment_plan(self.repo, str(target))

        with DeploymentTransaction(plan) as tx:
            target_agents, count = tx.commit()
            self.assertEqual(count, 1)
            self.assertTrue(target_agents.is_file())
            self.assertTrue((plan.target_skills / "example" / "SKILL.md").is_file())

        self.assertFalse(plan.lock_path.exists())

    def test_deploy_failure_during_backup_does_not_corrupt_target_agents(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "target"
        target.mkdir(parents=True)
        original_agents = target / "AGENTS.md"
        original_agents.write_text("original agents\n", encoding="utf-8")

        plan = create_deployment_plan(self.repo, str(target))

        orig_copy2 = shutil.copy2

        def corrupt_copy2(src, dst):
            if str(dst).endswith(".bak"):
                Path(dst).write_text("", encoding="utf-8")
                raise OSError("Simulated disk full during backup")
            return orig_copy2(src, dst)

        with (
            patch("shutil.copy2", side_effect=corrupt_copy2),
            self.assertRaises(OSError),
            DeploymentTransaction(plan) as tx,
        ):
            tx.commit()

        self.assertTrue(original_agents.exists())
        self.assertEqual(
            original_agents.read_text(encoding="utf-8"), "original agents\n"
        )

    def test_create_deployment_plan_rejects_target_that_is_regular_file(self):
        from scripts.deploy_agents import (
            DeploymentSafetyError,
            create_deployment_plan,
        )

        target = self.root / "target_file.txt"
        target.write_text("not a directory\n", encoding="utf-8")

        with self.assertRaises(DeploymentSafetyError) as ctx:
            create_deployment_plan(self.repo, str(target))
        self.assertIn("destination is not a directory", str(ctx.exception))

    def test_deploy_rejects_target_that_is_regular_file(self):
        target = self.root / "target_file.txt"
        target.write_text("not a directory\n", encoding="utf-8")

        result = self.run_deploy(target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("destination is not a directory", result.stderr)

    def test_deployment_lock_distinguishes_generic_oserror(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentLock,
            DeploymentSafetyError,
        )

        lock_path = self.root / "lock" / ".deploy.lock"
        lock = DeploymentLock(lock_path)

        with (
            patch("os.open", side_effect=PermissionError("Access denied")),
            self.assertRaises(DeploymentSafetyError) as ctx,
            lock,
        ):
            pass

        self.assertIn("failed to acquire deployment lock", str(ctx.exception))
        self.assertNotIn("deployment lock already held", str(ctx.exception))

    def test_deployment_lock_cleans_orphaned_lockfile_on_write_failure(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentLock,
            DeploymentSafetyError,
        )

        lock_path = self.root / "lock" / ".deploy.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock = DeploymentLock(lock_path)

        with (
            patch("os.fdopen", side_effect=OSError("Disk write failed")),
            self.assertRaises(DeploymentSafetyError),
            lock,
        ):
            pass

        self.assertFalse(lock_path.exists())

    def test_deployment_transaction_releases_lock_if_enter_cleanup_fails(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "tx_enter_fail_target"
        plan = create_deployment_plan(self.repo, str(target))

        with (
            patch.object(
                DeploymentTransaction,
                "_cleanup_scratch",
                side_effect=OSError("Scratch cleanup access denied"),
            ),
            self.assertRaises(OSError),
            DeploymentTransaction(plan),
        ):
            pass

        self.assertFalse(plan.lock_path.exists())

    def test_deployment_transaction_releases_lock_if_exit_cleanup_fails(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "tx_exit_fail_target"
        plan = create_deployment_plan(self.repo, str(target))

        cleanup_calls = 0

        def failing_exit_cleanup(tx_self):
            nonlocal cleanup_calls
            cleanup_calls += 1
            if cleanup_calls > 1:
                raise OSError("Exit cleanup access denied")

        with (
            patch.object(DeploymentTransaction, "_cleanup_scratch", failing_exit_cleanup),
            self.assertRaises(OSError),
            DeploymentTransaction(plan),
        ):
            pass

        self.assertFalse(plan.lock_path.exists())

    def test_cleanup_scratch_suppresses_oserror_on_unlink(self):
        from unittest.mock import patch

        from scripts.deploy_agents import (
            DeploymentTransaction,
            create_deployment_plan,
        )

        target = self.root / "tx_cleanup_oserror_target"
        plan = create_deployment_plan(self.repo, str(target))
        tx = DeploymentTransaction(plan)
        tx.staging_agents.parent.mkdir(parents=True, exist_ok=True)
        tx.staging_agents.write_text("scratch", encoding="utf-8")

        with patch.object(Path, "unlink", side_effect=OSError("Unlink denied")):
            try:
                tx._cleanup_scratch()
            except OSError:
                self.fail("_cleanup_scratch() raised OSError on unlink")

    def test_deploy_rejects_tilde_home_expansion(self):
        result = self.run_deploy("~")
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing unsafe AGENT_HOME", result.stderr)
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_deploy_expands_tilde_subpath(self):
        result = self.run_deploy("~/custom_agents")
        self.assertEqual(result.returncode, 0, result.stderr)
        custom_target = self.home / "custom_agents"
        self.assertTrue((custom_target / "AGENTS.md").exists())
        self.assertTrue((custom_target / "skills" / "example" / "SKILL.md").exists())

    def test_deploy_rejects_target_as_ancestor_of_repo_root(self):
        from scripts.deploy_agents import DeploymentSafetyError, create_deployment_plan

        target = self.root / "parent_target"
        nested_repo = target / "nested" / "repo"
        nested_repo.mkdir(parents=True)
        (nested_repo / "AGENTS.md").write_text("agents", encoding="utf-8")
        (nested_repo / "skills").mkdir()

        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(nested_repo, str(target))

    def test_deploy_rejects_target_as_ancestor_of_home(self):
        from scripts.deploy_agents import DeploymentSafetyError, create_deployment_plan

        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(self.repo, str(self.home.parent))

    def test_deploy_rejects_symlink_or_junction_targets(self):
        from scripts.deploy_agents import DeploymentSafetyError, create_deployment_plan

        target = self.root / "symlink_target"
        real_dir = self.root / "real_dir"
        real_dir.mkdir()

        def make_dir_link(src: Path, dst: Path):
            try:
                os.symlink(str(src), str(dst), target_is_directory=True)
            except (OSError, NotImplementedError):
                import _winapi

                _winapi.CreateJunction(str(src), str(dst))

        # 1. Target directory itself is a link
        make_dir_link(real_dir, target)
        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(self.repo, str(target))

        # 2. target_skills is a link
        target_dir = self.root / "normal_target"
        target_dir.mkdir()
        make_dir_link(real_dir, target_dir / "skills")
        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(self.repo, str(target_dir))

        # 3. Dangling link/junction at target_skills
        dangling_target = self.root / "dangling_target"
        dangling_target.mkdir()
        will_delete = self.root / "will_delete"
        will_delete.mkdir()
        make_dir_link(will_delete, dangling_target / "skills")
        will_delete.rmdir()
        with self.assertRaises(DeploymentSafetyError):
            create_deployment_plan(self.repo, str(dangling_target))


if __name__ == "__main__":
    unittest.main()
