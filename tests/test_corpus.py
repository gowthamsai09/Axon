"""The shared corpora are well formed and equal what the generators produce."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.make_injection_corpus import main as generate
from scripts.make_ssrf_corpus import main as generate_ssrf

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus" / "injection"
SSRF = ROOT / "corpus" / "ssrf" / "urls.json"
OUTCOMES = {"sanitized", "contained", "truncated", "rejected", "accepted"}


def load() -> list[dict[str, object]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(CORPUS.glob("*.json"))]


def test_counts_and_ids() -> None:
    cases = load()
    kinds = [c["kind"] for c in cases]
    assert kinds.count("document") >= 30 and kinds.count("output") >= 6 and "base" in kinds
    ids = [str(c["id"]) for c in cases]
    assert len(set(ids)) == len(ids)
    assert sorted(p.stem for p in CORPUS.glob("*.json")) == sorted(ids)


def test_every_case_states_a_valid_outcome() -> None:
    for c in load():
        if c["kind"] == "base":
            continue
        expect = c["expect"]
        assert isinstance(expect, dict) and expect["outcome"] in OUTCOMES, c["id"]
        if c["kind"] == "output":
            assert expect["outcome"] in {"rejected", "accepted"}
            assert (expect["outcome"] == "accepted") or expect["reason"], c["id"]
        else:
            assert expect["outcome"] in {"sanitized", "contained", "truncated"}


def test_committed_files_equal_the_generator(tmp_path: Path) -> None:
    assert generate(["--out", str(tmp_path)]) == 0
    fresh = {p.name: p.read_bytes() for p in tmp_path.glob("*.json")}
    assert fresh == {p.name: p.read_bytes() for p in CORPUS.glob("*.json")}


def test_ssrf_corpus_is_well_formed() -> None:
    cases = json.loads(SSRF.read_text(encoding="utf-8"))
    ids = [c["id"] for c in cases]
    assert len(cases) >= 80 and len(set(ids)) == len(ids)
    assert {c["expect"] for c in cases} == {"allowed", "blocked"}
    categories = {c["category"] for c in cases}
    assert {"scheme", "ipv4", "ipv6", "numeric-host", "userinfo", "port", "dns", "allowed"} <= categories
    for c in cases:
        assert set(c) == {"id", "url", "expect", "category", "dns"}
        assert all(isinstance(v, list) and v for v in c["dns"].values())


def test_every_numeric_host_case_resolves_to_a_public_address() -> None:
    """They must be refused whatever DNS says, so DNS is made to say 'public'."""
    for c in json.loads(SSRF.read_text(encoding="utf-8")):
        if c["category"] == "numeric-host":
            assert c["dns"] and all(v == ["93.184.216.34"] for v in c["dns"].values()), c["id"]


def test_ssrf_file_equals_the_generator(tmp_path: Path) -> None:
    assert generate_ssrf(["--out", str(tmp_path)]) == 0
    assert (tmp_path / "urls.json").read_bytes() == SSRF.read_bytes()
