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

    def test_unquoted_reserved_frontmatter_scalar_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "crisp" / "SKILL.md"
            text = skill.read_text(encoding="utf-8")
            skill.write_text(
                text.replace(
                    'activation: "`/crisp`, `/crisp on`"',
                    "activation: `/crisp`, `/crisp on`",
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

    def test_duplicate_catalog_row_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            specification = repository / "spec" / "skills-spec.md"
            text = specification.read_text(encoding="utf-8")
            row = (
                "| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |"
            )
            self.assertIn(row, text)
            specification.write_text(
                text.replace(row, row + "\n" + row, 1), encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("catalog skill must appear exactly once: crisp", result.stdout)

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

    def test_catalog_contract_mismatch_fails(self):
        row = (
            "| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |"
        )
        replacements = {
            "role": row.replace("Compresses response prose", "Wrong role"),
            "activation": row.replace("/crisp`, `/crisp on", "/wrong"),
            "modification-authority": row.replace("| None |", "| Wrong files |"),
        }
        for field, changed_row in replacements.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory(
                prefix="agent-setup-validator-"
            ) as directory:
                repository = clone_repo_to_temp(directory)
                specification = repository / "spec" / "skills-spec.md"
                text = specification.read_text(encoding="utf-8")
                specification.write_text(
                    text.replace(row, changed_row, 1), encoding="utf-8"
                )

                result = subprocess.run(
                    [sys.executable, "scripts/validate-skills.py"],
                    cwd=repository,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"catalog mismatch for crisp: {field}=", result.stdout)

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
        text = (ROOT / "skills" / "mark-plan" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("planned -> cancelled", text)

    def test_readme_documents_complete_validation(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate-skills.py", text)
        self.assertIn("python3 -m unittest discover -s tests -v", text)

    def test_spec_drive_has_only_spec_drive_command_alias(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        catalog = (ROOT / "spec" / "skills-spec.md").read_text(encoding="utf-8")

        self.assertIn(
            'activation: "`/spec-drive`, contract-sensitive change"', skill
        )
        self.assertNotIn("activation: `/spec-drive`, `/sdd`", skill)
        self.assertIn(
            "| `spec-drive` | Coordinates contract-centered SDD | `/spec-drive`, contract-sensitive change |",
            catalog,
        )
        self.assertNotIn("/sdd", skill)
        self.assertNotIn(
            "| `spec-drive` | Coordinates contract-centered SDD | `/spec-drive`, `/sdd`",
            catalog,
        )

    def test_catalog_table_parsing_heading_agnostic(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            spec_path = repository / "spec" / "skills-spec.md"
            text = spec_path.read_text(encoding="utf-8")
            text = text.replace(
                "## 2. Skill Catalog", "## Section 2: Catalog of Skills", 1
            ).replace(
                "## 3. Routing and Handoffs", "## Section 3: Routing", 1
            )
            spec_path.write_text(text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_malformed_catalog_row_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            spec_path = repository / "spec" / "skills-spec.md"
            text = spec_path.read_text(encoding="utf-8")
            bad_row = "| `crisp` | Missing columns |"
            text = text.replace(
                "| `crisp` | Compresses response prose | `/crisp`, `/crisp on` | None |",
                bad_row,
                1,
            )
            spec_path.write_text(text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("malformed catalog row", result.stdout)

    def test_peer_skills_delegate_plan_paths_to_mark_plan(self):
        peer_skills = ["challenge", "challenge-docs", "challenge-light", "spec-drive", "tdd-plan"]
        for name in peer_skills:
            skill_file = ROOT / "skills" / name / "SKILL.md"
            text = skill_file.read_text(encoding="utf-8")
            self.assertNotIn(
                ".plans/YYYY-MM-DD",
                text,
                f"Skill {name} hardcodes .plans/ path instead of delegating to mark-plan",
            )

    def test_sql_audit_declares_safe_dynamic_analysis(self):
        text = (ROOT / "skills" / "sql-orm-indicator-audit" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Regexes are triage heuristics, not security proofs", text)
        self.assertIn("Never run `EXPLAIN ANALYZE` by default", text)
        self.assertIn("disposable non-production environment", text)
        self.assertIn("Do not execute DDL or DML", text)
        self.assertIn("````markdown", text)
        self.assertEqual(text.count("````"), 2)


if __name__ == "__main__":
    unittest.main()
