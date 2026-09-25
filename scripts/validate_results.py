#!/usr/bin/env python
"""Runs the 9 validation checks of results-schema.md §9 against a results directory
(T088). Exit code 1 on any failure.

Usage: python scripts/validate_results.py <results/raw/<experiment>/<suite>> [--cell-audit PATH]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tfo_bench import records


def validate_directory(directory: Path, cell_audit_path: Path | None) -> list[str]:
    issues: list[str] = []
    runs_path = directory / "runs.csv"
    if not runs_path.exists():
        return [f"{runs_path}: not found"]

    issues += records.validate_runs_csv(runs_path)  # checks 1, 2, 3, 4 (evals_internal), 5, 6
    issues += records.validate_identifiers_csv(runs_path)  # check 9

    curves_path = directory / "curves.csv"
    if curves_path.exists():
        issues += records.validate_curves_csv(runs_path, curves_path)  # check 7

    mech_path = directory / "mechanism_evals.csv"
    if mech_path.exists():
        issues += records.validate_mechanism_evals_csv(runs_path, mech_path)  # check 4 (per-tag)

    if cell_audit_path is not None and cell_audit_path.exists():
        issues += records.validate_audit_dispositions(runs_path, cell_audit_path)  # check 8

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--cell-audit", type=Path, default=Path("results/audit/cell_audit.csv"))
    args = parser.parse_args()

    issues = validate_directory(args.directory, args.cell_audit)
    if issues:
        print(f"FAIL: {len(issues)} issue(s) in {args.directory}:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    print(f"OK: {args.directory} passes all applicable checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
