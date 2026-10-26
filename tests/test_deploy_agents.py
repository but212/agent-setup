import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def check_symlink_support():
    try:
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src"
            src.mkdir()
            dst = Path(temp) / "dst"
            dst.symlink_to(src, target_is_directory=True)
            return True
    except OSError:
        return False


CAN_SYMLINK = check_symlink_support()


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

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_rejects_symlinked_target_without_touching_target(self):
        victim = self.root / "victim"
        victim.mkdir()
        sentinel = victim / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        target = self.root / "target"
        target.symlink_to(victim, target_is_directory=True)

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked AGENT_HOME", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_rejects_symlinked_ancestor_target_without_touching_victim(self):
        victim = self.root / "victim"
        victim.mkdir()
        sentinel = victim / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        sym_parent = self.root / "sym_parent"
        sym_parent.symlink_to(victim, target_is_directory=True)
        target = sym_parent / "sub"

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked AGENT_HOME", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertFalse((victim / "sub").exists())

    def test_has_symlink_or_reparse_in_chain_detects_ancestor(self):
        from unittest.mock import patch

        from scripts.deploy_agents import has_symlink_or_reparse_in_chain

        sym_parent = self.root / "sym_parent"
        path = sym_parent / "sub" / "target"
        with patch("scripts.deploy_agents.is_symlink_or_reparse") as mock_is_sym:
            mock_is_sym.side_effect = lambda p: p == sym_parent
            self.assertTrue(has_symlink_or_reparse_in_chain(path))

    def test_has_symlink_or_reparse_in_chain_respects_stop_at(self):
        from unittest.mock import patch

        from scripts.deploy_agents import has_symlink_or_reparse_in_chain

        sym_parent = self.root / "sym_parent"
        stop_at = sym_parent / "sub"
        path = stop_at / "target"
        with patch("scripts.deploy_agents.is_symlink_or_reparse") as mock_is_sym:
            mock_is_sym.side_effect = lambda p: p == sym_parent
            self.assertFalse(has_symlink_or_reparse_in_chain(path, stop_at=stop_at))

    def test_has_symlink_or_reparse_in_chain_exempts_darwin_system_symlinks(self):
        from unittest.mock import patch

        from scripts.deploy_agents import has_symlink_or_reparse_in_chain

        path = Path("/tmp/sub/target")
        with patch("scripts.deploy_agents.is_symlink_or_reparse") as mock_is_sym:
            mock_is_sym.side_effect = lambda p: p == Path("/tmp")
            self.assertFalse(has_symlink_or_reparse_in_chain(path, is_darwin=True))
            self.assertTrue(has_symlink_or_reparse_in_chain(path, is_darwin=False))

    def test_has_symlink_or_reparse_in_chain_darwin_still_rejects_sub_symlinks(self):
        from unittest.mock import patch

        from scripts.deploy_agents import has_symlink_or_reparse_in_chain

        path = Path("/tmp/sym_sub/target")
        with patch("scripts.deploy_agents.is_symlink_or_reparse") as mock_is_sym:
            mock_is_sym.side_effect = lambda p: (
                p in (Path("/tmp"), Path("/tmp/sym_sub"))
            )
            self.assertTrue(has_symlink_or_reparse_in_chain(path, is_darwin=True))

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_rejects_symlinked_skills_without_touching_victim(self):
        target = self.root / "target"
        target.mkdir()
        victim = self.root / "victim"
        victim.mkdir()
        sentinel = victim / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        (target / "skills").symlink_to(victim, target_is_directory=True)

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked destination", result.stderr)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")
        self.assertFalse((target / "AGENTS.md").exists())

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_rejects_symlinked_agents_without_touching_victim(self):
        target = self.root / "target"
        target.mkdir()
        victim = self.root / "victim"
        victim.write_text("keep", encoding="utf-8")
        (target / "AGENTS.md").symlink_to(victim)

        result = self.run_deploy(target)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked destination", result.stderr)
        self.assertEqual(victim.read_text(encoding="utf-8"), "keep")

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

    def test_compute_mirror_actions_identifies_stale_and_copied_files(self):
        from scripts.deploy_agents import ActionKind, compute_mirror_actions

        source = self.root / "src_skills"
        target = self.root / "dst_skills"
        (source / "alpha").mkdir(parents=True)
        (source / "alpha" / "SKILL.md").write_text("alpha", encoding="utf-8")
        (target / "beta").mkdir(parents=True)
        (target / "beta" / "stale.md").write_text("stale", encoding="utf-8")

        actions = compute_mirror_actions(source, target)
        action_kinds = [a.kind for a in actions]

        self.assertIn(ActionKind.PRUNE_FILE, action_kinds)
        self.assertIn(ActionKind.PRUNE_DIR, action_kinds)
        self.assertIn(ActionKind.MAKE_DIR, action_kinds)
        self.assertIn(ActionKind.COPY_FILE, action_kinds)

    def test_validate_deployment_safety_returns_typed_target(self):
        from scripts.deploy_agents import DeploymentTarget, validate_deployment_safety

        target = self.root / "valid_target"
        result = validate_deployment_safety(self.repo, str(target))

        self.assertIsInstance(result, DeploymentTarget)
        self.assertEqual(result.canonical_target, target.resolve())

    def test_deploy_rejects_target_inside_repo_root(self):
        result = self.run_deploy(self.repo)
        self.assertEqual(result.returncode, 1)
        self.assertIn("refusing unsafe AGENT_HOME", result.stderr)

        nested_target = self.repo / "nested"
        result_nested = self.run_deploy(nested_target)
        self.assertEqual(result_nested.returncode, 1)
        self.assertIn("refusing unsafe AGENT_HOME", result_nested.stderr)

    def test_mirror_action_enforces_source_invariants(self):
        from scripts.deploy_agents import ActionKind, MirrorAction

        with self.assertRaises(ValueError):
            MirrorAction(kind=ActionKind.COPY_FILE, dst=Path("dst"), src=None)

        with self.assertRaises(ValueError):
            MirrorAction(kind=ActionKind.PRUNE_FILE, dst=Path("dst"), src=Path("src"))

        with self.assertRaises(ValueError):
            MirrorAction(kind=ActionKind.PRUNE_DIR, dst=Path("dst"), src=Path("src"))

        with self.assertRaises(ValueError):
            MirrorAction(kind=ActionKind.MAKE_DIR, dst=Path("dst"), src=Path("src"))


if __name__ == "__main__":
    unittest.main()
