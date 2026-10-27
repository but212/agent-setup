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

    def test_deploy_rejects_resolved_home_alias_before_write(self):
        result = self.run_deploy(self.home / ".")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe AGENT_HOME", result.stderr)
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_deploy_rejects_agents_directory_before_write(self):
        target = self.root / "target"
        target.mkdir()
        (target / "AGENTS.md").mkdir()

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("regular file", result.stderr)
        self.assertFalse((target / "AGENTS.md" / "AGENTS.md").exists())

    def test_deploy_mirrors_and_cleans_stale(self):
        target = self.root / "target"
        (target / "skills").mkdir(parents=True)
        stale = target / "skills" / "stale.txt"
        stale.write_text("stale", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stale.exists())
        self.assertTrue((target / "skills" / "example" / "SKILL.md").exists())
        self.assertEqual(
            (target / "AGENTS.md").read_text(encoding="utf-8"),
            (self.repo / "AGENTS.md").read_text(encoding="utf-8"),
        )

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
        (target / "skills").mkdir(parents=True)
        stale = target / "skills" / "stale.txt"
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

    def test_validate_deployment_safety_returns_canonical_target(self):
        from scripts.deploy_agents import validate_deployment_safety

        target = self.root / "valid_target"
        canonical_target = validate_deployment_safety(self.repo, str(target))

        self.assertEqual(canonical_target, target.resolve())

    def test_deploy_rejects_target_inside_repo_root(self):
        result = self.run_deploy(self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing unsafe AGENT_HOME", result.stderr)

        nested_target = self.repo / "nested"
        result_nested = self.run_deploy(nested_target)
        self.assertEqual(result_nested.returncode, 1)
        self.assertIn("refusing unsafe AGENT_HOME", result_nested.stderr)

    def test_deploy_fails_when_lock_held(self):
        target = self.root / "target"
        target.mkdir(parents=True)
        lock_file = target / ".deploy.lock"
        lock_file.write_text("99999\n", encoding="utf-8")

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deployment lock already held", result.stderr)

    def test_deploy_releases_lock_on_success(self):
        target = self.root / "target"
        result = self.run_deploy(target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((target / ".deploy.lock").exists())

    def test_deploy_failure_preserves_original_skills(self):
        from unittest.mock import patch
        from scripts.deploy_agents import sync_skills_atomic

        target = self.root / "target"
        target_skills = target / "skills"
        (target_skills / "example").mkdir(parents=True)
        original_skill = target_skills / "example" / "SKILL.md"
        original_skill.write_text("original content\n", encoding="utf-8")

        source_skills = self.repo / "skills"

        with patch("shutil.copytree", side_effect=IOError("Simulated disk full")):
            with self.assertRaises(IOError):
                sync_skills_atomic(source_skills, target_skills)

        self.assertTrue(original_skill.exists())
        self.assertEqual(
            original_skill.read_text(encoding="utf-8"), "original content\n"
        )
        staging_dirs = list(target.glob(".skills.*"))
        self.assertEqual(staging_dirs, [])

    def test_create_deployment_plan_returns_valid_plan(self):
        from scripts.deploy_agents import create_deployment_plan

        target = self.root / "valid_plan_target"
        plan = create_deployment_plan(self.repo, str(target))
        self.assertEqual(plan.canonical_target, target.resolve())
        self.assertEqual(plan.target_agents, target.resolve() / "AGENTS.md")
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


if __name__ == "__main__":
    unittest.main()
