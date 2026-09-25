"""tfo_bench.records: writers and validators for the results CSV schema
(contracts/results-schema.md).

Only the parent process ever calls these writers (research.md R17): the runner (single-writer)
appends one row at a time, opening each file in append mode and writing the header only if the
file does not already exist, so a checkpointed/resumed run just keeps appending.
"""

from __future__ import annotations

import csv
import gzip
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np

from tfo.registry import ALL_TAGS, Archetype, ENABLE_TAGS

MECHANISM_TAGS: list[str] = [t.value for t in ALL_TAGS]

SCHEMA_VERSION = 1

RUNS_COLUMNS: list[str] = [
    "schema_version",
    "run_key",
    "experiment",
    "suite",
    "cell_id",
    "function_id",
    "dim",
    "algorithm",
    "variant_id",
    "config_hash",
    "run",
    "seed",
    "budget",
    "evals_used",
    "evals_internal",
    "status",
    "best_f",
    "f_star",
    "error",
    "max_violation",
    "wall_time_s",
    "objective_time_s",
    "n_iterations",
    "n_state_transitions",
    "occ_build_up",
    "occ_control",
    "occ_high_press",
    "occ_chasing",
    "n_counter_attacks",
    "n_substitutions",
    "n_var_rollbacks",
    "n_set_pieces",
    "final_possession_rate",
]

CURVE_COLUMNS: list[str] = ["run_key"] + [f"c{k:03d}" for k in range(1, 101)]
MECHANISM_EVALS_COLUMNS: list[str] = ["run_key", "tag", "evals"]
TACTICAL_TRACE_COLUMNS: list[str] = [
    "run_key",
    "segment",
    "state",
    "iter_start",
    "iter_end",
    "eval_start",
    "eval_end",
]


def _fmt(value: Any) -> str:
    """repr precision for floats (results-schema.md "Conventions"); empty string for None/NaN."""
    if value is None:
        return ""
    if isinstance(value, float):
        if np.isnan(value):
            return ""
        return repr(value)
    return str(value)


def run_key(experiment: str, cell_id: str, algorithm: str, variant_id: str, run: int) -> str:
    return f"{experiment}/{cell_id}/{algorithm}/{variant_id}/{run}"


def make_run_record(
    *,
    experiment: str,
    suite: str,
    cell_id: str,
    function_id: str,
    dim: int,
    algorithm: str,
    variant_id: str,
    config_hash: str,
    run: int,
    seed: int,
    budget: int,
    evals_used: int,
    evals_internal: Optional[int],
    status: str,
    best_f: float,
    f_star: Optional[float],
    max_violation: Optional[float] = None,
    wall_time_s: float = 0.0,
    objective_time_s: float = 0.0,
    n_iterations: Optional[int] = None,
    n_state_transitions: Optional[int] = None,
    occupancy: Optional[dict[str, float]] = None,
    n_counter_attacks: Optional[int] = None,
    n_substitutions: Optional[int] = None,
    n_var_rollbacks: Optional[int] = None,
    n_set_pieces: Optional[int] = None,
    final_possession_rate: Optional[float] = None,
) -> dict[str, Any]:
    error = None if f_star is None else (best_f - f_star)
    occupancy = occupancy or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "run_key": run_key(experiment, cell_id, algorithm, variant_id, run),
        "experiment": experiment,
        "suite": suite,
        "cell_id": cell_id,
        "function_id": function_id,
        "dim": dim,
        "algorithm": algorithm,
        "variant_id": variant_id,
        "config_hash": config_hash,
        "run": run,
        "seed": seed,
        "budget": budget,
        "evals_used": evals_used,
        "evals_internal": evals_internal,
        "status": status,
        "best_f": best_f,
        "f_star": f_star,
        "error": error,
        "max_violation": max_violation,
        "wall_time_s": wall_time_s,
        "objective_time_s": objective_time_s,
        "n_iterations": n_iterations,
        "n_state_transitions": n_state_transitions,
        "occ_build_up": occupancy.get("BUILD_UP"),
        "occ_control": occupancy.get("CONTROL"),
        "occ_high_press": occupancy.get("HIGH_PRESS"),
        "occ_chasing": occupancy.get("CHASING"),
        "n_counter_attacks": n_counter_attacks,
        "n_substitutions": n_substitutions,
        "n_var_rollbacks": n_var_rollbacks,
        "n_set_pieces": n_set_pieces,
        "final_possession_rate": final_possession_rate,
    }


class ResultsWriter:
    """One writer per `(experiment, suite)` output directory (results-schema.md §1 layout)."""

    def __init__(self, results_root: str | Path, experiment: str, suite: str):
        self.dir = Path(results_root) / experiment / suite
        self.dir.mkdir(parents=True, exist_ok=True)

    # -- generic CSV append, header written once --------------------------------------

    def _append_row(self, filename: str, columns: list[str], row: dict[str, Any]) -> None:
        path = self.dir / filename
        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="") as fh:
            writer = csv.writer(fh)
            if write_header:
                writer.writerow(columns)
            writer.writerow([_fmt(row.get(c)) for c in columns])

    def append_run(self, record: dict[str, Any]) -> None:
        self._append_row("runs.csv", RUNS_COLUMNS, record)

    def append_curve(self, run_key_: str, curve: np.ndarray) -> None:
        row = {"run_key": run_key_}
        row.update({f"c{k:03d}": float(curve[k - 1]) for k in range(1, 101)})
        self._append_row("curves.csv", CURVE_COLUMNS, row)

    def append_mechanism_evals(self, run_key_: str, evals_by_tag: dict[str, int]) -> None:
        path = self.dir / "mechanism_evals.csv"
        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="") as fh:
            writer = csv.writer(fh)
            if write_header:
                writer.writerow(MECHANISM_EVALS_COLUMNS)
            for tag in MECHANISM_TAGS:
                writer.writerow([run_key_, tag, int(evals_by_tag.get(tag, 0))])

    def append_tactical_trace(self, run_key_: str, segments: Iterable[Any]) -> None:
        path = self.dir / "tactical_trace.csv.gz"
        write_header = not path.exists() or path.stat().st_size == 0
        lines = []
        if write_header:
            lines.append(",".join(TACTICAL_TRACE_COLUMNS))
        for i, seg in enumerate(segments):
            lines.append(
                ",".join(
                    str(v)
                    for v in (
                        run_key_,
                        i,
                        seg.state,
                        seg.iter_start,
                        seg.iter_end,
                        seg.eval_start,
                        seg.eval_end,
                    )
                )
            )
        data = ("\n".join(lines) + "\n").encode("utf-8")
        # Append as a new gzip member (multi-member gzip streams read back transparently via
        # `gzip.open`); gzip mtime=0 for reproducible bytes (results-schema.md "Conventions").
        with open(path, "ab") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
                gz.write(data)

    def append_best_x(self, run_key_: str, x_real: np.ndarray) -> None:
        D = len(x_real)
        columns = ["run_key"] + [f"x{i + 1}" for i in range(D)]
        row = {"run_key": run_key_}
        row.update({f"x{i + 1}": float(x_real[i]) for i in range(D)})
        self._append_row("best_x.csv", columns, row)


# ----------------------------------------------------------------------------------------
# Validators (scripts/validate_results.py calls these; results-schema.md §9)
# ----------------------------------------------------------------------------------------


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def validate_runs_csv(path: str | Path) -> list[str]:
    """Checks 1 (columns), 2 (unique run_key), 3 (evals_used<=budget), 4 (TFO evals_internal),
    6 (identical budget per cell)."""
    issues: list[str] = []
    rows = read_csv_rows(path)
    if not rows:
        return issues
    got_cols = list(rows[0].keys())
    if got_cols != RUNS_COLUMNS:
        issues.append(f"runs.csv columns mismatch: {got_cols} != {RUNS_COLUMNS}")

    seen_keys: set[str] = set()
    budgets_by_cell: dict[str, set[str]] = {}
    seeds_by_cell_run: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        rk = row["run_key"]
        if rk in seen_keys:
            issues.append(f"duplicate run_key: {rk}")
        seen_keys.add(rk)

        evals_used = int(row["evals_used"])
        budget = int(row["budget"])
        if evals_used > budget:
            issues.append(f"{rk}: evals_used ({evals_used}) > budget ({budget})")

        if row["evals_internal"]:
            evals_internal = int(row["evals_internal"])
            if evals_internal != evals_used:
                issues.append(f"{rk}: evals_internal ({evals_internal}) != evals_used ({evals_used})")

        budgets_by_cell.setdefault(row["cell_id"], set()).add(row["budget"])
        seeds_by_cell_run.setdefault((row["cell_id"], row["run"]), set()).add(row["seed"])

    for cell_id, budgets in budgets_by_cell.items():
        if len(budgets) > 1:
            issues.append(f"cell {cell_id}: budget differs across algorithms: {budgets}")
    for (cell_id, run), seeds in seeds_by_cell_run.items():
        if len(seeds) > 1:
            issues.append(f"cell {cell_id} run {run}: seed differs across algorithms: {seeds}")

    return issues


def validate_curves_csv(runs_path: str | Path, curves_path: str | Path) -> list[str]:
    """Checks 7 (non-increasing curves) and cross-reference with runs.csv run_keys."""
    issues: list[str] = []
    run_keys = {r["run_key"] for r in read_csv_rows(runs_path)}
    curve_rows = read_csv_rows(curves_path)
    got_cols = list(curve_rows[0].keys()) if curve_rows else CURVE_COLUMNS
    if got_cols != CURVE_COLUMNS:
        issues.append(f"curves.csv columns mismatch: {got_cols} != {CURVE_COLUMNS}")
    for row in curve_rows:
        rk = row["run_key"]
        if rk not in run_keys:
            issues.append(f"curves.csv run_key {rk} not in runs.csv")
        values = [float(row[c]) for c in CURVE_COLUMNS[1:]]
        for a, b in zip(values, values[1:]):
            if b > a + 1e-9:
                issues.append(f"{rk}: curve is not non-increasing ({a} -> {b})")
                break
    return issues


#: Every `variant_id` this pass can produce (data-model.md A15; results-schema.md's `algorithm`
#: and `variant_id` columns), used by check 9 (Principle VI, plan.md's identifier allowlist).
ALLOWED_VARIANT_IDS: set[str] = (
    {"default", "full", "static", "G-topology", "custom"}
    | {f"off:{tag.value}" for tag in ENABLE_TAGS}
    | {f"homog:{a.value.lower()}" for a in Archetype}
)

#: Baseline roster labels plus every "TFO" / "TFO-static" / "TFO[<variant_id>]" spelling
#: (optimizer-interface.md §2).
ALLOWED_ALGORITHM_NAMES: set[str] = {
    "TFO",
    "TFO-static",
    "CA",
    "GA",
    "PSO",
    "GWO",
    "WOA",
    "L-SHADE",
    "CMA-ES (IPOP)",
} | {f"TFO[{v}]" for v in ALLOWED_VARIANT_IDS}


def validate_identifiers_csv(runs_path: str | Path) -> list[str]:
    """Check 9: "The files contain no identifier that is not in the registry allowlist"
    (Principle VI; plan.md)."""
    issues: list[str] = []
    for row in read_csv_rows(runs_path):
        if row["algorithm"] not in ALLOWED_ALGORITHM_NAMES:
            issues.append(f"{row['run_key']}: unknown algorithm identifier {row['algorithm']!r}")
        if row["variant_id"] not in ALLOWED_VARIANT_IDS:
            issues.append(f"{row['run_key']}: unknown variant_id identifier {row['variant_id']!r}")
    return issues


def validate_audit_dispositions(runs_path: str | Path, cell_audit_path: str | Path) -> list[str]:
    """Check 8: "Every analysed cell has an admissible audit disposition" (G5)."""
    from tfo_bench.audit import ADMISSIBLE_FOR_ANALYSIS

    dispositions = {row["cell_id"]: row["disposition"] for row in read_csv_rows(cell_audit_path)}
    issues: list[str] = []
    seen_cells: set[str] = set()
    for row in read_csv_rows(runs_path):
        cell_id = row["cell_id"]
        if cell_id in seen_cells:
            continue
        seen_cells.add(cell_id)
        disposition = dispositions.get(cell_id)
        if disposition not in ADMISSIBLE_FOR_ANALYSIS:
            issues.append(
                f"cell {cell_id!r} has disposition {disposition!r}, not one of "
                f"{sorted(ADMISSIBLE_FOR_ANALYSIS)} (G5)"
            )
    return issues


def validate_mechanism_evals_csv(runs_path: str | Path, mech_path: str | Path) -> list[str]:
    """Check 4's per-tag sum, for the TFO family only."""
    issues: list[str] = []
    runs_by_key = {r["run_key"]: r for r in read_csv_rows(runs_path)}
    sums: dict[str, int] = {}
    tags_seen: dict[str, set[str]] = {}
    for row in read_csv_rows(mech_path):
        rk = row["run_key"]
        sums[rk] = sums.get(rk, 0) + int(row["evals"])
        tags_seen.setdefault(rk, set()).add(row["tag"])

    for rk, total in sums.items():
        run = runs_by_key.get(rk)
        if run is None:
            continue
        if run["evals_internal"] and int(run["evals_internal"]) != total:
            issues.append(f"{rk}: mechanism_evals sum ({total}) != evals_internal ({run['evals_internal']})")
        missing_tags = set(MECHANISM_TAGS) - tags_seen[rk]
        if missing_tags:
            issues.append(f"{rk}: mechanism_evals.csv missing tags {missing_tags}")
    return issues
