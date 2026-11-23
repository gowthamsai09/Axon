"""Check or apply pinned third-party actions. Offline: the table below is the source of truth.

python scripts/pin_actions.py --check DIR [DIR ...]   exit 1 on any unpinned or mismatched line
python scripts/pin_actions.py --apply DIR [DIR ...]   rewrite `uses:` lines to the table
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PINS: dict[str, tuple[str, str]] = {
    "actions/checkout": ("v6.1.0", "d23441a48e516b6c34aea4fa41551a30e30af803"),
    "actions/setup-python": ("v6.3.0", "ece7cb06caefa5fff74198d8649806c4678c61a1"),
    "actions/setup-node": ("v6.5.0", "249970729cb0ef3589644e2896645e5dc5ba9c38"),
}
USES = re.compile(r"^(?P<lead>\s*-?\s*uses:\s*)(?P<name>[\w./-]+)@(?P<ref>\S+)(?P<tail>.*)$")


def process(path: Path, apply: bool) -> list[str]:
    problems: list[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        m = USES.match(line)
        if m is None or m["name"].startswith("./"):
            continue
        pin = PINS.get(m["name"])
        if pin is None:
            problems.append(f"{path}:{i + 1}: no pin known for {m['name']}")
            continue
        if m["ref"] != pin[1]:
            problems.append(f"{path}:{i + 1}: {m['name']}@{m['ref'][:12]} is not the pinned SHA")
            if apply:
                lines[i] = f"{m['lead']}{m['name']}@{pin[1]}  # {pin[0]}"
    if apply and problems:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    ap.add_argument("dirs", nargs="+", type=Path)
    args = ap.parse_args(argv)
    problems: list[str] = []
    for d in args.dirs:
        for f in sorted(d.glob("*.yml")):
            problems += process(f, args.apply)
    for p in problems:
        print(p, file=sys.stderr)
    print(f"{len(problems)} problem(s)" + (" (fixed)" if args.apply and problems else ""))
    return 1 if problems and args.check else 0


if __name__ == "__main__":
    sys.exit(main())
