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
    def test_crisp_has_no_commit_mode(self):
        skill = (ROOT / "skills" / "crisp" / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Commit Message Mode", skill)
        self.assertNotIn("/crisp commit", skill)
        self.assertNotIn("Conventional Commits", skill)

    def test_skills_use_role_based_adapters(self):
        challenge = (ROOT / "skills" / "challenge" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        lean_design = (ROOT / "skills" / "lean-design" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        lean_review = (ROOT / "skills" / "lean-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Implementation Engine (default: `lean-mode`)", challenge)
        self.assertIn("Plan Coordinator (default: `spec-drive`)", challenge)
        self.assertIn("Implementation Engine (default: `lean-mode`)", lean_design)
        self.assertIn("Implementation Engine (default: `lean-mode`)", lean_review)
        self.assertIn("Plan Coordinator (default: `spec-drive`)", lean_review)

    def test_spec_drive_protocol_gates(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Quality Gate", skill)
        self.assertIn("Structural Designer (default: `lean-design`)", skill)
        self.assertIn("Implementation Engine (default: `lean-mode`)", skill)
        self.assertIn("Review Gate (default: `lean-review`)", skill)

    def test_lean_mode_subcontracts(self):
        skill = (ROOT / "skills" / "lean-mode" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Sub-Contract 1: Minimal Implementation", skill)
        self.assertIn("## Sub-Contract 2: Deterministic Testing", skill)

    def test_catalog_validates(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate-skills.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_seven_skills_registered(self):
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
        expected = [
            "challenge",
            "crisp",
            "git-conflict",
            "lean-design",
            "lean-mode",
            "lean-review",
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
                    'activation: "`/crisp`, compression request"',
                    "activation: `/crisp`, compression request",
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
        text = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("planned -> in-progress | cancelled", text)

    def test_blocked_plan_can_be_cancelled(self):
        text = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("blocked -> in-progress | cancelled", text)

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
            "git-conflict",
            "lean-design",
            "lean-mode",
            "lean-review",
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

    def test_git_conflict_requires_explicit_commit_request(self):
        skill = (ROOT / "skills" / "git-conflict" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("necessarily requires completing the integration", skill)
        self.assertIn(
            "Do not stash, commit, or push unless the user explicitly requests that operation.",
            skill,
        )

    def test_git_conflict_commands_are_shell_neutral(self):
        skill = (ROOT / "skills" / "git-conflict" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("|| true", skill)
        self.assertNotIn("grep", skill)
        self.assertIn("git diff --cached --name-only --diff-filter=U", skill)

    def test_spec_drive_verifies_after_refactor(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        red_idx = skill.find("1. **Red:**")
        green_idx = skill.find("2. **Green:**")
        refactor_idx = skill.find("3. **Refactor:**")
        verify_idx = skill.find("4. **Verify:**")
        self.assertTrue(red_idx < green_idx < refactor_idx < verify_idx)

    def test_spec_drive_phase4_runs_lean_review(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("lean-review", skill)
        self.assertIn("Blocking: No", skill)

    def test_spec_drive_has_no_invariants_matrix(self):
        skill = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Invariants Matrix", skill)

    def test_lean_review_hands_off_blocking_findings(self):
        skill = (ROOT / "skills" / "lean-review" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("lean-mode", skill)
        self.assertIn("Blocking: Yes", skill)

    def test_permissive_safety_guard_clause_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            agents = repository / "AGENTS.md"
            text = agents.read_text(encoding="utf-8")
            agents.write_text(
                text.replace(
                    "never run destructive commands such as `git push`, `git reset --hard`, `git clean -f`, or `rm -rf`, unless explicitly requested.",
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

    def test_spec_drive_registers_all_roles(self):
        spec_drive = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        roles = (
            "Plan Coordinator",
            "Structural Designer",
            "Implementation Engine",
            "Review Gate",
        )

        self.assertIn("### Role Registry", spec_drive)
        for role in roles:
            self.assertIn(f"| {role} |", spec_drive)

    def test_verification_record_gates_plan_checklist(self):
        lean_mode = (ROOT / "skills" / "lean-mode" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        spec_drive = (ROOT / "skills" / "spec-drive" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Result: pass | fail | inconclusive", lean_mode)
        self.assertIn("check the item only on `Result: pass`", spec_drive)

    def test_spec_routes_implementation_skills(self):
        spec = (ROOT / "spec" / "skills-spec.md").read_text(encoding="utf-8")
        routing = spec.split("### 3.2 Implementation Routing", 1)[1].split(
            "### 3.3", 1
        )[0]

        for name in (
            "lean-design",
            "spec-drive",
            "lean-mode",
            "lean-review",
            "git-conflict",
        ):
            self.assertIn(f"`{name}`", routing)

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

    def test_transition_table_drift_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "spec-drive" / "SKILL.md"
            text = skill.read_text(encoding="utf-8").replace(
                "blocked -> in-progress | cancelled",
                "blocked -> in-progress",
                1,
            )
            skill.write_text(text, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "missing plan transition `blocked -> in-progress | cancelled`",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
