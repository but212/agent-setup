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

    def test_exact_nine_skills_registered(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
        expected = [
            "challenge",
            "crisp",
            "crisp-commit",
            "git-conflict",
            "lean-design",
            "lean-mode",
            "lean-review",
            "lean-test",
            "spec-drive",
        ]
        self.assertEqual(skills, expected)

    def test_unquoted_reserved_frontmatter_scalar_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "crisp" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            skill.write_text(
                text.replace(
                    'activation: "`/crisp`, `/crisp on`, compression request"',
                    "activation: `/crisp`, `/crisp on`, compression request",
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

    def test_planned_plan_can_be_cancelled(self):
        text = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("planned -> in-progress | cancelled", text)

    def test_readme_documents_complete_validation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate-skills.py", text)
        self.assertIn("python3 -m unittest discover -s tests -v", text)

    def test_spec_drive_has_only_spec_drive_command_alias(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'activation: "`/spec-drive`, contract-sensitive change, planning request"',
            skill,
        )
        self.assertNotIn("/sdd", skill)

    def test_peer_skills_do_not_hardcode_plan_paths(self):
        peer_skills = [
            "challenge",
            "crisp",
            "crisp-commit",
            "git-conflict",
            "lean-design",
            "lean-mode",
            "lean-review",
            "lean-test",
        ]
        for name in peer_skills:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertNotIn(
                ".plans/YYYY-MM-DD",
                text,
                f"Skill {name} hardcodes .plans/ path instead of delegating to spec-drive",
            )

    def test_empty_block_scalar_description_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "crisp" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            lines = text.splitlines()
            end = lines.index("---", 1)
            new_lines = []
            for line in lines[:end]:
                if line.startswith("description:"):
                    new_lines.append("description: >")
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
        self.assertIn("missing description", result.stdout)

    def test_multiline_block_scalar_description_passes(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "crisp" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            lines = text.splitlines()
            end = lines.index("---", 1)
            new_lines = []
            for line in lines[:end]:
                if line.startswith("description:"):
                    new_lines.append("description: >")
                    new_lines.append("  Line one of description.")
                    new_lines.append("  Line two of description.")
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

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
