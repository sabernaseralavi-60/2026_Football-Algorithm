#!/usr/bin/env python3
"""Assembles `docs/reviewer_audit_packet.md`: the operator-family table (T109), the metaphor-free
description (T113), and the CA overlap audit (T111), bundled into the single artefact User Story
1's Independent Test hands to a reader unfamiliar with football (tasks.md T116).
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts"))

from audit_overlap import overlap_report, render_report  # noqa: E402
from make_mechanism_table import render_table  # noqa: E402

_METAPHOR_FREE_DOC = _ROOT / "docs" / "metaphor_free_description.md"
_OUTPUT = _ROOT / "docs" / "reviewer_audit_packet.md"


def build_packet() -> str:
    table = render_table()
    overlap = render_report(overlap_report(), "Design-time")
    metaphor_free = _METAPHOR_FREE_DOC.read_text(encoding="utf-8")

    return f"""# Reviewer Audit Packet: Total Football Optimizer (TFO)

This packet is the single artefact for User Story 1's Independent Test (spec.md): "give only the
mechanism map and the metaphor-free description to a reader unfamiliar with football; they can
state each mechanism's operator family and canonical source, and re-implement the algorithm without
any football term." It bundles three pieces, each generated directly from the code
(`src/tfo/registry.py`) so none of them can drift from the implementation (Principle I):

1. The operator-family table (all 19 mechanisms, family, canonical citation) -- `scripts/make_mechanism_table.py`.
2. The CA overlap audit (SC-002) -- `scripts/audit_overlap.py`.
3. The complete metaphor-free specification -- `docs/metaphor_free_description.md`.

## 1. Operator-family table

Every one of TFO's 19 mechanisms, mapped to a named operator family from the established
metaheuristics literature with at least one canonical citation (FR-042, SC-001).

{table}

## 2. CA overlap audit

{overlap}

Per-mechanism detail is in `mechanism-map.md`'s "Overlap audit against the Chess Algorithm (CA)"
table, which is committed prior art positioning, not code-generated (Principle I, FR-042).

## 3. Metaphor-free specification

The full text of `docs/metaphor_free_description.md` follows verbatim. It contains zero football
vocabulary (enforced by `scripts/check_metaphor_free.py`, tasks.md T114) and is sufficient on its
own to re-implement the algorithm.

---

{metaphor_free}
"""


def main() -> int:
    packet = build_packet()
    _OUTPUT.write_text(packet, encoding="utf-8")
    print(f"wrote {_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
