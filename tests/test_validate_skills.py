import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clone_repo_to_temp(directory: str) -> Path:
    repository = Path(directory) / "repo"
    shutil.copytree(
        ROOT,
        repository,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache"),
    )
    return repository


class RepositoryContractTests(unittest.TestCase):
    def test_catalog_validates(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate-skills.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_four_skills_registered(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
        expected = ["challenge", "crisp", "lean-design", "lean-review"]
        self.assertEqual(skills, expected)

    def test_skills_modification_authorities(self):
        for name in ["challenge", "lean-design", "lean-review"]:
            skill = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("modification-authority: None", skill)
        crisp = (ROOT / "skills" / "crisp" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("modification-authority: Named files only", crisp)

    def test_agents_contains_absorbed_directives(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(
            "Multi-step tasks track execution via an agent plan artifact", agents
        )
        self.assertIn("Follow test-driven development for logic changes", agents)
        self.assertIn("Resolve integration conflicts by preserving behavior", agents)
        self.assertIn("do not run destructive commands", agents)

    def test_missing_frontmatter_description_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            lines = [
                line
                for line in skill.read_text(encoding="utf-8").splitlines()
                if not line.startswith("description:")
            ]
            skill.write_text("\n".join(lines) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing description", result.stdout)

    def test_non_ascii_markdown_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            readme = repository / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\n\u2028\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-ASCII Markdown content", result.stdout)

    def test_invalid_plan_calendar_date_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            invalid_plan = repository / ".plans" / "2026-99-99" / "test.md"
            invalid_plan.parent.mkdir(parents=True)
            invalid_plan.write_text("# invalid\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid ISO calendar date", result.stdout)

    def test_planned_plan_status_passes(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            plan = repository / ".plans" / "2026-01-01" / "task.md"
            plan.parent.mkdir(parents=True)
            plan.write_text("# Plan: task\n\n- Status: `planned`\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unknown_plan_status_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            plan = repository / ".plans" / "2026-01-01" / "task.md"
            plan.parent.mkdir(parents=True)
            plan.write_text("# Plan: task\n\n- Status: `done`\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown status 'done'", result.stdout)

    def test_readme_documents_complete_validation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate-skills.py", text)
        self.assertIn("python3 -m unittest discover -s tests -v", text)

    def test_lean_review_hands_off_blocking_findings(self):
        skill = (ROOT / "skills" / "lean-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Blocking: Yes", skill)
        self.assertIn("AGENTS.md", skill)

    def test_agents_safety_guard_clause_present(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(
            "do not run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, without explicit user request.",
            agents,
        )

    def test_spec_stable_with_unchecked_gate_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            spec = repository / "spec" / "skills-spec.md"
            spec_text = spec.read_text(encoding="utf-8").replace("- [x]", "- [ ]", 1)
            spec.write_text(spec_text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unchecked quality gate", result.stdout)

    def test_gitattributes_enforces_lf(self):
        gitattributes = ROOT / ".gitattributes"
        self.assertTrue(gitattributes.is_file(), ".gitattributes must exist")
        content = gitattributes.read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", content)

    def test_tracked_text_files_use_lf_line_endings(self):
        suffixes = {".md", ".py", ".sh", ".yml", ".yaml"}
        named_files = {"LICENSE", "NOTICE", ".gitattributes", ".gitignore"}
        crlf_files: list[str] = []
        for path in ROOT.rglob("*"):
            if not path.is_file():
                continue
            rel_parts = path.relative_to(ROOT).parts
            if any(part.startswith((".", "__pycache__")) for part in rel_parts):
                continue
            if (
                path.suffix in suffixes or path.name in named_files
            ) and b"\r\n" in path.read_bytes():
                crlf_files.append(str(path.relative_to(ROOT)))
            self.assertEqual(crlf_files, [], f"Found CRLF in files: {crlf_files}")

    def test_skills_have_no_orphaned_skill_references(self):
        orphaned_patterns = ["spec-drive", "lean-mode", "git-conflict"]
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            content = skill_file.read_text(encoding="utf-8")
            for pattern in orphaned_patterns:
                self.assertNotIn(
                    pattern,
                    content,
                    f"Found orphaned reference '{pattern}' in {skill_file.relative_to(ROOT)}",
                )

    def test_missing_agents_file_reports_error_without_crash(self):
        import importlib

        sys.path.insert(0, str(ROOT / "scripts"))
        validator = importlib.import_module("validate-skills")

        report = validator.validate_repository(
            agents_path=ROOT / "NONEXISTENT_AGENTS.md"
        )
        self.assertFalse(report.is_valid)
        self.assertTrue(any("missing AGENTS.md" in err for err in report.errors))

    def test_missing_skills_dir_reports_error(self):
        import importlib

        sys.path.insert(0, str(ROOT / "scripts"))
        validator = importlib.import_module("validate-skills")

        report = validator.validate_repository(skills_dir=ROOT / "NONEXISTENT_SKILLS")
        self.assertFalse(report.is_valid)
        self.assertTrue(
            any("skills directory not found" in err for err in report.errors)
        )

    def test_skills_subdir_without_skill_md_reports_error(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            orphan_subdir = repository / "skills" / "incomplete-skill"
            orphan_subdir.mkdir(parents=True)

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("incomplete-skill", result.stdout)


if __name__ == "__main__":
    unittest.main()
