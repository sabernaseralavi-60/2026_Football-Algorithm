#!/usr/bin/env python3
"""Computes the CA overlap audit from `registry.py` against mechanism-map.md's overlap table:
"At least half of TFO's mechanisms belong to operator families absent from CA's operator-family
table (11 of 19 at design time)" (SC-002).

tasks.md T111 (User Story 1). `--post-ablation` re-reports the ratio after removing the named
mechanisms (a post-hoc, separately labelled table per plan.md's Complexity Tracking row 2), so a
pruned variant's overlap ratio can be reported without touching the design-time count above.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tfo.registry import REGISTRY, MechanismTag, all_mechanisms, ca_absent_count  # noqa: E402


def overlap_report(removed: frozenset[MechanismTag] = frozenset()) -> dict:
    kept = [entry for entry in all_mechanisms() if entry.tag not in removed]
    absent = sum(1 for entry in kept if entry.overlaps_ca == "no")
    total = len(kept)
    return {
        "total": total,
        "absent_from_ca": absent,
        "ratio": absent / total if total else 0.0,
        "at_least_half": absent * 2 >= total,
    }


def render_report(report: dict, label: str) -> str:
    return (
        f"{label}: {report['absent_from_ca']} of {report['total']} mechanisms "
        f"({report['ratio']:.1%}) belong to operator families absent from CA's operator-family "
        f"table. At-least-half claim holds: {report['at_least_half']}."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--post-ablation",
        metavar="TAG,TAG,...",
        default=None,
        help="Comma-separated mechanism tags removed after ablation; re-reports the ratio among "
        "the remaining mechanisms, in a separately labelled post-hoc table (never overwriting the "
        "design-time count).",
    )
    args = parser.parse_args(argv)

    design_time = overlap_report()
    print(render_report(design_time, "Design-time"))
    assert design_time["absent_from_ca"] == 11 and design_time["total"] == 19, (
        "SC-002 reference figure (11 of 19) must match the registry"
    )

    if args.post_ablation is not None:
        removed = frozenset(MechanismTag(t.strip()) for t in args.post_ablation.split(",") if t.strip())
        post = overlap_report(removed)
        print(render_report(post, "Post-ablation (separately labelled, post-hoc)"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
