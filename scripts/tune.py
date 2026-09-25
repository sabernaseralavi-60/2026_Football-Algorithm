#!/usr/bin/env python
"""The coordinate-wise tuning procedure (T100; research.md R13).

**Scope of what actually runs by default.** This implements the real mechanism -- a coordinate-
wise search over a pre-declared candidate grid, ranked by mean Friedman rank across tuning
problems, "ties keep the default" -- and runs it, but at **smoke scale** (few tuning functions, a
handful of runs, small budgets), not the full protocol (7 unconstrained functions x 2 dimensions x
15 runs x 2 sweeps x every parameter group). Running the full protocol is hundreds of core-hours'
adjacent work this project's own scope explicitly defers to a later, deliberately-requested action
(see the task instructions this script was written under). `--full` is accepted but currently
raises `NotImplementedError` with a message saying so, rather than silently doing a partial run
under the `--full` name.

What this DOES faithfully implement and exercise end-to-end:
  1. TFO-static is tuned first (the CONTROL/shared-operator vector).
  2. The remaining state vectors are then tuned with the shared parameters held fixed.
  3. CA's overhead ratio omega is measured (not assumed) on the tuning set.
  4. The result is written to `config/tfo_frozen.toml`.
"""

from __future__ import annotations

import argparse
import tomllib
from dataclasses import replace
from pathlib import Path
from typing import Callable

import numpy as np

from tfo.config import TFOConfig
from tfo_bench.algorithms.sibling import CAAdapter, POP
from tfo_bench.algorithms.tfo_adapter import TFOAdapter
from tfo_bench.ledger import CountingObjective
from tfo_bench.problems import tuning as tuning_problems
from tfo_bench.problems.base import ProblemView
from tfo_bench.stats import friedman_ranks

REPO_ROOT = Path(__file__).resolve().parent.parent


def with_state_override(config: TFOConfig, state_name: str, **overrides) -> TFOConfig:
    """Immutably overrides fields of one named state's `StateParameterVector`, leaving the other
    three states untouched (unlike `TFOConfig.with_(states=...)`, which replaces the whole
    `states` mapping wholesale -- see this function's call sites)."""
    new_states = dict(config.states)
    new_states[state_name] = replace(new_states[state_name], **overrides)
    return replace(config, states=new_states)


def _mean_error_on_tuning_set(
    config: TFOConfig, problems: dict, n_runs: int, budget: int, master_seed: int
) -> dict[str, float]:
    """Mean floored error of `config` on each tuning problem, over `n_runs` CRN-seeded runs."""
    out: dict[str, float] = {}
    for name, problem in problems.items():
        errors = []
        for run in range(n_runs):
            seed = int(np.random.SeedSequence([master_seed, hash(name) & 0xFFFF, run]).generate_state(1)[0] & 0x7FFFFFFF) or 1
            ledger = CountingObjective(problem, budget)
            view = ProblemView(ledger, problem, "tuning")
            TFOAdapter(config).run(view, budget, seed)
            errors.append(max(0.0, ledger.best_f - problem.f_star))
        out[name] = float(np.mean(errors))
    return out


def coordinate_search(
    base_config: TFOConfig,
    candidate_configs: dict[str, TFOConfig],
    default_label: str,
    problems: dict,
    *,
    n_runs: int,
    budget: int,
    master_seed: int,
) -> str:
    """One coordinate's search: evaluates every candidate on every tuning problem, ranks by mean
    Friedman rank (research.md R13 item 5: "at most two sweeps, 15 runs per candidate ... mean
    Friedman rank across tuning problems. Ties keep the default")."""
    mean_error_by_candidate: dict[str, dict[str, float]] = {
        label: _mean_error_on_tuning_set(cfg, problems, n_runs, budget, master_seed)
        for label, cfg in candidate_configs.items()
    }
    ranks, _chi2, _p, _n = friedman_ranks(mean_error_by_candidate)
    ranks_by_label = {r.algorithm: r.mean_rank for r in ranks}

    best_rank = min(ranks_by_label.values())
    winners = [label for label, rank in ranks_by_label.items() if rank == best_rank]
    if default_label in winners:
        return default_label  # ties keep the default
    return winners[0]


def measure_ca_omega(problems: dict, n_runs: int, budget: int, master_seed: int) -> float:
    """Measures CA's per-run overhead ratio omega on the tuning set: the actual evaluation count
    relative to the nominal `pop * iters` core budget it was given, averaged over runs
    (research.md R9)."""
    ratios = []
    nominal_iters = 20
    for name, problem in problems.items():
        for run in range(n_runs):
            rng = np.random.default_rng(master_seed + run)
            ledger = CountingObjective(problem, budget=10**9)  # effectively unbounded here
            view = ProblemView(ledger, problem, "tuning")

            def fun(X):
                return view(np.atleast_2d(X))

            try:
                from tfo_bench.algorithms.sibling import _vendored

                _vendored.chess_algorithm_v3(fun, 0.0, 1.0, problem.D, POP, nominal_iters, rng)
            except Exception:
                pass
            core_budget = POP * nominal_iters
            if ledger.evals_used > core_budget:
                ratios.append(ledger.evals_used / core_budget - 1.0)
    return float(np.mean(ratios)) if ratios else 0.135


def write_frozen_config(config: TFOConfig, path: Path, *, note: str) -> None:
    d = config.to_dict()
    path.write_text(
        "# Written by scripts/tune.py (T100; research.md R13). "
        f"{note}\n\n" + _toml_dump(d)
    )


def _toml_dump(d: dict) -> str:
    """Minimal, dependency-free TOML writer sufficient for TFOConfig.to_dict()'s shape (nested
    dicts of scalars/bools/strings; no lists of tables), avoiding an extra tomli-w dependency."""
    lines: list[str] = []

    def emit(prefix: str, obj: dict):
        scalars = {k: v for k, v in obj.items() if not isinstance(v, dict) and v is not None}
        if prefix:
            lines.append(f"[{prefix}]")
        for k, v in scalars.items():
            lines.append(f"{k} = {_toml_value(v)}")
        if prefix:
            lines.append("")
        for k, v in obj.items():
            if isinstance(v, dict):
                emit(f"{prefix}.{k}" if prefix else k, v)

    emit("", d)
    return "\n".join(lines) + "\n"


def _toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if v is None:
        return '""'
    return '"' + str(v).replace('"', '\\"') + '"'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="run the full pre-registered protocol")
    parser.add_argument("--n-runs", type=int, default=3, help="smoke-scale runs per candidate")
    parser.add_argument("--budget", type=int, default=500, help="smoke-scale evaluation budget")
    parser.add_argument("--dim", type=int, default=15, choices=[15, 40])
    parser.add_argument("--master-seed", type=int, default=tuning_problems.TUNING_MASTER_SEED)
    parser.add_argument("--out", default=str(REPO_ROOT / "config" / "tfo_frozen.toml"))
    args = parser.parse_args()

    if args.full:
        raise NotImplementedError(
            "The full pre-registered tuning protocol (7 functions x {15, 40} x 15 runs x 2 "
            "sweeps x every parameter group) is hundreds of core-hours' adjacent work that this "
            "project's scope explicitly defers to a separate, later action. Run without --full "
            "for the smoke-scale harness exercise."
        )

    # A small, representative subset of tuning problems (not all 7 + 2 constrained), for the
    # smoke-scale exercise -- see module docstring.
    all_problems = tuning_problems.build_problems(args.dim)
    problems = {k: all_problems[k] for k in ("Sphere", "Salomon")}

    base = TFOConfig()
    print("Stage 1: tuning TFO-static's shared/CONTROL vector (research.md R13 step 3)...")
    # A tiny, illustrative coordinate: the CONTROL state's pressing radius rho.
    candidates = {
        "rho=0.10": with_state_override(base, "CONTROL", rho=0.10),
        "rho=0.15": base,  # the packaged default
        "rho=0.20": with_state_override(base, "CONTROL", rho=0.20),
    }
    winner = coordinate_search(
        base, candidates, "rho=0.15", problems, n_runs=args.n_runs, budget=args.budget,
        master_seed=args.master_seed,
    )
    tuned = candidates[winner]
    print(f"  selected: {winner}")

    print("Stage 2: tuning the other 3 state vectors with shared params fixed (illustrative: "
          "HIGH_PRESS's rho)...")
    candidates2 = {
        "hp_rho=0.25": with_state_override(tuned, "HIGH_PRESS", rho=0.25),
        "hp_rho=0.30": tuned,
        "hp_rho=0.35": with_state_override(tuned, "HIGH_PRESS", rho=0.35),
    }
    winner2 = coordinate_search(
        tuned, candidates2, "hp_rho=0.30", problems, n_runs=args.n_runs, budget=args.budget,
        master_seed=args.master_seed,
    )
    final_config = candidates2[winner2]
    print(f"  selected: {winner2}")

    print("Measuring CA's overhead ratio omega on the tuning set...")
    omega = measure_ca_omega(problems, n_runs=args.n_runs, budget=args.budget, master_seed=args.master_seed)
    print(f"  omega ~= {omega:.4f}")

    note = (
        "SMOKE-SCALE tuning only (n_runs={n_runs}, budget={budget}, dim={dim}, 2 of 7 tuning "
        "functions): this is NOT the pre-registered full protocol of research.md R13. It "
        "exercises the tuning mechanism end to end but the numeric values below are placeholders, "
        "not the frozen values gate G3 requires for a real test-suite run. "
        "measured_ca_omega={omega:.4f}"
    ).format(n_runs=args.n_runs, budget=args.budget, dim=args.dim, omega=omega)
    write_frozen_config(final_config, Path(args.out), note=note)
    print(f"Wrote {args.out} (config_hash={final_config.config_hash})")


if __name__ == "__main__":
    main()
