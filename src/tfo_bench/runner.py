"""tfo_bench.runner: job enumeration, execution pool, and the freeze/pre-registration/SC-010
guards (T089; data-model.md B5; constitution gates G3, G4; SC-010).

Design note on process-pool safety: a worker process rebuilds its `Problem` and `Optimizer`
adapter from small, picklable specs (suite name + dimension + function id; algorithm name) rather
than receiving live objects, since several underlying libraries' state (niapy's `Task`, pycma's
`CMAEvolutionStrategy`, an opfunu class instance holding a bound `evaluate`) does not pickle
reliably. `SUITE_BUILDERS` and `ALGORITHM_FACTORIES` are the two small registries this requires.
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np

from tfo.config import TFOConfig

from tfo_bench import records
from tfo_bench.algorithms.base import Optimizer
from tfo_bench.algorithms.cmaes import CMAESAdapter
from tfo_bench.algorithms.lshade import LSHADEAdapter
from tfo_bench.algorithms.sibling import CAAdapter, GAAdapter, GWOAdapter, PSOAdapter
from tfo_bench.algorithms.tfo_adapter import TFOAdapter, static_adapter
from tfo_bench.algorithms.woa import WOAAdapter
from tfo_bench.ledger import BudgetExhausted, CountingObjective
from tfo_bench.problems import cec2017, cec2022, engineering, tuning
from tfo_bench.problems.base import Problem, ProblemView
from tfo_bench.seeds import cell_seed


class ConfigNotFrozenError(Exception):
    """G3: a non-smoke test-suite job was requested with a TFOConfig hash that differs from the
    file tagged `tfo-frozen-v1`."""


class PreRegistrationRequiredError(Exception):
    """G4: a non-smoke test-suite run was requested before hypotheses/protocol were pre-registered
    (the `prereg-v1` tag does not exist)."""


class RosterCompositionError(Exception):
    """SC-010: an experiment definition includes TFO without also including TFO-static."""


#: suite name -> (dim -> {function_id: Problem}) builder.
SUITE_BUILDERS: dict[str, Callable[[int], dict[str, Problem]]] = {
    "cec2017": cec2017.build_problems,
    "cec2022": cec2022.build_problems,
    "tuning": tuning.build_problems,
}

#: algorithm name -> zero-arg factory. TFO-family variants are handled separately (they need a
#: TFOConfig), via `tfo_variant_factories` in tfo_adapter.py.
ALGORITHM_FACTORIES: dict[str, Callable[[], Optimizer]] = {
    "TFO": lambda: TFOAdapter(),
    "TFO-static": static_adapter,
    "CA": CAAdapter,
    "GA": GAAdapter,
    "PSO": PSOAdapter,
    "GWO": GWOAdapter,
    "WOA": WOAAdapter,
    "L-SHADE": LSHADEAdapter,
    "CMA-ES (IPOP)": CMAESAdapter,
}

NON_SMOKE_TEST_SUITE_EXPERIMENTS = frozenset(
    {"main", "ablation", "sensitivity", "takeover", "epsilon", "timing"}
)


def set_single_threaded_env() -> None:
    """"a ProcessPoolExecutor pool with OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/MKL_NUM_THREADS set
    to 1" (T089): called once per worker process so BLAS/OpenMP never oversubscribes cores when
    many single-evaluation jobs run in parallel."""
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"


@dataclass(frozen=True)
class ExperimentJob:
    """data-model.md B5."""

    experiment: str
    suite: str
    cell_id: str
    function_id: str
    dim: int
    algorithm: str
    variant_id: str
    run: int
    seed: int
    budget: int
    config_hash: str


def check_roster_includes_tfo_static_with_tfo(algorithms: Iterable[str]) -> None:
    """SC-010: "refuses any experiment definition including TFO without also including
    TFO-static"."""
    algorithms = set(algorithms)
    if "TFO" in algorithms and "TFO-static" not in algorithms:
        raise RosterCompositionError(
            "SC-010: an experiment roster includes 'TFO' but not 'TFO-static'; every experiment "
            "that runs TFO must also run TFO-static."
        )


def check_config_frozen(
    config_hash: str, experiment: str, frozen_config_path: str | Path
) -> None:
    """G3: `ConfigNotFrozenError` for any non-smoke test-suite job whose TFO configuration hash
    differs from `config/tfo_frozen.toml` (tagged `tfo-frozen-v1`)."""
    if experiment not in NON_SMOKE_TEST_SUITE_EXPERIMENTS:
        return
    frozen_path = Path(frozen_config_path)
    if not frozen_path.exists():
        raise ConfigNotFrozenError(
            f"{frozen_path} does not exist; tuning must freeze it (tagged tfo-frozen-v1) before "
            f"any non-smoke {experiment!r} job runs (gate G3)."
        )
    frozen_hash = TFOConfig.from_toml(frozen_path).config_hash
    if config_hash != frozen_hash:
        raise ConfigNotFrozenError(
            f"config_hash {config_hash} does not match the frozen configuration's "
            f"{frozen_hash} at {frozen_path} (gate G3)."
        )


def get_git_tags(repo_root: Optional[Path] = None) -> set[str]:
    import subprocess

    root = str(repo_root) if repo_root is not None else "."
    try:
        out = subprocess.check_output(
            ["git", "-C", root, "tag", "--list"], stderr=subprocess.DEVNULL
        )
        return set(out.decode().split())
    except Exception:
        return set()


def check_preregistered(experiment: str, git_tags: Iterable[str]) -> None:
    """G4: hypotheses/protocol must be pre-registered (tag `prereg-v1`) before any non-smoke
    test-suite job runs."""
    if experiment not in NON_SMOKE_TEST_SUITE_EXPERIMENTS:
        return
    if "prereg-v1" not in set(git_tags):
        raise PreRegistrationRequiredError(
            f"tag 'prereg-v1' not found; {experiment!r} jobs require config/protocol.toml to be "
            "pre-registered before any non-smoke test-suite run (gate G4)."
        )


def build_problem(suite: str, dim: int, function_id: str) -> Problem:
    if suite == "engineering":
        return engineering.build_problems()[function_id]
    return SUITE_BUILDERS[suite](dim)[function_id]


def build_algorithm(algorithm: str, variant_id: str, tfo_config: Optional[TFOConfig] = None) -> Optimizer:
    if algorithm == "TFO-static" and tfo_config is None:
        import tfo as _tfo

        return TFOAdapter(_tfo.TFO_STATIC)
    if algorithm in ("TFO", "TFO-static") or algorithm.startswith("TFO["):
        return TFOAdapter(tfo_config)
    return ALGORITHM_FACTORIES[algorithm]()


def enumerate_jobs(
    *,
    experiment: str,
    suite: str,
    function_ids: Iterable[str],
    dim: int,
    algorithms: Iterable[str],
    n_runs: int,
    budget: int,
    master_seed: int,
    variant_id_by_algorithm: Optional[dict[str, str]] = None,
    config_hash_by_algorithm: Optional[dict[str, str]] = None,
) -> list[ExperimentJob]:
    """Enumerates every `(function_id, algorithm, run)` job for one suite/dimension, with the CRN
    seed shared across every algorithm at the same (cell, run) (research.md R11)."""
    algorithms = list(algorithms)
    check_roster_includes_tfo_static_with_tfo(algorithms)
    default_variant_ids = {"TFO": "full", "TFO-static": "static"}
    variant_id_by_algorithm = {**default_variant_ids, **(variant_id_by_algorithm or {})}
    config_hash_by_algorithm = config_hash_by_algorithm or {}

    jobs: list[ExperimentJob] = []
    for function_id in function_ids:
        cell_id = f"{suite}_{function_id}_D{dim}" if suite != "engineering" else f"engineering_{function_id}"
        numeric_fid = int("".join(c for c in function_id if c.isdigit()) or 0)
        for run in range(n_runs):
            seed = cell_seed(master_seed, suite, numeric_fid, dim, run)
            for algorithm in algorithms:
                jobs.append(
                    ExperimentJob(
                        experiment=experiment,
                        suite=suite,
                        cell_id=cell_id,
                        function_id=function_id,
                        dim=dim,
                        algorithm=algorithm,
                        variant_id=variant_id_by_algorithm.get(algorithm, "default"),
                        run=run,
                        seed=seed,
                        budget=budget,
                        config_hash=config_hash_by_algorithm.get(algorithm, ""),
                    )
                )
    return jobs


def existing_run_keys(runs_csv_path: str | Path) -> set[str]:
    """For checkpoint/resume: run_keys already completed and written."""
    path = Path(runs_csv_path)
    if not path.exists():
        return set()
    return {row["run_key"] for row in records.read_csv_rows(path)}


def run_single_job(
    job: ExperimentJob, *, tfo_config: Optional[TFOConfig] = None, experiment_for_view: Optional[str] = None
) -> dict:
    """Runs exactly one job and returns everything needed to write it to the results files.
    Pure function of `job` (plus, for TFO-family jobs, the `TFOConfig` to use) -- safe to call
    from a worker process."""
    problem = build_problem(job.suite, job.dim, job.function_id)
    ledger = CountingObjective(problem, job.budget)
    view = ProblemView(ledger, problem, experiment_for_view or job.experiment)

    adapter = build_algorithm(job.algorithm, job.variant_id, tfo_config)
    t0 = time.perf_counter()
    result = adapter.run(view, job.budget, job.seed)
    wall_time_s = time.perf_counter() - t0
    ledger.finalize()

    is_tfo_family = job.algorithm in ("TFO", "TFO-static") or job.algorithm.startswith("TFO[")
    evals_internal = sum(result.extras["evals_by_mechanism"].values()) if is_tfo_family else None

    max_violation = None
    if problem.has_constraints and ledger.best_u is not None:
        G = problem.constraints_unit(ledger.best_u[None, :])[0]
        max_violation = float(np.max(np.concatenate([[0.0], G])))

    record = records.make_run_record(
        experiment=job.experiment,
        suite=job.suite,
        cell_id=job.cell_id,
        function_id=job.function_id,
        dim=job.dim,
        algorithm=job.algorithm,
        variant_id=job.variant_id,
        config_hash=job.config_hash or (tfo_config.config_hash if tfo_config else ""),
        run=job.run,
        seed=job.seed,
        budget=job.budget,
        evals_used=ledger.evals_used,
        evals_internal=evals_internal,
        status=result.status,
        best_f=ledger.best_f,
        f_star=problem.f_star,
        max_violation=max_violation,
        wall_time_s=wall_time_s,
        objective_time_s=ledger.objective_time_ns / 1e9,
    )
    return {
        "record": record,
        "curve": ledger.curve,
        "evals_by_mechanism": result.extras.get("evals_by_mechanism") if is_tfo_family else None,
        "tactical_trace": result.extras.get("tactical_trace") if is_tfo_family else None,
        "best_x_real": problem.decode(ledger.best_u[None, :])[0] if ledger.best_u is not None else None,
    }


def run_experiment(
    jobs: list[ExperimentJob],
    writer: records.ResultsWriter,
    *,
    tfo_configs_by_variant: Optional[dict[str, TFOConfig]] = None,
    n_workers: int = 1,
    resume: bool = True,
    write_best_x_for: frozenset[str] = frozenset({"engineering", "epsilon"}),
) -> int:
    """Runs every job not already present in `writer`'s runs.csv (checkpoint/resume keyed by
    run_key, which already encodes (algorithm, cell_id, variant_id, run)). Returns the number of
    jobs actually run."""
    tfo_configs_by_variant = tfo_configs_by_variant or {}
    runs_path = writer.dir / "runs.csv"
    done = existing_run_keys(runs_path) if resume else set()

    def _job_key(job: ExperimentJob) -> str:
        return records.run_key(job.experiment, job.cell_id, job.algorithm, job.variant_id, job.run)

    pending = [j for j in jobs if _job_key(j) not in done]
    n_ran = 0

    if n_workers <= 1:
        for job in pending:
            cfg = tfo_configs_by_variant.get(job.variant_id)
            outcome = run_single_job(job, tfo_config=cfg)
            _write_outcome(writer, job, outcome, write_best_x_for)
            n_ran += 1
        return n_ran

    set_single_threaded_env()
    with ProcessPoolExecutor(max_workers=n_workers, initializer=set_single_threaded_env) as pool:
        futures = {
            pool.submit(run_single_job, job, tfo_config=tfo_configs_by_variant.get(job.variant_id)): job
            for job in pending
        }
        for future in as_completed(futures):
            job = futures[future]
            outcome = future.result()
            _write_outcome(writer, job, outcome, write_best_x_for)
            n_ran += 1
    return n_ran


def _write_outcome(writer: records.ResultsWriter, job: ExperimentJob, outcome: dict, write_best_x_for) -> None:
    record = outcome["record"]
    writer.append_run(record)
    writer.append_curve(record["run_key"], outcome["curve"])
    if outcome["evals_by_mechanism"] is not None:
        writer.append_mechanism_evals(record["run_key"], outcome["evals_by_mechanism"])
    if outcome["tactical_trace"] is not None:
        writer.append_tactical_trace(record["run_key"], outcome["tactical_trace"])
    if job.experiment in write_best_x_for and outcome["best_x_real"] is not None:
        writer.append_best_x(record["run_key"], outcome["best_x_real"])
