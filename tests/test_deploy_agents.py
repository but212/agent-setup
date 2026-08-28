import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeployAgentsTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory(prefix="agent-setup-deploy-")
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "skills" / "example").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts" / "deploy-agents.sh", self.repo / "scripts" / "deploy-agents.sh")
        shutil.copy2(ROOT / "AGENTS.md", self.repo / "AGENTS.md")
        (self.repo / "skills" / "example" / "SKILL.md").write_text("example\n", encoding="utf-8")
        self.home = self.root / "home"
        self.home.mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def run_deploy(self, target, *, link=False, cwd=None):
        environment = os.environ.copy()
        environment.update({"AGENT_HOME": str(target), "HOME": str(self.home)})
        command = [str(self.repo / "scripts" / "deploy-agents.sh")]
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

    def test_rejects_resolved_home_alias_before_write(self):
        result = self.run_deploy(self.home / ".")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe AGENT_HOME", result.stderr)
        self.assertFalse((self.home / "AGENTS.md").exists())

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
        self.assertEqual((pi_dir / "AGENTS.md").read_text(encoding="utf-8"), "user-owned")

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


class RepositoryContractTests(unittest.TestCase):
    def test_catalog_validates(self):
        result = subprocess.run(
            ["python3", "scripts/validate-skills.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_catalog_row_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = Path(directory) / "repo"
            shutil.copytree(ROOT, repository, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            specification = repository / "spec" / "skills-spec.md"
            text = specification.read_text(encoding="utf-8")
            row = "| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |"
            self.assertIn(row, text)
            specification.write_text(text.replace(row, row + "\n" + row, 1), encoding="utf-8")

            result = subprocess.run(
                ["python3", "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("catalog skill must appear exactly once: crisp", result.stdout)

    def test_sql_audit_declares_safe_dynamic_analysis(self):
        text = (ROOT / "skills" / "sql-orm-indicator-audit" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Regexes are triage heuristics, not security proofs", text)
        self.assertIn("Never run `EXPLAIN ANALYZE` by default", text)
        self.assertIn("disposable non-production environment", text)
        self.assertIn("Do not execute DDL or DML", text)
        self.assertIn("````markdown", text)
        self.assertEqual(text.count("````"), 2)


if __name__ == "__main__":
    unittest.main()
