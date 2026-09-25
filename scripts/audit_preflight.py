#!/usr/bin/env python
"""Runs the preflight stage of `tfo_bench.audit` for each suite and writes
`results/audit/cell_audit.csv`, one row per cell (T094; data-model.md B4).

This only evaluates every cell's `Problem` once, at its claimed optimum -- it never runs any of
the 9 roster algorithms, so it is cheap enough to actually execute (unlike the real benchmark
programme, which this project's scope explicitly defers).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from tfo_bench.audit import audit_preflight_stage
from tfo_bench.problems import cec2017, cec2022, engineering, tuning

CELL_AUDIT_COLUMNS = [
    "cell_id",
    "implementation",
    "f_star",
    "f_at_xstar",
    "preflight_abs_err",
    "preflight_pass",
    "min_best_f_all_runs",
    "below_optimum_pass",
    "cross_ref_implementation",
    "cross_ref_preflight_pass",
    "cross_ref_below_optimum_pass",
    "disposition",
    "evidence_path",
    "pre_audit_numbers_path",
]

#: research.md R12 item 6's composition-singularity backoff (see audit.py's `run_preflight`
#: docstring for why a literal 1e-6 offset alone does not suffice for every CEC-2017 composition
#: function at this implementation's numeric precision).
_COMPOSITION_BACKOFF = [1e-6, 1e-8, 1e-10, 1e-12, 1e-14]


def _iter_all_cells():
    for n in cec2017.OFFICIAL_NUMBERS:
        fid = cec2017.function_id(n)
        problem = cec2017.build_problems(D=30)[fid]
        backoff = _COMPOSITION_BACKOFF if cec2017.is_composition(n) else None
        yield "cec2017", problem, backoff

    for D in cec2022.SUPPORTED_DIMS:
        for fid, problem in cec2022.build_problems(D).items():
            yield "cec2022", problem, None

    for name, problem in engineering.build_problems().items():
        # engineering has no x_star field populated (audit.py's variant handling uses f_ref only
        # for orientation, per data-model.md B4's "engineering variant" note); skip x*-based
        # preflight here and let the runner's post-hoc feasibility check (research.md R10) cover
        # feasibility instead.
        yield "engineering", problem, "skip"

    for D in tuning.DIMS:
        for name, problem in tuning.build_problems(D).items():
            yield "tuning", problem, None
    for name, problem in tuning.build_constrained_problems().items():
        yield "tuning", problem, None


def run(out_path: Path) -> list[dict]:
    rows = []
    for suite, problem, backoff in _iter_all_cells():
        if backoff == "skip":
            continue
        audit = audit_preflight_stage(problem, problem.problem_id, composition_epsilon_backoff=backoff)
        rows.append(audit.to_dict())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CELL_AUDIT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="results/audit/cell_audit.csv")
    args = parser.parse_args()

    rows = run(Path(args.out))
    n_pass = sum(1 for r in rows if r["preflight_pass"])
    print(f"{len(rows)} cells checked, {n_pass} passed preflight, wrote {args.out}")
    failing = [r["cell_id"] for r in rows if not r["preflight_pass"]]
    if failing:
        print(f"cells requiring cross-validation: {failing}")


if __name__ == "__main__":
    main()
