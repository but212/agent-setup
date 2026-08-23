#!/usr/bin/env python3
"""Validate the skill catalog, skill metadata, and core safety contracts."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CATALOG = ROOT / "spec" / "skills-spec.md"
AGENTS = ROOT / "AGENTS.md"


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
            values[match.group(1)] = match.group(2).strip().strip('"')
    return values


def catalog_names(text: str) -> set[str]:
    section = text.split("## 3. Routing and Handoffs", 1)[0]
    table = section.split("## 2. Skill Catalog", 1)[-1]
    return {
        match.group(1)
        for line in table.splitlines()
        if (match := re.match(r"\|\s*`([^`]+)`\s*\|", line))
    }


def main() -> int:
    errors: list[str] = []
    skill_files = sorted(SKILLS.glob("*/SKILL.md"))
    actual_names: set[str] = set()

    for path in skill_files:
        try:
            metadata = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
            continue
        expected = path.parent.name
        name = metadata.get("name")
        if name != expected:
            errors.append(f"{path.relative_to(ROOT)}: name={name!r}, expected {expected!r}")
        if not metadata.get("description"):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
        if name:
            if name in actual_names:
                errors.append(f"duplicate skill name: {name}")
            actual_names.add(name)

    catalog_text = CATALOG.read_text(encoding="utf-8")
    listed_names = catalog_names(catalog_text)
    for name in sorted(actual_names - listed_names):
        errors.append(f"catalog missing skill: {name}")
    for name in sorted(listed_names - actual_names):
        errors.append(f"catalog lists absent skill: {name}")

    required_catalog_terms = ("Activation", "Modification authority", "exactly one", "user approval")
    for term in required_catalog_terms:
        if term not in catalog_text:
            errors.append(f"catalog missing routing/authority term: {term}")

    agents_text = AGENTS.read_text(encoding="utf-8")
    for term in ("git push", "git reset --hard", "git clean -f", "rm -rf"):
        if term not in agents_text:
            errors.append(f"AGENTS.md missing destructive-command guard: {term}")

    if errors:
        print("Skill validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"Validated {len(skill_files)} skills and catalog parity.")
    print("Validated routing, authority, approval, and destructive-command guards.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
