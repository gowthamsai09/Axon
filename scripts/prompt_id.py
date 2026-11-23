"""Prompt id helpers shared by the hub tests and the code repos' CI (spec 4.4, Appendix C 82).

python scripts/prompt_id.py FILE    print p-<first 10 hex of sha256> (LF-normalised)
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def normalised(path: Path) -> str:
    """Text as Python's text mode reads it (CRLF becomes LF), which is what the template hashes."""
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


def prompt_id(text: str) -> str:
    return "p-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: prompt_id.py FILE", file=sys.stderr)
        return 2
    print(prompt_id(normalised(Path(argv[1]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
