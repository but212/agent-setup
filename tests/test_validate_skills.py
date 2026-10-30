import importlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
validator = importlib.import_module("validate-skills")


def clone_repo_to_temp(directory: str) -> Path:
    repository = Path(directory) / "repo"
    shutil.copytree(
        ROOT,
        repository,
        ignore=shutil.ignore_patterns(".git", "__pycache__", ".ruff_cache"),
    )
    return repository


def find_tracked_crlf_files(root: Path) -> list[str]:
    suffixes = {".md", ".py", ".sh", ".yml", ".yaml"}
    named_files = {"LICENSE", "NOTICE", ".gitattributes", ".gitignore"}
    crlf_files: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(
            (part.startswith(".") and part != ".github") or part == "__pycache__"
            for part in rel_parts[:-1]
        ):
            continue
        if (
            path.suffix in suffixes or path.name in named_files
        ) and b"\r\n" in path.read_bytes():
            crlf_files.append(str(path.relative_to(root)))
    return crlf_files


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

    def test_non_ascii_markdown_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            agents = repository / "AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8") + "\n\u2028\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)

        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\n\u2028\n", encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)

    def test_non_ascii_non_agent_markdown_passes(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            readme = repository / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\n한글 설명 및 유니코드 다이어그램\n",
                encoding="utf-8",
            )
            spec = repository / "docs" / "skills-spec.md"
            spec.write_text(
                spec.read_text(encoding="utf-8") + "\n한글 주석\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_gitattributes_enforces_lf(self):
        gitattributes = ROOT / ".gitattributes"
        self.assertTrue(gitattributes.is_file(), ".gitattributes must exist")
        content = gitattributes.read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", content)

    def test_tracked_text_files_use_lf_line_endings(self):
        crlf_files = find_tracked_crlf_files(ROOT)
        self.assertEqual(crlf_files, [], f"Found CRLF in files: {crlf_files}")

    def test_find_tracked_crlf_files_detects_crlf_in_dotfiles_and_github_workflows(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-crlf-") as tmp:
            tmp_root = Path(tmp)
            gitattr = tmp_root / ".gitattributes"
            gitattr.write_bytes(b"* text=auto\r\n")
            workflow = tmp_root / ".github" / "workflows" / "ci.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_bytes(b"name: CI\r\n")

            crlf_files = find_tracked_crlf_files(tmp_root)
            normalized = [p.replace("\\", "/") for p in crlf_files]
            self.assertIn(".gitattributes", normalized)
            self.assertIn(".github/workflows/ci.yml", normalized)

    def test_check_agents_file_supports_root_and_relative_path(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-agents-") as tmp:
            tmp_root = Path(tmp)
            missing = tmp_root / "nested" / "AGENTS.md"
            errors = validator.check_agents_file(missing, root=tmp_root)
            self.assertEqual(len(errors), 1)
            self.assertIn(str(Path("nested") / "AGENTS.md"), errors[0])
            self.assertNotIn(str(tmp_root), errors[0])

    def test_missing_agents_file_reports_error_without_crash(self):
        report = validator.validate_repository(
            agents_path=ROOT / "NONEXISTENT_AGENTS.md"
        )
        self.assertFalse(report.is_valid)
        self.assertTrue(any("missing AGENTS.md" in err for err in report.errors))

    def test_missing_skills_dir_reports_error(self):
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

    def test_frontmatter_inline_json_array_passes(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            content = skill.read_text(encoding="utf-8")
            content = re.sub(
                r"^activation:.*$",
                'activation: ["/challenge", "/grill-me"]',
                content,
                flags=re.MULTILINE,
            )
            skill.write_text(content, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_parse_frontmatter_text_normalizes_inline_json_and_comments(self):
        raw_text = (
            "---\n"
            "name: test-skill\n"
            'activation: ["/a", "/b"] # inline comment\n'
            'role: "quoted role"\n'
            "---\n"
            "# Content\n"
        )
        parsed = validator.parse_frontmatter_text(raw_text)
        self.assertEqual(parsed["name"], "test-skill")
        self.assertEqual(parsed["activation"], "/a, /b")
        self.assertEqual(parsed["role"], "quoted role")

    def test_parse_frontmatter_text_preserves_hash_inside_quotes_and_json_array(self):
        raw_text = (
            "---\n"
            "name: test-skill\n"
            'description: "Fix issue #42 and optimize" # inline comment\n'
            'role: "Security #1 Lead" # comment with hash # inside\n'
            'activation: ["tag #1", "tag #2"] # list comment\n'
            "modification-authority: 'Maintainer #5' # single quoted\n"
            "---\n"
            "# Content\n"
        )
        parsed = validator.parse_frontmatter_text(raw_text)
        self.assertEqual(parsed["name"], "test-skill")
        self.assertEqual(parsed["description"], "Fix issue #42 and optimize")
        self.assertEqual(parsed["role"], "Security #1 Lead")
        self.assertEqual(parsed["activation"], "tag #1, tag #2")
        self.assertEqual(parsed["modification-authority"], "Maintainer #5")

    def test_scan_non_ascii_lines_pure(self):
        findings = validator.scan_non_ascii_lines("hello\nworld\n")
        self.assertEqual(findings, [])

        findings = validator.scan_non_ascii_lines("hello\nworld \u2028\n")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0][0], 2)
        self.assertIn("U+2028", findings[0][1])

    def test_validate_plan_path_parts_pure(self):
        self.assertEqual(
            validator.validate_plan_path_parts(("2026-01-01", "task.md"), ".md"),
            [],
        )
        errs = validator.validate_plan_path_parts(("2026-99-99", "task.md"), ".md")
        self.assertTrue(any("valid ISO calendar date" in e for e in errs))
        errs = validator.validate_plan_path_parts(("2026-01-01", "task.txt"), ".txt")
        self.assertTrue(any("must be .plans" in e for e in errs))

    def test_frontmatter_multiline_block_scalar_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            content = skill.read_text(encoding="utf-8")
            content = re.sub(
                r"^description:.*$",
                "description: >\n  A multiline description.",
                content,
                flags=re.MULTILINE,
            )
            skill.write_text(content, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)

    def test_frontmatter_nested_list_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            skill = repository / "skills" / "challenge" / "SKILL.md"
            content = skill.read_text(encoding="utf-8")
            content = re.sub(
                r"^activation:.*$",
                "activation:\n  - /challenge\n  - /grill-me",
                content,
                flags=re.MULTILINE,
            )
            skill.write_text(content, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)

    def test_validate_document_line_count_pure(self):
        normal_text = "\n".join(f"line {i}" for i in range(50))
        self.assertEqual(validator.validate_document_line_count(normal_text, 200), [])

        overflow_text = "\n".join(f"line {i}" for i in range(205))
        errors = validator.validate_document_line_count(overflow_text, 200)
        self.assertEqual(len(errors), 1)

    def test_document_exceeding_line_budget_fails(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-validator-") as directory:
            repository = clone_repo_to_temp(directory)
            agents = repository / "AGENTS.md"
            bloat = "\n".join(f"# Bloat rule {i}" for i in range(250))
            agents.write_text(agents.read_text(encoding="utf-8") + "\n" + bloat + "\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "scripts/validate-skills.py"],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)

    def test_validate_plan_status_flexible_syntax(self):
        self.assertEqual(
            validator.validate_plan_status_text("Status: planned\n"), []
        )
        self.assertEqual(
            validator.validate_plan_status_text("- Status: `in-progress`\n"), []
        )
        errors = validator.validate_plan_status_text("Status: `invalid`\n")
        self.assertEqual(len(errors), 1)

    def test_check_ascii_markdown_external_paths_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            ext_agents = ext_dir / "CUSTOM_AGENTS.md"
            ext_agents.write_text("# Non-ASCII: \u2014\n", encoding="utf-8")
            ext_skills = ext_dir / "custom_skills"
            ext_skills.mkdir()
            (ext_skills / "test.md").write_text("# Non-ASCII: \u2022\n", encoding="utf-8")

            errors = validator.check_ascii_markdown(
                agents_path=ext_agents,
                skills_dir=ext_skills,
                root=ROOT,
            )
            self.assertEqual(len(errors), 2)
            self.assertTrue(any("CUSTOM_AGENTS.md" in err for err in errors))
            self.assertTrue(any("test.md" in err for err in errors))

    def test_check_document_line_limits_external_paths_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            ext_agents = ext_dir / "CUSTOM_AGENTS.md"
            ext_agents.write_text("\n".join(f"line {i}" for i in range(10)) + "\n", encoding="utf-8")
            ext_skills = ext_dir / "custom_skills"
            skill_sub = ext_skills / "s1"
            skill_sub.mkdir(parents=True)
            (skill_sub / "SKILL.md").write_text("\n".join(f"line {i}" for i in range(10)) + "\n", encoding="utf-8")

            errors = validator.check_document_line_limits(
                agents_path=ext_agents,
                skills_dir=ext_skills,
                root=ROOT,
                max_lines=5,
            )
            self.assertEqual(len(errors), 2)
            self.assertTrue(any("CUSTOM_AGENTS.md" in err for err in errors))
            self.assertTrue(any("SKILL.md" in err for err in errors))

    def test_parse_skill_metadata_external_path_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            skill_sub = ext_dir / "my-skill"
            skill_sub.mkdir()
            skill_file = skill_sub / "SKILL.md"
            skill_file.write_text("invalid frontmatter\n", encoding="utf-8")

            metadata, errors = validator.parse_skill_metadata(skill_file, root=ROOT)
            self.assertIsNone(metadata)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing frontmatter", errors[0])

    def test_check_skill_frontmatters_external_paths_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            ext_skills = ext_dir / "custom_skills"
            ext_skills.mkdir()
            skill_sub = ext_skills / "my-skill"
            skill_sub.mkdir()
            (skill_sub / "SKILL.md").write_text(
                "---\nname: wrong-name\nrole: r\nactivation: a\nmodification-authority: m\ndescription: d\n---\n",
                encoding="utf-8",
            )

            skills, errors = validator.check_skill_frontmatters(ext_skills, root=ROOT)
            self.assertEqual(len(skills), 0)
            self.assertEqual(len(errors), 1)
            self.assertTrue(any("wrong-name" in err for err in errors))

    def test_check_plan_paths_external_paths_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            ext_plans = ext_dir / "plans"
            bad_plan = ext_plans / "not-a-date" / "task.txt"
            bad_plan.parent.mkdir(parents=True)
            bad_plan.write_text("test", encoding="utf-8")

            errors = validator.check_plan_paths(ext_plans, root=ROOT)
            self.assertEqual(len(errors), 1)
            self.assertIn(str(bad_plan), errors[0])

    def test_check_plan_status_external_paths_without_crash(self):
        with tempfile.TemporaryDirectory(prefix="agent-setup-external-") as tmp:
            ext_dir = Path(tmp)
            ext_plans = ext_dir / "plans"
            plan_file = ext_plans / "2026-01-01" / "task.md"
            plan_file.parent.mkdir(parents=True)
            plan_file.write_text("Status: invalid\n", encoding="utf-8")

            errors = validator.check_plan_status(ext_plans, root=ROOT)
            self.assertEqual(len(errors), 1)
            self.assertIn("unknown status", errors[0])
            self.assertIn(str(plan_file), errors[0])

    def test_frontmatter_block_scalar_with_chomping_indicator_fails(self):
        raw_text = (
            "---\n"
            "name: test-skill\n"
            "role: test\n"
            "activation: test\n"
            "modification-authority: None\n"
            "description: |-\n"
            "  A multiline description.\n"
            "---\n"
            "# Content\n"
        )
        with self.assertRaises(ValueError) as ctx:
            validator.parse_frontmatter_text(raw_text)
        self.assertIn("multiline block scalars", str(ctx.exception))

    def test_frontmatter_unrecognized_non_key_value_line_fails(self):
        raw_text = (
            "---\n"
            "name: test-skill\n"
            "role: test\n"
            "activation: test\n"
            "modification-authority: None\n"
            "description: A valid description\n"
            "malformed syntax without colon\n"
            "---\n"
            "# Content\n"
        )
        with self.assertRaises(ValueError) as ctx:
            validator.parse_frontmatter_text(raw_text)
        self.assertIn("unsupported frontmatter line", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
