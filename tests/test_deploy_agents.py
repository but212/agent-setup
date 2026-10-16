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

    def run_deploy(self, target, *, link=False, cwd=None):
        environment = os.environ.copy()
        environment.update({"AGENT_HOME": str(target), "HOME": str(self.home)})
        command = [
            sys.executable,
            str(self.repo / "scripts" / "deploy_agents.py"),
        ]
        if link:
            command.append("--link")
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

    def test_rejects_existing_pi_file_before_deployment_write(self):
        target = self.root / "target"
        pi_dir = self.home / ".pi" / "agent"
        pi_dir.mkdir(parents=True)
        (pi_dir / "AGENTS.md").write_text("user-owned", encoding="utf-8")

        result = self.run_deploy(target, link=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite real file", result.stderr)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertEqual(
            (pi_dir / "AGENTS.md").read_text(encoding="utf-8"), "user-owned"
        )

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_rejects_symlinked_pi_directory_before_deployment_write(self):
        target = self.root / "target"
        victim = self.root / "victim"
        victim.mkdir()
        pi_parent = self.home / ".pi"
        pi_parent.mkdir()
        (pi_parent / "agent").symlink_to(victim, target_is_directory=True)

        result = self.run_deploy(target, link=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlinked pi agent directory", result.stderr)
        self.assertFalse((target / "AGENTS.md").exists())

    @unittest.skipUnless(CAN_SYMLINK, "filesystem symlinks not supported/permitted")
    def test_relative_target_creates_absolute_pi_link(self):
        workdir = self.root / "work"
        workdir.mkdir()
        target = Path("deployed")

        result = self.run_deploy(target, link=True, cwd=workdir)

        self.assertEqual(result.returncode, 0, result.stderr)
        link = self.home / ".pi" / "agent" / "AGENTS.md"
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), (workdir / target).resolve() / "AGENTS.md")

    def test_safe_target_is_mirrored_without_external_deletion(self):
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


if __name__ == "__main__":
    unittest.main()
