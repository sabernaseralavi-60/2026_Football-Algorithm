#!/usr/bin/env python
"""Reports two result directories as bit-identical in `runs.csv` and `curves.csv`, ignoring
timing columns (T107; research.md R20)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tfo_bench.records import CURVE_COLUMNS, RUNS_COLUMNS, read_csv_rows

#: Timing columns are expected to differ between reproductions (wall-clock varies by machine/
#: load) and are excluded from the bit-identical comparison (research.md R20).
_TIMING_COLUMNS = {"wall_time_s", "objective_time_s"}


def _compare_csv(path_a: Path, path_b: Path, columns: list[str]) -> list[str]:
    issues = []
    rows_a = {r["run_key"]: r for r in read_csv_rows(path_a)}
    rows_b = {r["run_key"]: r for r in read_csv_rows(path_b)}

    if set(rows_a) != set(rows_b):
        only_a = set(rows_a) - set(rows_b)
        only_b = set(rows_b) - set(rows_a)
        if only_a:
            issues.append(f"{path_a}: run_keys not in {path_b}: {sorted(only_a)[:5]}")
        if only_b:
            issues.append(f"{path_b}: run_keys not in {path_a}: {sorted(only_b)[:5]}")

    compare_columns = [c for c in columns if c not in _TIMING_COLUMNS]
    for run_key in sorted(set(rows_a) & set(rows_b)):
        a, b = rows_a[run_key], rows_b[run_key]
        for col in compare_columns:
            if a.get(col) != b.get(col):
                issues.append(f"{run_key}: column {col!r} differs: {a.get(col)!r} != {b.get(col)!r}")
    return issues


def compare_directories(dir_a: Path, dir_b: Path) -> list[str]:
    issues = []
    runs_a, runs_b = dir_a / "runs.csv", dir_b / "runs.csv"
    if runs_a.exists() and runs_b.exists():
        issues += _compare_csv(runs_a, runs_b, RUNS_COLUMNS)
    else:
        issues.append(f"runs.csv missing in {dir_a} or {dir_b}")

    curves_a, curves_b = dir_a / "curves.csv", dir_b / "curves.csv"
    if curves_a.exists() and curves_b.exists():
        issues += _compare_csv(curves_a, curves_b, CURVE_COLUMNS)

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir_a", type=Path)
    parser.add_argument("dir_b", type=Path)
    args = parser.parse_args()

    issues = compare_directories(args.dir_a, args.dir_b)
    if issues:
        print(f"DIFFER: {len(issues)} issue(s) between {args.dir_a} and {args.dir_b}:")
        for issue in issues[:50]:
            print(f"  - {issue}")
        return 1
    print(f"IDENTICAL: {args.dir_a} and {args.dir_b} match in runs.csv/curves.csv (timing excluded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
