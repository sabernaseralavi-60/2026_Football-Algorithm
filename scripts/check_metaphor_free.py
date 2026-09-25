#!/usr/bin/env python3
"""Scans `docs/metaphor_free_description.md` against a football-word denylist and fails if any
term appears (tasks.md T114; Principle I, FR-042).

The document's trailing "Appendix: implementation cross-reference" section is excluded from the
scan: it exists only to point maintainers at the (necessarily football-named) source files, is
explicitly marked as not part of the specification, and the specification itself (everything above
that heading) must stand on its own with zero football vocabulary.
"""

from __future__ import annotations

import sys
from pathlib import Path

APPENDIX_HEADING = "## Appendix: implementation cross-reference"

#: Case-insensitive substring denylist (deliberately broad: catches "passing", "offside-line",
#: etc. as well as the bare words tasks.md T114 names).
DENYLIST: tuple[str, ...] = (
    "ball",
    "pitch",
    "keeper",
    "striker",
    "pass",
    "formation",
    "press",
    "offside",
    "substitution",
    "substitute",
    "fixture",
    "tackle",
    "dribble",
    "corner",
    "free kick",
    "referee",
    "goal",
    "match",
    "team",
    "squad",
    "wing-back",
    "wing back",
    "defender",
    "midfielder",
    "forward",
    "coach",
    "manager",
    "tactic",
    "football",
    "soccer",
    "sweeper",
    "counter-attack",
    "counter attack",
    "set piece",
    "set-piece",
    "possession",
    "total football",
    "playmaker",
    "goalkeeper",
    "penalty",
    "kickoff",
    "kick-off",
    "throw-in",
    "throw in",
    "yellow card",
    "red card",
    "var review",
)


def specification_text(doc_path: Path) -> str:
    full_text = doc_path.read_text(encoding="utf-8")
    idx = full_text.find(APPENDIX_HEADING)
    return full_text if idx == -1 else full_text[:idx]


def find_violations(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in DENYLIST if term in lowered]


def main(argv: list[str] | None = None) -> int:
    doc_path = Path(argv[0]) if argv else (
        Path(__file__).resolve().parents[1] / "docs" / "metaphor_free_description.md"
    )
    text = specification_text(doc_path)
    violations = find_violations(text)
    if violations:
        print(f"FAIL: football vocabulary found in {doc_path}: {violations}")
        return 1
    print(f"OK: {doc_path} is metaphor-free.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
