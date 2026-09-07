#!/usr/bin/env python3
"""Validate skill metadata, repository contracts, and ASCII-only Markdown."""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CATALOG = ROOT / "spec" / "skills-spec.md"
AGENTS = ROOT / "AGENTS.md"
PLANS = ROOT / ".plans"


def frontmatter(path: Path) -> dict[str, str]:
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
            if value.startswith(("`", "@")):
                raise ValueError(
                    f"{field} plain value cannot start with reserved character "
                    f"{value[0]!r}"
                )
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            values[field] = value
    return values


def catalog_rows(text: str) -> list[dict[str, str]]:
    section = text.split("## 3. Routing and Handoffs", 1)[0]
    table = section.split("## 2. Skill Catalog", 1)[-1]
    rows: list[dict[str, str]] = []
    for line in table.splitlines():
        if not line.startswith("|") or line.startswith(("| ---", "| Skill")):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) == 4 and all(fields):
            rows.append(
                {
                    "name": fields[0].strip("`").strip(),
                    "role": fields[1],
                    "activation": fields[2],
                    "modification-authority": fields[3],
                }
            )
    return rows


def markdown_ascii_errors() -> list[str]:
    errors: list[str] = []
    markdown_files = sorted(
        path for path in ROOT.rglob("*.md") if ".git" not in path.parts
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
                    f"{path.relative_to(ROOT)}: non-ASCII Markdown content "
                    f"at line {line_number} ({codepoints})"
                )
                break
    return errors


def main() -> int:
    errors = markdown_ascii_errors()
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    actual_names: set[str] = set()
    metadata_by_name: dict[str, dict[str, str]] = {}

    for path in skill_files:
        try:
            metadata = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        expected = path.parent.name
        name = metadata.get("name")
        if name != expected:
            errors.append(
                f"{path.relative_to(ROOT)}: name={name!r}, expected {expected!r}"
            )
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
        for field in ("role", "activation", "modification-authority"):
            if not metadata.get(field):
                errors.append(f"{path.relative_to(ROOT)}: missing {field}")
        if name:
            if name in actual_names:
                errors.append(f"duplicate skill name: {name}")
            actual_names.add(name)
            metadata_by_name[name] = metadata

    catalog_text = CATALOG.read_text(encoding="utf-8")
    catalog_entries = catalog_rows(catalog_text)
    listed_names = [row["name"] for row in catalog_entries]
    listed_counts: dict[str, int] = {}
    for name in listed_names:
        listed_counts[name] = listed_counts.get(name, 0) + 1
    for name, count in sorted(listed_counts.items()):
        if count != 1:
            errors.append(
                f"catalog skill must appear exactly once: {name} ({count} rows)"
            )

    catalog_section = catalog_text.split("## 3. Routing and Handoffs", 1)[0]
    catalog_table = catalog_section.split("## 2. Skill Catalog", 1)[-1]
    for line in catalog_table.splitlines():
        if not line.startswith("|") or line.startswith(("| ---", "| Skill")):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) != 4 or any(not field for field in fields):
            errors.append(f"malformed catalog row: {line}")

    listed_name_set = set(listed_names)
    for name in sorted(actual_names - listed_name_set):
        errors.append(f"catalog missing skill: {name}")
    for name in sorted(listed_name_set - actual_names):
        errors.append(f"catalog lists absent skill: {name}")

    for row in catalog_entries:
        metadata = metadata_by_name.get(row["name"])
        if metadata is None:
            continue
        for field in ("role", "activation", "modification-authority"):
            if metadata.get(field) != row[field]:
                errors.append(
                    f"catalog mismatch for {row['name']}: {field}="
                    f"{metadata.get(field)!r}, expected {row[field]!r}"
                )

    required_catalog_terms = (
        "Activation",
        "Modification authority",
        "Challenge Routing",
        "Implementation Routing",
        "exactly one",
        "user approval",
    )
    for term in required_catalog_terms:
        if term not in catalog_text:
            errors.append(f"catalog missing routing/authority term: {term}")

    if PLANS.exists():
        date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        for path in PLANS.rglob("*"):
            if not path.is_file() or path.name.startswith("."):
                continue
            relative = path.relative_to(PLANS)
            if (
                len(relative.parts) != 2
                or not date_pattern.fullmatch(relative.parts[0])
                or path.suffix != ".md"
            ):
                errors.append(
                    f"plan must be .plans/YYYY-MM-DD/<task-name>.md: {path.relative_to(ROOT)}"
                )
                continue
            try:
                date.fromisoformat(relative.parts[0])
            except ValueError:
                errors.append(
                    f"plan must use a valid ISO calendar date: {path.relative_to(ROOT)}"
                )


    agents_text = AGENTS.read_text(encoding="utf-8")
    for term in ("git push", "git reset --hard", "git clean -f", "rm -rf"):
        if term not in agents_text:
            errors.append(f"AGENTS.md missing destructive-command guard: {term}")

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Validated {len(skill_files)} skills and catalog parity.")
    print(
        "Validated ASCII-only Markdown, routing/authority markers, approval, dated plan paths, and destructive-command guards."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
