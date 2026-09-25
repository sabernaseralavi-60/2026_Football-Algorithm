"""tfo_bench.stats: the statistical analysis plan (research.md R12).

- the error floor (errors below 1e-8 are set to 0);
- per-cell Wilcoxon signed-rank, Holm-corrected over all C(k, 2) pairs;
- Friedman mean ranks;
- the Mann-Whitney (rank-sum) robustness check;
- the mechanical non-discriminative (ND) rule (research.md R12.5): "a cell is non-discriminative
  if none of its C(k, 2) pairwise tests is significant after Holm correction".
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal, Optional

import numpy as np
from scipy import stats as _scipy_stats

ERROR_FLOOR = 1e-8
ALPHA = 0.05


def apply_error_floor(errors: np.ndarray) -> np.ndarray:
    """"Errors below 1e-8 are set to 0" (research.md R12 item 1)."""
    errors = np.asarray(errors, dtype=float)
    return np.where(errors < ERROR_FLOOR, 0.0, errors)


def holm_correction(p_values: list[float]) -> list[float]:
    """Holm (1979) step-down correction. Unit-tested against a published worked example
    (T097; research.md R12.7).

    Returns adjusted p-values in the SAME order as the input, each capped at 1.0 and enforced
    monotone (a later-ranked p-value's adjustment is never smaller than an earlier one's, the
    standard Holm step-down guarantee)."""
    m = len(p_values)
    if m == 0:
        return []
    order = np.argsort(p_values)
    sorted_p = np.asarray(p_values, dtype=float)[order]
    adjusted_sorted = np.empty(m, dtype=float)
    running_max = 0.0
    for i, p in enumerate(sorted_p):
        candidate = (m - i) * p
        running_max = max(running_max, candidate)
        adjusted_sorted[i] = min(1.0, running_max)
    adjusted = np.empty(m, dtype=float)
    adjusted[order] = adjusted_sorted
    return adjusted.tolist()


@dataclass
class PairwiseTest:
    alg_a: str
    alg_b: str
    n: int
    w_stat: Optional[float]
    p_raw: float
    median_diff: float
    outcome_a: Literal["win", "tie", "loss"] = "tie"
    p_holm: Optional[float] = None  # filled in once the whole cell's family is known


def wilcoxon_signed_rank(errors_a: np.ndarray, errors_b: np.ndarray) -> PairwiseTest:
    """Two-sided Wilcoxon signed-rank, paired by run index (CRN), `zero_method="pratt"`
    (research.md R12 item 2). "If all 30 differences are zero, the outcome is a tie and no test is
    run" (the edge case named explicitly in research.md R12)."""
    errors_a = np.asarray(errors_a, dtype=float)
    errors_b = np.asarray(errors_b, dtype=float)
    diffs = errors_a - errors_b
    n = len(diffs)
    median_diff = float(np.median(diffs))

    if np.all(diffs == 0.0):
        return PairwiseTest("a", "b", n, None, 1.0, median_diff, outcome_a="tie")

    w_stat, p_raw = _scipy_stats.wilcoxon(errors_a, errors_b, zero_method="pratt", method="auto")
    return PairwiseTest("a", "b", n, float(w_stat), float(p_raw), median_diff)


def mann_whitney_robustness(errors_a: np.ndarray, errors_b: np.ndarray) -> float:
    """The pre-registered robustness check: `scipy.stats.ranksums` (research.md R12 item 4)."""
    _stat, p_raw = _scipy_stats.ranksums(errors_a, errors_b)
    return float(p_raw)


def cell_pairwise_tests(errors_by_algorithm: dict[str, np.ndarray]) -> list[PairwiseTest]:
    """All C(k, 2) pairwise Wilcoxon tests within one cell, Holm-corrected as one family
    (research.md R12 item 2: "over all C(k, 2) pairs of the k algorithms in the roster")."""
    algorithms = list(errors_by_algorithm)
    pairs = list(combinations(algorithms, 2))
    tests = []
    for alg_a, alg_b in pairs:
        t = wilcoxon_signed_rank(errors_by_algorithm[alg_a], errors_by_algorithm[alg_b])
        t.alg_a, t.alg_b = alg_a, alg_b
        tests.append(t)

    p_raw_values = [t.p_raw for t in tests]
    p_holm_values = holm_correction(p_raw_values)
    for t, p_holm in zip(tests, p_holm_values):
        t.p_holm = p_holm
        if p_holm < ALPHA and t.median_diff != 0.0:
            t.outcome_a = "win" if t.median_diff < 0 else "loss"
        else:
            t.outcome_a = "tie"
    return tests


def is_non_discriminative(pairwise_tests: list[PairwiseTest]) -> bool:
    """research.md R12.5: "A cell is non-discriminative if none of its C(k, 2) pairwise tests is
    significant after Holm correction."."""
    return not any((t.p_holm is not None and t.p_holm < ALPHA) for t in pairwise_tests)


@dataclass
class SuiteRanks:
    algorithm: str
    mean_rank: float


def friedman_ranks(
    mean_error_by_algorithm_and_cell: dict[str, dict[str, float]],
) -> tuple[list[SuiteRanks], float, float, int]:
    """Friedman mean ranks over cells (blocking factor), plus the chi-square statistic and its
    p-value (research.md R12 item 3)."""
    algorithms = list(mean_error_by_algorithm_and_cell)
    cells = list(next(iter(mean_error_by_algorithm_and_cell.values())))
    n_cells = len(cells)

    # matrix: rows = cells (blocks), columns = algorithms
    matrix = np.array(
        [[mean_error_by_algorithm_and_cell[alg][cell] for alg in algorithms] for cell in cells]
    )
    ranks = np.array([_scipy_stats.rankdata(row) for row in matrix])
    mean_ranks = ranks.mean(axis=0)

    if n_cells >= 2 and len(algorithms) >= 3:
        chi2, p = _scipy_stats.friedmanchisquare(*[matrix[:, j] for j in range(len(algorithms))])
    else:
        chi2, p = float("nan"), float("nan")

    return (
        [SuiteRanks(alg, float(mr)) for alg, mr in zip(algorithms, mean_ranks)],
        float(chi2),
        float(p),
        n_cells,
    )
