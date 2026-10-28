#!/usr/bin/env python3
"""Validate skill metadata, repository contracts, and ASCII-only Markdown."""

import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
AGENTS = ROOT / "AGENTS.md"
PLANS = ROOT / ".plans"

PLAN_STATUSES = frozenset(
    {"planned", "in-progress", "blocked", "complete", "cancelled"}
)
MAX_AGENT_DOC_LINES = 200


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


def parse_frontmatter_text(text: str) -> dict[str, str]:
    """Parse YAML frontmatter text into a normalized flat key-value dict."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated frontmatter") from exc

    values: dict[str, str] = {}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if re.search(r":\s*[|>]\s*$", stripped):
            raise ValueError(
                "multiline block scalars (| or >) are unsupported; use single-line string"
            )
        if stripped.startswith("- "):
            raise ValueError(
                "nested list items (- item) are unsupported; use inline JSON array"
            )

        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            field = match.group(1)
            raw_value = match.group(2).strip()
            if " #" in raw_value and not (
                raw_value.startswith(('"', "'")) and raw_value.endswith(('"', "'"))
            ):
                raw_value = raw_value.split(" #", 1)[0].strip()

            if raw_value.startswith("[") and raw_value.endswith("]"):
                try:
                    items = json.loads(raw_value)
                    if isinstance(items, list):
                        raw_value = ", ".join(str(x) for x in items)
                except json.JSONDecodeError:
                    pass
            elif (
                len(raw_value) >= 2
                and raw_value[0] == raw_value[-1]
                and raw_value[0] in "'\""
            ):
                raw_value = raw_value[1:-1]

            values[field] = raw_value
    return values


def validate_skill_metadata_fields(
    raw: dict[str, str], expected_name: str
) -> tuple[SkillMetadata | None, list[str]]:
    """Validate parsed frontmatter dictionary against required skill contracts."""
    errors: list[str] = []
    name = raw.get("name")
    if name != expected_name:
        errors.append(f"name={name!r}, expected {expected_name!r}")

    description = raw.get("description", "")
    if not description:
        errors.append("missing description")

    for field in ("role", "activation", "modification-authority"):
        if not raw.get(field):
            errors.append(f"missing {field}")

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


def scan_non_ascii_lines(text: str) -> list[tuple[int, str]]:
    """Scan text and return (line_number, codepoints) for any line containing non-ASCII characters."""
    findings: list[tuple[int, str]] = []
    if text.isascii():
        return findings
    for line_number, line in enumerate(text.splitlines(keepends=True), 1):
        non_ascii = sorted({char for char in line if not char.isascii()})
        if non_ascii:
            codepoints = ", ".join(f"U+{ord(char):04X}" for char in non_ascii)
            findings.append((line_number, codepoints))
    return findings


def validate_plan_path_parts(rel_parts: tuple[str, ...], suffix: str) -> list[str]:
    """Validate that plan path parts conform to YYYY-MM-DD/[task-name].md."""
    errors: list[str] = []
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if (
        len(rel_parts) != 2
        or not date_pattern.fullmatch(rel_parts[0])
        or suffix != ".md"
    ):
        errors.append("plan must be .plans/YYYY-MM-DD/[task-name].md")
        return errors
    try:
        date.fromisoformat(rel_parts[0])
    except ValueError:
        errors.append("plan must use a valid ISO calendar date")
    return errors


def validate_plan_status_text(
    text: str, allowed_statuses: frozenset[str] = PLAN_STATUSES
) -> list[str]:
    """Validate status field embedded in plan markdown text."""
    errors: list[str] = []
    status_match = re.search(
        r"^(?:-\s*)?Status:\s*`?([a-zA-Z0-9_-]+)`?", text, re.MULTILINE
    )
    if not status_match:
        errors.append("plan missing Status field")
    elif status_match.group(1) not in allowed_statuses:
        errors.append(f"plan has unknown status {status_match.group(1)!r}")
    return errors


def validate_document_line_count(
    text: str, max_lines: int = MAX_AGENT_DOC_LINES
) -> list[str]:
    """Validate that document does not exceed max line budget."""
    lines = text.splitlines()
    if len(lines) > max_lines:
        return [f"exceeds line budget ({len(lines)} > {max_lines} lines)"]
    return []


def parse_frontmatter_dict(path: Path) -> dict[str, str]:
    """Compatibility wrapper reading path and delegating to parse_frontmatter_text."""
    return parse_frontmatter_text(path.read_text(encoding="utf-8"))


def parse_skill_metadata(
    path: Path, root: Path = ROOT
) -> tuple[SkillMetadata | None, list[str]]:
    """Parse and validate SKILL.md file."""
    try:
        raw = parse_frontmatter_dict(path)
    except ValueError as exc:
        return None, [f"{path.relative_to(root)}: {exc}"]
    metadata, errors = validate_skill_metadata_fields(raw, path.parent.name)
    return metadata, [f"{path.relative_to(root)}: {err}" for err in errors]


def check_ascii_markdown(
    agents_path: Path = AGENTS,
    skills_dir: Path = SKILLS,
    root: Path = ROOT,
) -> list[str]:
    """Verify that AGENTS.md and skills/ markdown files contain only ASCII characters."""
    if agents_path.is_dir() and skills_dir == SKILLS:
        actual_root = agents_path
        actual_agents = actual_root / "AGENTS.md"
        actual_skills = actual_root / "skills"
    else:
        actual_root = root
        actual_agents = agents_path
        actual_skills = skills_dir

    errors: list[str] = []
    markdown_files: list[Path] = []
    if actual_agents.is_file():
        markdown_files.append(actual_agents)
    if actual_skills.is_dir():
        markdown_files.extend(
            path
            for path in sorted(actual_skills.rglob("*.md"))
            if ".git" not in path.parts
        )
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        findings = scan_non_ascii_lines(text)
        if findings:
            first_line, codepoints = findings[0]
            errors.append(
                f"{path.relative_to(actual_root)}: non-ASCII Markdown content "
                f"at line {first_line} ({codepoints})"
            )
    return errors


def check_skill_frontmatters(
    skills_dir: Path = SKILLS, root: Path = ROOT
) -> tuple[dict[str, SkillMetadata], list[str]]:
    """Check that all skills directories contain valid SKILL.md files."""
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
    """Validate all files under .plans/ follow date directory hierarchy."""
    errors: list[str] = []
    if not plans_dir.exists():
        return errors

    for path in plans_dir.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel_parts = path.relative_to(plans_dir).parts
        part_errors = validate_plan_path_parts(rel_parts, path.suffix)
        for err in part_errors:
            errors.append(f"{err}: {path.relative_to(root)}")
    return errors


def check_plan_status(plans_dir: Path, root: Path = ROOT) -> list[str]:
    """Check that all plan markdown files specify a recognized Status."""
    errors: list[str] = []
    if not plans_dir.exists():
        return errors

    for path in sorted(plans_dir.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        status_errors = validate_plan_status_text(text)
        for err in status_errors:
            errors.append(f"{err}: {path.relative_to(root)}")
    return errors


def check_agents_file(agents_path: Path) -> list[str]:
    """Verify that AGENTS.md exists."""
    errors: list[str] = []
    if not agents_path.is_file():
        errors.append(f"missing AGENTS.md file: {agents_path}")
    return errors


def check_document_line_limits(
    agents_path: Path = AGENTS,
    skills_dir: Path = SKILLS,
    root: Path = ROOT,
    max_lines: int = MAX_AGENT_DOC_LINES,
) -> list[str]:
    """Verify that agent prompt documents (AGENTS.md, skills/*/SKILL.md) obey line budget invariant."""
    if agents_path.is_dir() and skills_dir == SKILLS:
        actual_root = agents_path
        actual_agents = actual_root / "AGENTS.md"
        actual_skills = actual_root / "skills"
    else:
        actual_root = root
        actual_agents = agents_path
        actual_skills = skills_dir

    errors: list[str] = []
    documents: list[Path] = []
    if actual_agents.is_file():
        documents.append(actual_agents)
    if actual_skills.is_dir():
        documents.extend(sorted(actual_skills.glob("*/SKILL.md")))

    for path in documents:
        text = path.read_text(encoding="utf-8")
        for err in validate_document_line_count(text, max_lines):
            errors.append(f"{path.relative_to(actual_root)}: {err}")
    return errors


def validate_repository(
    root: Path = ROOT,
    skills_dir: Path = SKILLS,
    agents_path: Path = AGENTS,
    plans_dir: Path = PLANS,
) -> ValidationReport:
    """Validate full repository constraints."""
    errors: list[str] = []
    errors.extend(check_ascii_markdown(agents_path, skills_dir, root))
    errors.extend(check_document_line_limits(agents_path, skills_dir, root))

    skills, skill_errors = check_skill_frontmatters(skills_dir, root)
    errors.extend(skill_errors)

    errors.extend(check_plan_paths(plans_dir, root))
    errors.extend(check_plan_status(plans_dir, root))
    errors.extend(check_agents_file(agents_path))

    return ValidationReport(skills=skills, errors=errors)


def main() -> int:
    report = validate_repository(ROOT, SKILLS, AGENTS, PLANS)

    if not report.is_valid:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in report.errors))
        return 1

    print(f"Validated {len(report.skills)} skills frontmatter metadata.")
    print(
        f"Validated ASCII-only Markdown (AGENTS.md, skills/), document line budgets (<= {MAX_AGENT_DOC_LINES} lines), dated plan paths, plan status, and AGENTS.md existence."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
