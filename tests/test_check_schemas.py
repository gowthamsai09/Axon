from __future__ import annotations

import json
import shutil
from pathlib import Path

from scripts.check_schemas import EXPECTED, check, find_slug_enums, main

SCHEMAS = Path(__file__).resolve().parent.parent / "schemas"


def test_committed_schemas_pass() -> None:
    assert check(SCHEMAS) == []
    assert main(["x", str(SCHEMAS)]) == 0


def test_missing_file_reported(tmp_path: Path) -> None:
    shutil.copytree(SCHEMAS, tmp_path / "s")
    (tmp_path / "s" / "summary.schema.json").unlink()
    assert any("missing schema" in p for p in check(tmp_path / "s"))


def test_slug_enum_drift_reported(tmp_path: Path) -> None:
    d = tmp_path / "s"
    shutil.copytree(SCHEMAS, d)
    f = d / "profile.schema.json"
    doc = json.loads(f.read_text())

    def drop(node: object) -> None:
        if isinstance(node, dict):
            e = node.get("enum")
            if isinstance(e, list) and "robotics" in e:
                e.remove("robotics")
            for v in node.values():
                drop(v)
        elif isinstance(node, list):
            for v in node:
                drop(v)

    drop(doc)
    f.write_text(json.dumps(doc))
    assert any("differs" in p for p in check(d))


def test_bad_json_and_missing_id(tmp_path: Path) -> None:
    for name in EXPECTED:
        (tmp_path / f"{name}.schema.json").write_text("{}")
    (tmp_path / "summary.schema.json").write_text("{nope")
    problems = check(tmp_path)
    assert any("invalid JSON" in p for p in problems)
    assert any("missing $schema" in p for p in problems)


def test_find_slug_enums() -> None:
    assert find_slug_enums({"a": {"enum": ["llm-releases", "rag"]}, "b": [{"enum": ["x"]}]})
