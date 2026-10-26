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
        self.assertIn("Multi-step tasks track execution via an agent plan artifact", agents)
        self.assertIn("Follow test-driven development for logic changes", agents)
        self.assertIn("Resolve integration conflicts by preserving behavior", agents)
        self.assertIn("do not run destructive commands", agents)

    def test_unquoted_reserved_frontmatter_scalar_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            skill.write_text(
                text.replace(
                    'activation: "`/challenge`, assumption review"',
                    "activation: `/challenge`, assumption review",
                    1,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "activation plain value cannot start with reserved character '`'",
            result.stdout,
        )

    def test_block_scalar_description_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            lines = text.splitlines()
            end = lines.index("---", 1)
            new_lines = []
            for line in lines[:end]:
                if line.startswith("description:"):
                    new_lines.append("description: >")
                    new_lines.append("  Line one of description.")
                    break
                new_lines.append(line)
            new_lines.extend(lines[end:])
            skill.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("description block scalar not permitted", result.stdout)

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

    def test_permissive_safety_guard_clause_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            agents = repository / "AGENTS.md"
            text = agents.read_text(encoding="utf-8")
            agents.write_text(
                text.replace(
                    "do not run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, without explicit user request.",
                    "destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf` are allowed unless the user objects.",
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "AGENTS.md missing exact destructive-command guard sentence", result.stdout
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

    def test_spec_status_readme_mismatch_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            readme = repository / "README.md"
            readme_text = readme.read_text(encoding="utf-8").replace(
                "specification is currently `stable`",
                "specification is currently `candidate`",
                1,
            )
            readme.write_text(readme_text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not match", result.stdout)


if __name__ == "__main__":
    unittest.main()
