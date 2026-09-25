#!/usr/bin/env python
"""The thin CLI shared by every suite run (T108): `--smoke`, `--part i/n`, `--suite`,
`--functions`, `--algorithms`, `--runs`, `--out` -- enumerating `ExperimentJob`s through
`runner.py`.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

from tfo_bench import records, runner
from tfo_bench.problems import cec2017, cec2022, engineering, tuning

REPO_ROOT = Path(__file__).resolve().parent.parent

_ALL_FUNCTION_IDS = {
    "cec2017": lambda dim: [cec2017.function_id(n) for n in cec2017.OFFICIAL_NUMBERS],
    "cec2022": lambda dim: [cec2022.function_id(n) for n in cec2022.NUMBERS],
    "engineering": lambda dim: list(engineering.SPECS),
    "tuning": lambda dim: list(tuning.build_problems(dim)),
}

_DEFAULT_DIM = {"cec2017": 30, "cec2022": 10, "engineering": None, "tuning": 15}


def _partition(items: list, part_spec: str) -> list:
    i, n = (int(x) for x in part_spec.split("/"))
    if not (1 <= i <= n):
        raise ValueError(f"--part must be 'i/n' with 1 <= i <= n, got {part_spec!r}")
    return [x for idx, x in enumerate(items) if idx % n == (i - 1)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, choices=["cec2017", "cec2022", "engineering", "tuning"])
    parser.add_argument("--dim", type=int, default=None)
    parser.add_argument("--experiment", default="main")
    parser.add_argument("--functions", nargs="*", default=None, help="subset of function ids; default: all")
    parser.add_argument(
        "--algorithms", nargs="*", default=list(runner.ALGORITHM_FACTORIES), help="roster subset"
    )
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--budget", type=int, default=None, help="override; default: protocol.toml's")
    parser.add_argument("--out", default=str(REPO_ROOT / "results" / "raw"))
    parser.add_argument("--smoke", action="store_true", help="tiny budget/run-count smoke run")
    parser.add_argument("--part", default=None, help="'i/n': only this 1-indexed slice of functions")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--protocol", default=str(REPO_ROOT / "config" / "protocol.toml"))
    parser.add_argument("--master-seed", type=int, default=None)
    args = parser.parse_args()

    experiment = "smoke" if args.smoke else args.experiment
    dim = args.dim if args.dim is not None else _DEFAULT_DIM[args.suite]

    function_ids = args.functions or _ALL_FUNCTION_IDS[args.suite](dim)
    if args.part:
        function_ids = _partition(function_ids, args.part)

    with open(args.protocol, "rb") as fh:
        protocol = tomllib.load(fh)
    master_seed = args.master_seed if args.master_seed is not None else protocol["seeds"]["master_seed"]

    if args.smoke:
        n_runs, budget = min(args.runs, 2), (args.budget or 200)
        out_root = Path(args.out) / "_smoke"  # results-schema.md §1: never read by tuning/analysis
    else:
        n_runs = args.runs
        budget = args.budget or _protocol_budget(protocol, args.suite, dim, function_ids)
        out_root = Path(args.out)
        runner.check_roster_includes_tfo_static_with_tfo(args.algorithms)
        for algorithm in args.algorithms:
            runner.check_preregistered(experiment, runner.get_git_tags(REPO_ROOT))

    jobs = runner.enumerate_jobs(
        experiment=experiment,
        suite=args.suite,
        function_ids=function_ids,
        dim=dim or 0,
        algorithms=args.algorithms,
        n_runs=n_runs,
        budget=budget,
        master_seed=master_seed,
    )
    print(f"Enumerated {len(jobs)} jobs ({args.suite}, experiment={experiment}, dim={dim}, "
          f"{len(function_ids)} functions x {len(args.algorithms)} algorithms x {n_runs} runs)")

    writer = records.ResultsWriter(out_root, experiment, args.suite)
    n_ran = runner.run_experiment(jobs, writer, n_workers=args.workers)
    print(f"Ran {n_ran} new jobs (resumed/skipped {len(jobs) - n_ran} already-completed ones)")
    print(f"Results in {writer.dir}")
    return 0


def _protocol_budget(protocol: dict, suite: str, dim, function_ids: list[str]) -> int:
    budgets = protocol["budgets"]
    if suite == "cec2017":
        return budgets["cec2017"][f"d{dim}"]
    if suite == "cec2022":
        return budgets["cec2022"][f"d{dim}"]
    if suite == "engineering":
        # one budget per named problem; require a single function_id when not overridden
        if len(function_ids) != 1:
            raise ValueError("engineering suite: pass exactly one --functions id, or --budget explicitly")
        return budgets["engineering"][function_ids[0]]
    raise ValueError(f"no protocol budget rule for suite {suite!r} (tuning has none; pass --budget)")


if __name__ == "__main__":
    sys.exit(main())
