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

REQUIRED_CATALOG_TERMS = (
    "Activation",
    "Modification authority",
    "Challenge Routing",
    "Implementation Routing",
    "exactly one",
    "user approval",
)
REQUIRED_SAFETY_GUARDS = (
    "git push",
    "git reset --hard",
    "git clean -f",
    "rm -rf",
)


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated frontmatter") from exc
    values: dict[str, str] = {}
    lines_slice = lines[1:end]
    i = 0
    while i < len(lines_slice):
        line = lines_slice[i]
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            field = match.group(1)
            value = match.group(2).strip()
            if value in (">", "|", ">-", "|-"):
                block_lines: list[str] = []
                i += 1
                while i < len(lines_slice) and (
                    lines_slice[i].startswith((" ", "\t")) or not lines_slice[i].strip()
                ):
                    if lines_slice[i].strip():
                        block_lines.append(lines_slice[i].strip())
                    i += 1
                values[field] = " ".join(block_lines)
                continue
            if value.startswith(("`", "@")):
                raise ValueError(
                    f"{field} plain value cannot start with reserved character "
                    f"{value[0]!r}"
                )
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            values[field] = value
        i += 1
    return values


def parse_catalog_table(text: str) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    lines = text.splitlines()
    in_table = False

    for line in lines:
        stripped = line.strip()
        if not in_table:
            if stripped.startswith("|") and "Skill" in stripped and "Role" in stripped:
                headers = [h.strip() for h in stripped.strip("|").split("|")]
                if (
                    len(headers) == 4
                    and headers[0] == "Skill"
                    and headers[1] == "Role"
                    and headers[2] == "Activation"
                    and headers[3] == "Modification authority"
                ):
                    in_table = True
            continue

        if not stripped.startswith("|"):
            break

        if re.match(r"^\|\s*[-:]+", stripped):
            continue

        fields = [field.strip() for field in stripped.strip("|").split("|")]
        if len(fields) != 4 or any(not field for field in fields):
            errors.append(f"malformed catalog row: {line}")
            continue

        rows.append(
            {
                "name": fields[0].strip("`").strip(),
                "role": fields[1],
                "activation": fields[2],
                "modification-authority": fields[3],
            }
        )

    return rows, errors


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
) -> tuple[dict[str, dict[str, str]], list[str]]:
    errors: list[str] = []
    actual_names: set[str] = set()
    metadata_by_name: dict[str, dict[str, str]] = {}
    skill_files = sorted(skills_dir.glob("*/SKILL.md"))

    for path in skill_files:
        try:
            metadata = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        expected = path.parent.name
        name = metadata.get("name")
        if name != expected:
            errors.append(
                f"{path.relative_to(root)}: name={name!r}, expected {expected!r}"
            )
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(root)}: missing description")
        for field in ("role", "activation", "modification-authority"):
            if not metadata.get(field):
                errors.append(f"{path.relative_to(root)}: missing {field}")
        if name:
            if name in actual_names:
                errors.append(f"duplicate skill name: {name}")
            actual_names.add(name)
            metadata_by_name[name] = metadata

    return metadata_by_name, errors


def check_catalog_parity(
    catalog_path: Path, metadata_by_name: dict[str, dict[str, str]]
) -> list[str]:
    errors: list[str] = []
    catalog_text = catalog_path.read_text(encoding="utf-8")
    catalog_entries, parse_errors = parse_catalog_table(catalog_text)
    errors.extend(parse_errors)

    listed_names = [row["name"] for row in catalog_entries]
    listed_counts: dict[str, int] = {}
    for name in listed_names:
        listed_counts[name] = listed_counts.get(name, 0) + 1
    for name, count in sorted(listed_counts.items()):
        if count != 1:
            errors.append(
                f"catalog skill must appear exactly once: {name} ({count} rows)"
            )

    actual_names = set(metadata_by_name.keys())
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

    for term in REQUIRED_CATALOG_TERMS:
        if term not in catalog_text:
            errors.append(f"catalog missing routing/authority term: {term}")

    return errors


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
                f"plan must be .plans/YYYY-MM-DD/<task-name>.md: {path.relative_to(root)}"
            )
            continue
        try:
            date.fromisoformat(relative.parts[0])
        except ValueError:
            errors.append(
                f"plan must use a valid ISO calendar date: {path.relative_to(root)}"
            )
    return errors


def check_safety_guards(agents_path: Path) -> list[str]:
    errors: list[str] = []
    agents_text = agents_path.read_text(encoding="utf-8")
    for term in REQUIRED_SAFETY_GUARDS:
        if term not in agents_text:
            errors.append(f"AGENTS.md missing destructive-command guard: {term}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(check_ascii_markdown(ROOT))

    metadata_by_name, skill_errors = check_skill_frontmatters(SKILLS, ROOT)
    errors.extend(skill_errors)

    if CATALOG.exists():
        errors.extend(check_catalog_parity(CATALOG, metadata_by_name))
    else:
        errors.append(f"catalog file not found: {CATALOG.relative_to(ROOT)}")

    errors.extend(check_plan_paths(PLANS, ROOT))
    errors.extend(check_safety_guards(AGENTS))

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    skill_files = list(SKILLS.glob("*/SKILL.md"))
    print(f"Validated {len(skill_files)} skills and catalog parity.")
    print(
        "Validated ASCII-only Markdown, routing/authority markers, approval, dated plan paths, and destructive-command guards."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
