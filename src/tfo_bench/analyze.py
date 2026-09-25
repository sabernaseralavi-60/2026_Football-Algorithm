"""tfo_bench.analyze: the generic `runs.csv` -> `CellStats`, `PairwiseTest`, `SuiteRanks` pipeline
(data-model.md B7), refusing to analyse any cell without an admissible audit disposition
(`AuditPendingError`, gate G5)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from tfo_bench.audit import ADMISSIBLE_FOR_ANALYSIS, AuditPendingError
from tfo_bench.records import read_csv_rows
from tfo_bench.stats import (
    apply_error_floor,
    cell_pairwise_tests,
    friedman_ranks,
    is_non_discriminative,
)


@dataclass
class CellStats:
    cell_id: str
    algorithm: str
    variant_id: str
    n_runs: int
    best: float
    mean: float
    std: float
    median: float
    worst: float


def load_cell_dispositions(cell_audit_csv: str) -> dict[str, str]:
    return {row["cell_id"]: row["disposition"] for row in read_csv_rows(cell_audit_csv)}


def _check_admissible(cell_id: str, dispositions: dict[str, str]) -> None:
    disposition = dispositions.get(cell_id)
    if disposition not in ADMISSIBLE_FOR_ANALYSIS:
        raise AuditPendingError(
            f"cell {cell_id!r} has disposition {disposition!r}, not one of "
            f"{sorted(ADMISSIBLE_FOR_ANALYSIS)} (gate G5)"
        )


def compute_cell_stats(
    runs_csv: str, cell_audit_csv: str, *, restrict_cell_ids: Optional[set[str]] = None
) -> list[CellStats]:
    """Reads `runs.csv`, floors each row's error, and aggregates to one `CellStats` per
    (cell, algorithm, variant); refuses any cell whose audit disposition is not admissible (G5)."""
    dispositions = load_cell_dispositions(cell_audit_csv)
    rows = read_csv_rows(runs_csv)

    groups: dict[tuple[str, str, str], list[float]] = {}
    for row in rows:
        cell_id = row["cell_id"]
        if restrict_cell_ids is not None and cell_id not in restrict_cell_ids:
            continue
        _check_admissible(cell_id, dispositions)
        key = (cell_id, row["algorithm"], row["variant_id"])
        error = float(row["error"]) if row["error"] != "" else np.nan
        groups.setdefault(key, []).append(error)

    results = []
    for (cell_id, algorithm, variant_id), errors in groups.items():
        floored = apply_error_floor(np.array(errors, dtype=float))
        results.append(
            CellStats(
                cell_id=cell_id,
                algorithm=algorithm,
                variant_id=variant_id,
                n_runs=len(floored),
                best=float(np.min(floored)),
                mean=float(np.mean(floored)),
                std=float(np.std(floored, ddof=1)) if len(floored) > 1 else 0.0,
                median=float(np.median(floored)),
                worst=float(np.max(floored)),
            )
        )
    return results


def compute_pairwise_and_ranks(
    runs_csv: str, cell_audit_csv: str, *, restrict_cell_ids: Optional[set[str]] = None
):
    """Per-cell pairwise Wilcoxon+Holm tests, the ND rule, and suite-level Friedman ranks over the
    discriminative cells (research.md R12 items 2-3, 5; G5)."""
    dispositions = load_cell_dispositions(cell_audit_csv)
    rows = read_csv_rows(runs_csv)

    # cell_id -> algorithm -> list of (run, error), so pairing by run index (CRN) is exact.
    by_cell_alg: dict[str, dict[str, dict[str, float]]] = {}
    for row in rows:
        cell_id = row["cell_id"]
        if restrict_cell_ids is not None and cell_id not in restrict_cell_ids:
            continue
        _check_admissible(cell_id, dispositions)
        alg = row["algorithm"]
        error = float(row["error"]) if row["error"] != "" else np.nan
        by_cell_alg.setdefault(cell_id, {}).setdefault(alg, {})[row["run"]] = error

    pairwise_by_cell = {}
    nd_cells: set[str] = set()
    mean_error_by_alg_and_cell: dict[str, dict[str, float]] = {}

    for cell_id, by_alg in by_cell_alg.items():
        common_runs = set.intersection(*(set(v) for v in by_alg.values())) if by_alg else set()
        errors_by_alg = {
            alg: apply_error_floor(np.array([by_alg[alg][r] for r in sorted(common_runs)]))
            for alg in by_alg
        }
        tests = cell_pairwise_tests(errors_by_alg)
        pairwise_by_cell[cell_id] = tests
        if dispositions.get(cell_id) == "non_discriminative" or is_non_discriminative(tests):
            nd_cells.add(cell_id)
        for alg, errs in errors_by_alg.items():
            mean_error_by_alg_and_cell.setdefault(alg, {})[cell_id] = float(np.mean(errs))

    discriminative_cells = set(by_cell_alg) - nd_cells
    ranks_input = {
        alg: {c: mean_error_by_alg_and_cell[alg][c] for c in discriminative_cells}
        for alg in mean_error_by_alg_and_cell
    }
    ranks, chi2, p, n_cells = (
        friedman_ranks(ranks_input) if discriminative_cells else ([], float("nan"), float("nan"), 0)
    )
    return pairwise_by_cell, nd_cells, ranks, chi2, p, n_cells
