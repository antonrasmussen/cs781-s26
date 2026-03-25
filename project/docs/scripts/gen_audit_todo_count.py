#!/usr/bin/env python3
"""Scan ``src/reliability_eval`` for TODO and NotImplementedError markers.

Run from the project root::

    python docs/scripts/gen_audit_todo_count.py

Use ``--write`` to refresh ``docs/generated/audit_marker_count.txt`` (git may
ignore or commit, per team policy).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "reliability_eval"
OUT = Path(__file__).resolve().parents[1] / "generated" / "audit_marker_count.txt"

TODO_RE = re.compile(r"\bTODO\b")
NOTIMPL_RE = re.compile(r"\bNotImplementedError\b")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help=f"Write summary to {OUT.relative_to(ROOT)}",
    )
    args = parser.parse_args()

    todo_hits = 0
    notimpl_hits = 0
    py_files = sorted(SRC.rglob("*.py"))
    for path in py_files:
        text = path.read_text(encoding="utf-8")
        todo_hits += len(TODO_RE.findall(text))
        notimpl_hits += len(NOTIMPL_RE.findall(text))

    lines = [
        f"TODO matches: {todo_hits}",
        f"NotImplementedError matches: {notimpl_hits}",
        f"Python files scanned: {len(py_files)}",
        "",
    ]
    report = "\n".join(lines)
    print(report, end="")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(report, encoding="utf-8")
        print(f"Wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
