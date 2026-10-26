#!/usr/bin/env python3
"""Validate skill metadata, repository contracts, and ASCII-only Markdown."""

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
AGENTS = ROOT / "AGENTS.md"
PLANS = ROOT / ".plans"
SPEC = ROOT / "spec" / "skills-spec.md"
README = ROOT / "README.md"

REQUIRED_SAFETY_GUARD_SENTENCE = (
    "Do not stage, commit, push, reset, discard, or clean changes, and do not run "
    "destructive commands such as `git push`, `git reset --hard`, `git clean -f`, "
    "or `rm -rf`, without explicit user request."
)

PLAN_STATUSES = frozenset(
    {"planned", "in-progress", "blocked", "complete", "cancelled"}
)


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    role: str
    activation: str
    modification_authority: str
    description: str


@dataclass(frozen=True)
class ValidationReport:
    skills: dict[str, SkillMetadata]
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


# ============================================================================
# Read-only Core: parsing and verification (no writes)
# ============================================================================


def parse_frontmatter_dict(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated frontmatter") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            field = match.group(1)
            value = match.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                raise ValueError(f"{field} block scalar not permitted")
            if value.startswith(("`", "@")):
                raise ValueError(
                    f"{field} plain value cannot start with reserved character "
                    f"{value[0]!r}"
                )
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            values[field] = value
    return values


def parse_skill_metadata(
    path: Path, root: Path = ROOT
) -> tuple[SkillMetadata | None, list[str]]:
    errors: list[str] = []
    try:
        raw = parse_frontmatter_dict(path)
    except ValueError as exc:
        return None, [f"{path.relative_to(root)}: {exc}"]

    expected_name = path.parent.name
    name = raw.get("name")
    if name != expected_name:
        errors.append(
            f"{path.relative_to(root)}: name={name!r}, expected {expected_name!r}"
        )

    description = raw.get("description", "")
    if not description:
        errors.append(f"{path.relative_to(root)}: missing description")

    for field in ("role", "activation", "modification-authority"):
        if not raw.get(field):
            errors.append(f"{path.relative_to(root)}: missing {field}")

    if errors or not name:
        return None, errors

    metadata = SkillMetadata(
        name=name,
        role=raw.get("role", ""),
        activation=raw.get("activation", ""),
        modification_authority=raw.get("modification-authority", ""),
        description=description,
    )
    return metadata, []


def check_ascii_markdown(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    markdown_files = sorted(
        path for path in root.rglob("*.md") if ".git" not in path.parts
    )
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        if text.isascii():
            continue
        for line_number, line in enumerate(text.splitlines(keepends=True), 1):
            non_ascii = sorted({char for char in line if not char.isascii()})
            if non_ascii:
                codepoints = ", ".join(f"U+{ord(char):04X}" for char in non_ascii)
                errors.append(
                    f"{path.relative_to(root)}: non-ASCII Markdown content "
                    f"at line {line_number} ({codepoints})"
                )
                break
    return errors


def check_skill_frontmatters(
    skills_dir: Path = SKILLS, root: Path = ROOT
) -> tuple[dict[str, SkillMetadata], list[str]]:
    errors: list[str] = []
    skills: dict[str, SkillMetadata] = {}
    if not skills_dir.is_dir():
        errors.append(f"skills directory not found: {skills_dir.relative_to(root)}")
        return skills, errors

    subdirs = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    for subdir in subdirs:
        skill_file = subdir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md in {subdir.relative_to(root)}")

    skill_files = sorted(skills_dir.glob("*/SKILL.md"))
    if not skill_files:
        errors.append(f"no skills found in {skills_dir.relative_to(root)}")
        return skills, errors

    for path in skill_files:
        metadata, parse_errors = parse_skill_metadata(path, root)
        errors.extend(parse_errors)
        if metadata:
            skills[metadata.name] = metadata

    return skills, errors


def check_plan_paths(plans_dir: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not plans_dir.exists():
        return errors

    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for path in plans_dir.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        relative = path.relative_to(plans_dir)
        if (
            len(relative.parts) != 2
            or not date_pattern.fullmatch(relative.parts[0])
            or path.suffix != ".md"
        ):
            errors.append(
                f"plan must be .plans/YYYY-MM-DD/[task-name].md: {path.relative_to(root)}"
            )
            continue
        try:
            date.fromisoformat(relative.parts[0])
        except ValueError:
            errors.append(
                f"plan must use a valid ISO calendar date: {path.relative_to(root)}"
            )
    return errors


def check_plan_status(plans_dir: Path, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not plans_dir.exists():
        return errors

    for path in sorted(plans_dir.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        status_match = re.search(r"^- Status:\s*`([^`]+)`", text, re.MULTILINE)
        if not status_match:
            errors.append(f"plan missing Status field: {path.relative_to(root)}")
        elif status_match.group(1) not in PLAN_STATUSES:
            errors.append(
                f"plan has unknown status {status_match.group(1)!r}: {path.relative_to(root)}"
            )
    return errors


def check_safety_guards(agents_path: Path) -> list[str]:
    errors: list[str] = []
    if not agents_path.is_file():
        errors.append(f"missing AGENTS.md file: {agents_path}")
        return errors
    agents_text = agents_path.read_text(encoding="utf-8")
    if REQUIRED_SAFETY_GUARD_SENTENCE not in agents_text:
        errors.append(
            f"AGENTS.md missing exact destructive-command guard sentence: "
            f"{REQUIRED_SAFETY_GUARD_SENTENCE}"
        )
    return errors


def check_spec_gates(
    spec_path: Path, readme_path: Path, root: Path = ROOT
) -> list[str]:
    errors: list[str] = []
    if not spec_path.exists():
        errors.append(f"missing specification file: {spec_path.relative_to(root)}")
        return errors

    spec_text = spec_path.read_text(encoding="utf-8")
    status_match = re.search(r"^- Status:\s*`([^`]+)`", spec_text, re.MULTILINE)
    if not status_match:
        errors.append(f"{spec_path.relative_to(root)}: missing or invalid Status field")
        return errors

    status = status_match.group(1).strip()
    if status == "stable":
        gates_match = re.search(
            r"## 4\. Quality Gates\s*\n(.*?)(?=\n##|\Z)", spec_text, re.DOTALL
        )
        if not gates_match:
            errors.append(
                f"{spec_path.relative_to(root)}: missing '## 4. Quality Gates' section"
            )
        else:
            unchecked = re.findall(r"^\s*-\s*\[ \]", gates_match.group(1), re.MULTILINE)
            if unchecked:
                errors.append(
                    f"{spec_path.relative_to(root)}: status is 'stable' but has {len(unchecked)} unchecked quality gate(s)"
                )

    if readme_path.exists():
        readme_text = readme_path.read_text(encoding="utf-8")
        readme_match = re.search(
            r"The skill specification is currently `([^`]+)`\.", readme_text
        )
        if not readme_match:
            errors.append(
                f"{readme_path.relative_to(root)}: missing 'The skill specification is currently `...`.' statement"
            )
        elif readme_match.group(1) != status:
            errors.append(
                f"{readme_path.relative_to(root)}: status `{readme_match.group(1)}` does not match "
                f"{spec_path.relative_to(root)} status `{status}`"
            )

    return errors


def validate_repository(
    root: Path = ROOT,
    skills_dir: Path = SKILLS,
    agents_path: Path = AGENTS,
    plans_dir: Path = PLANS,
    spec_path: Path = SPEC,
    readme_path: Path = README,
) -> ValidationReport:
    errors: list[str] = []
    errors.extend(check_ascii_markdown(root))

    skills, skill_errors = check_skill_frontmatters(skills_dir, root)
    errors.extend(skill_errors)

    errors.extend(check_plan_paths(plans_dir, root))
    errors.extend(check_plan_status(plans_dir, root))
    errors.extend(check_safety_guards(agents_path))
    errors.extend(check_spec_gates(spec_path, readme_path, root))

    return ValidationReport(skills=skills, errors=errors)


# ============================================================================
# Imperative Shell: CLI runner and formatting
# ============================================================================


def main() -> int:
    report = validate_repository(ROOT, SKILLS, AGENTS, PLANS, SPEC, README)

    if not report.is_valid:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in report.errors))
        return 1

    print(f"Validated {len(report.skills)} skills frontmatter metadata.")
    print(
        "Validated ASCII-only Markdown, dated plan paths, plan status, destructive-command guards, and spec gates."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
