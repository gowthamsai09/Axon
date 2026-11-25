"""The hostile-text corpus (onboarding, feedback, chat) is well formed and equals its generator."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.make_text_corpus import main as generate

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "corpus" / "hostile-text"
NAMES = ("onboarding", "feedback", "chat")


def load(name: str) -> list[dict[str, Any]]:
    data = json.loads((DIR / f"{name}.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_committed_files_equal_the_generator(tmp_path: Path) -> None:
    assert generate(["--out", str(tmp_path)]) == 0
    fresh = {p.name: p.read_bytes() for p in tmp_path.glob("*.json")}
    assert fresh == {p.name: p.read_bytes() for p in DIR.glob("*.json")}
    assert sorted(fresh) == [f"{n}.json" for n in sorted(NAMES)]


@pytest.mark.parametrize("name", NAMES)
def test_ids_are_unique_and_counts_are_real(name: str) -> None:
    cases = load(name)
    ids = [c["id"] for c in cases]
    assert len(set(ids)) == len(ids) and len(cases) >= 18


def test_onboarding_cases_state_an_outcome_and_a_unique_marker() -> None:
    cases = load("onboarding")
    assert {c["expect"] for c in cases} == {"accepted", "rejected"}
    markers = [c["marker"] for c in cases]
    assert len(set(markers)) == len(markers) and all(len(m) >= 8 for m in markers)
    assert sum(c["expect"] == "accepted" for c in cases) >= 8


def test_feedback_cases_cover_counted_and_ignored() -> None:
    cases = load("feedback")
    assert {c["expect"] for c in cases} == {"counted", "ignored"}
    assert all(isinstance(c["issue"], dict) for c in cases)


def test_chat_cases_name_what_must_not_appear() -> None:
    cases = load("chat")
    assert any(c["slack_forbidden"] for c in cases) and any(c["telegram_forbidden"] for c in cases)
    for c in cases:
        assert isinstance(c["text"], str) and c["text"]
        for needle in (*c["slack_forbidden"], *c["telegram_forbidden"]):
            assert needle in html.unescape(c["text"])


def test_files_are_ascii_json() -> None:
    for path in DIR.glob("*.json"):
        path.read_bytes().decode("ascii")
