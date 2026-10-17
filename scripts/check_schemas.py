"""Hub CI: every exported schema exists and parses, and all topic-slug enums agree.

Run: python scripts/check_schemas.py [schemas_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

EXPECTED = (
    "feed-item",
    "summary",
    "sources",
    "taxonomy",
    "authority",
    "profile",
    "task-result",
)
SLUG_FILES = ("feed-item", "summary", "profile", "task-result", "sources")  # must embed the enum
MARKER = "llm-releases"


def find_slug_enums(node: Any, path: str = "") -> list[tuple[str, frozenset[str]]]:
    """All `enum` lists that look like topic-slug lists (contain the marker slug)."""
    found: list[tuple[str, frozenset[str]]] = []
    if isinstance(node, dict):
        enum = node.get("enum")
        if isinstance(enum, list) and MARKER in enum:
            found.append((path or "/", frozenset(str(x) for x in enum)))
        for k, v in node.items():
            found += find_slug_enums(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            found += find_slug_enums(v, f"{path}/{i}")
    return found


def check(schema_dir: Path) -> list[str]:
    problems: list[str] = []
    reference: frozenset[str] | None = None
    for name in EXPECTED:
        p = schema_dir / f"{name}.schema.json"
        if not p.exists():
            problems.append(f"missing schema: {p.name}")
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"{p.name}: invalid JSON ({exc})")
            continue
        if "$schema" not in doc or "$id" not in doc:
            problems.append(f"{p.name}: missing $schema or $id")
        enums = find_slug_enums(doc)
        if name in SLUG_FILES and not enums:
            problems.append(f"{p.name}: no topic-slug enum found")
        for where, values in enums:
            if reference is None:
                reference = values
            elif values != reference:
                diff = sorted(values ^ reference)
                problems.append(f"{p.name} {where}: slug enum differs from others by {diff}")
    if reference is not None and len(reference) != 16:
        problems.append(f"expected 16 topic slugs, found {len(reference)}")
    return problems


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent / "schemas"
    problems = check(root)
    for p in problems:
        print(f"ERROR {p}", file=sys.stderr)
    print("schemas OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
