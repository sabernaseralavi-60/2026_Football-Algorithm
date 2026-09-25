#!/usr/bin/env python
"""The throughput pilot (T102; research.md R5).

Measures per-evaluation cost (objective plus algorithm overhead) for every roster algorithm on
(a subset of) the tuning set, projects the programme's total core-hours from the budgets declared
in `config/protocol.toml`, and applies the pre-committed {1/2, 1/4} reduction only if that
projection exceeds the declared compute envelope.

This measurement itself is cheap (a few hundred evaluations per algorithm) and is what this
implementation pass actually runs; the resulting *projection* is a planning number for whoever
runs the real programme, not a claim this pass makes about the full suites (which it does not run
-- research.md R5's own "not estimated" rule applies to the manuscript, not to this pre-flight
sizing step, and the pilot's whole purpose is to replace a hand-estimate with a measurement).
"""

from __future__ import annotations

import argparse
import json
import time
import tomllib
from pathlib import Path

import numpy as np

from tfo_bench.ledger import CountingObjective
from tfo_bench.problems import tuning as tuning_problems
from tfo_bench.problems.base import ProblemView
from tfo_bench.runner import ALGORITHM_FACTORIES, build_algorithm

REPO_ROOT = Path(__file__).resolve().parent.parent


def measure_cost_per_eval(algorithm: str, problem, budget: int, seed: int) -> float:
    ledger = CountingObjective(problem, budget)
    view = ProblemView(ledger, problem, "pilot")
    adapter = build_algorithm(algorithm, "default")
    t0 = time.perf_counter()
    adapter.run(view, budget, seed)
    elapsed = time.perf_counter() - t0
    return elapsed / max(1, ledger.evals_used)


def total_planned_evaluations(protocol: dict) -> int:
    budgets = protocol["budgets"]
    n_runs = budgets["n_runs"]
    n_algorithms = len(protocol["roster"]["algorithms"])

    # CEC-2017: 29 functions at D=30.
    cec2017_evals = 29 * budgets["cec2017"]["d30"] * n_runs * n_algorithms
    # CEC-2022: 12 functions at each of D=10, D=20.
    cec2022_evals = 12 * (budgets["cec2022"]["d10"] + budgets["cec2022"]["d20"]) * n_runs * n_algorithms
    # Engineering: 7 named problems, each with its own budget.
    engineering_evals = sum(budgets["engineering"].values()) * n_runs * n_algorithms

    return cec2017_evals + cec2022_evals + engineering_evals


def project_core_hours(total_evals: int, mean_cost_per_eval_s: float) -> float:
    return total_evals * mean_cost_per_eval_s / 3600.0


def choose_reduction(projected_core_hours: float, envelope_core_hours: float, multipliers: list[float]) -> float:
    """"Only one reduced multiplier per suite may be used, taken from the pre-committed list
    {1/2, 1/4}" (research.md R5): the largest (least aggressive) multiplier that brings the
    projection within the envelope, or 1.0 (no reduction) if it already fits."""
    if projected_core_hours <= envelope_core_hours:
        return 1.0
    for m in sorted(multipliers, reverse=True):
        if projected_core_hours * m <= envelope_core_hours:
            return m
    return min(multipliers)  # even the most aggressive pre-committed reduction is applied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default=str(REPO_ROOT / "config" / "protocol.toml"))
    parser.add_argument("--budget", type=int, default=300, help="smoke-scale measurement budget")
    parser.add_argument("--dim", type=int, default=15, choices=[15, 40])
    parser.add_argument("--out", default=str(REPO_ROOT / "results" / "raw" / "pilot" / "pilot_report.json"))
    args = parser.parse_args()

    with open(args.protocol, "rb") as fh:
        protocol = tomllib.load(fh)

    problem = tuning_problems.build_problems(args.dim)["Sphere"]
    algorithms = protocol["roster"]["algorithms"]

    costs = {}
    for algorithm in algorithms:
        seed = 12345
        cost = measure_cost_per_eval(algorithm, problem, args.budget, seed)
        costs[algorithm] = cost
        print(f"{algorithm}: {cost * 1e6:.2f} us/eval (measured, D={args.dim})")

    mean_cost = float(np.mean(list(costs.values())))
    total_evals = total_planned_evaluations(protocol)
    projected = project_core_hours(total_evals, mean_cost)
    envelope = protocol["compute_envelope"]["envelope_core_hours"]
    multipliers = protocol["compute_envelope"]["allowed_reduction_multipliers"]
    reduction = choose_reduction(projected, envelope, multipliers)

    report = {
        "measured_cost_per_eval_s": costs,
        "mean_cost_per_eval_s": mean_cost,
        "total_planned_evaluations": total_evals,
        "projected_core_hours_at_full_budget": projected,
        "envelope_core_hours": envelope,
        "chosen_reduction_multiplier": reduction,
        "measurement_note": (
            f"Costs measured on tuning/Sphere at D={args.dim}, budget={args.budget}; this is a "
            "sizing measurement, not a benchmark result."
        ),
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))

    print(f"\nProjected: {projected:.1f} core-hours vs envelope {envelope} core-hours")
    print(f"Chosen reduction multiplier: {reduction} (1.0 = no reduction)")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
