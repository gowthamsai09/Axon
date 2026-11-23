"""The hub holds the canonical prompts (Appendix C 82): equal to their id file and the spec."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.prompt_id import main, normalised, prompt_id

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
SPEC = (ROOT / "docs" / "axon-architecture.md").read_text(encoding="utf-8").replace("\r\n", "\n")


def spec_block(heading: str) -> str:
    """The first ```text block after the heading that starts with `heading`."""
    start = SPEC.index(f"### {heading}")
    m = re.search(r"```text\n(.*?)\n```", SPEC[start:], re.DOTALL)
    assert m is not None, heading
    return m.group(1)


def test_version_file_is_the_hash_of_the_summarizer_prompt() -> None:
    text = normalised(PROMPTS / "summarizer_system.txt")
    version = (PROMPTS / "summarizer_system.version").read_text(encoding="utf-8").strip()
    assert version == prompt_id(text)
    assert re.fullmatch(r"p-[0-9a-f]{10}", version)


def test_summarizer_prompt_equals_spec_13_1() -> None:
    assert normalised(PROMPTS / "summarizer_system.txt").rstrip("\n") == spec_block("13.1 ")


def test_onboarding_prompt_equals_spec_13_2() -> None:
    assert normalised(PROMPTS / "onboarding_system.txt").rstrip("\n") == spec_block("13.2 ")


def test_prompts_are_fence_free_and_lf() -> None:
    for name in ("summarizer_system.txt", "onboarding_system.txt"):
        raw = (PROMPTS / name).read_bytes()
        assert b"\r" not in raw and b"```" not in raw and raw.endswith(b"\n")


def test_any_edit_changes_the_id() -> None:
    text = normalised(PROMPTS / "summarizer_system.txt")
    assert prompt_id(text + " ") != prompt_id(text)
    assert prompt_id(text.replace("DATA", "data", 1)) != prompt_id(text)


def test_cli_prints_the_id(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["prompt_id.py", str(PROMPTS / "summarizer_system.txt")]) == 0
    printed = capsys.readouterr().out.strip()
    assert printed == (PROMPTS / "summarizer_system.version").read_text(encoding="utf-8").strip()
    assert main(["prompt_id.py"]) == 2
