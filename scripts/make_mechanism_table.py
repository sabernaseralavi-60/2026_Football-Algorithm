#!/usr/bin/env python3
"""Renders the operator-family table (all 19 mechanisms, family, canonical citation) directly from
`src/tfo/registry.py`, so the manuscript table cannot drift from the code (FR-042, SC-001).

tasks.md T109 (User Story 1).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tfo.registry import all_mechanisms  # noqa: E402


def render_table() -> str:
    lines = [
        "| # | Mechanism | Module | Operator family | Canonical citation(s) | FR |",
        "|---|---|---|---|---|---|",
    ]
    for idx, entry in enumerate(all_mechanisms(), start=1):
        citations = "; ".join(entry.citations)
        lines.append(
            f"| {idx} | {entry.display_name} | `{entry.module}` | {entry.family} | "
            f"{citations} | {entry.fr} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(render_table())
