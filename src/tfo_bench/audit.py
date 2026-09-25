"""tfo_bench.audit: the data-integrity audit pipeline (constitution Principle V; data-model.md B4;
research.md R12.5, R12.6).

Implements, for one `Problem` (a "cell"):

- the preflight tolerance check: |f(x*) - f*| <= 1e-6*max(1, |f*|);
- the below-optimum check over a set of runs: best_f < f* - 1e-6*max(1, |f*|);
- cross-validation against an independent reference implementation;
- the mechanical disposition state machine of data-model.md B4;
- the engineering `improvement`/`penalty_artifact` classification;
- the mechanical non-discriminative (ND) rule (research.md R12.5), delegated to `stats.py`.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from tfo_bench.problems.base import Problem

PREFLIGHT_RELATIVE_TOLERANCE = 1e-6
BELOW_OPTIMUM_RELATIVE_TOLERANCE = 1e-6

#: data-model.md B4's disposition state machine.
DISPOSITIONS = frozenset(
    {
        "pending",
        "preflight_ok",
        "cross_validating",
        "validated",
        "restored",
        "excluded",
        "non_discriminative",
    }
)

#: Dispositions admissible for analysis (G5).
ADMISSIBLE_FOR_ANALYSIS = frozenset({"validated", "restored", "non_discriminative"})


class AuditPendingError(Exception):
    """Raised by analyze.py (G5) for a cell without an admissible audit disposition."""


def preflight_tolerance(f_star: float) -> float:
    return PREFLIGHT_RELATIVE_TOLERANCE * max(1.0, abs(f_star))


def below_optimum_tolerance(f_star: float) -> float:
    return BELOW_OPTIMUM_RELATIVE_TOLERANCE * max(1.0, abs(f_star))


@dataclass
class PreflightResult:
    f_star: float
    f_at_xstar: float
    abs_err: float
    passed: bool
    epsilon_used: Optional[float] = None  # composition-singularity backoff, if any (see below)


def run_preflight(
    problem: Problem,
    x_star: Optional[np.ndarray] = None,
    *,
    composition_epsilon_backoff: Optional[list[float]] = None,
) -> PreflightResult:
    """Evaluates `problem` at its claimed optimum and checks the tolerance (research.md R12).

    `composition_epsilon_backoff`: for CEC-2017 composition functions, evaluating *exactly* at the
    shift point can divide by zero in the distance-weight term (a known singularity -- see
    `tfo_bench.problems.cec2017`'s module docstring and this project's own numerical check, which
    found that a literal 1e-6 offset (as research.md R12 describes) does not satisfy the tolerance
    for every composition function at this implementation's numeric precision). When given, this
    is a decreasing sequence of candidate offsets (e.g. `[1e-6, 1e-8, 1e-10, 1e-12]`); the first
    one that (a) avoids the NaN singularity and (b) satisfies the tolerance is used, and the
    offset actually used is recorded in `PreflightResult.epsilon_used` for the audit evidence.
    """
    x_star = problem.x_star if x_star is None else x_star
    f_star = problem.f_star
    tol = preflight_tolerance(f_star)

    if composition_epsilon_backoff is None:
        f_at_xstar = float(problem.evaluate(x_star[None, :])[0])
        abs_err = abs(f_at_xstar - f_star)
        return PreflightResult(f_star, f_at_xstar, abs_err, abs_err <= tol)

    last_f_at_xstar, last_abs_err = np.nan, np.inf
    for eps in composition_epsilon_backoff:
        candidate = np.clip(x_star + eps, problem.lb, problem.ub)
        f_at_xstar = float(problem.evaluate(candidate[None, :])[0])
        if not np.isfinite(f_at_xstar):
            continue
        abs_err = abs(f_at_xstar - f_star)
        last_f_at_xstar, last_abs_err = f_at_xstar, abs_err
        if abs_err <= tol:
            return PreflightResult(f_star, f_at_xstar, abs_err, True, epsilon_used=eps)
    return PreflightResult(f_star, last_f_at_xstar, last_abs_err, False, epsilon_used=None)


def below_optimum_check(problem: Problem, best_f_all_runs: np.ndarray) -> tuple[bool, float]:
    """`True` (passes) iff no run's best_f is below f* - tolerance."""
    min_best_f = float(np.min(best_f_all_runs)) if len(best_f_all_runs) else np.inf
    tol = below_optimum_tolerance(problem.f_star)
    passed = not (min_best_f < problem.f_star - tol)
    return passed, min_best_f


@dataclass
class CellAudit:
    """data-model.md B4."""

    cell_id: str
    implementation: str
    f_star: float
    f_at_xstar: Optional[float] = None
    preflight_abs_err: Optional[float] = None
    preflight_pass: Optional[bool] = None
    min_best_f_all_runs: Optional[float] = None
    below_optimum_pass: Optional[bool] = None
    cross_ref_implementation: Optional[str] = None
    cross_ref_preflight_pass: Optional[bool] = None
    cross_ref_below_optimum_pass: Optional[bool] = None
    disposition: str = "pending"
    evidence_path: Optional[str] = None
    pre_audit_numbers_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "implementation": self.implementation,
            "f_star": self.f_star,
            "f_at_xstar": self.f_at_xstar,
            "preflight_abs_err": self.preflight_abs_err,
            "preflight_pass": self.preflight_pass,
            "min_best_f_all_runs": self.min_best_f_all_runs,
            "below_optimum_pass": self.below_optimum_pass,
            "cross_ref_implementation": self.cross_ref_implementation,
            "cross_ref_preflight_pass": self.cross_ref_preflight_pass,
            "cross_ref_below_optimum_pass": self.cross_ref_below_optimum_pass,
            "disposition": self.disposition,
            "evidence_path": self.evidence_path,
            "pre_audit_numbers_path": self.pre_audit_numbers_path,
        }


def audit_preflight_stage(problem: Problem, cell_id: str, **preflight_kwargs) -> CellAudit:
    """Runs the preflight stage only (data-model.md B4: pending -> preflight_ok | cross_validating)."""
    result = run_preflight(problem, **preflight_kwargs)
    audit = CellAudit(
        cell_id=cell_id,
        implementation=problem.implementation,
        f_star=problem.f_star,
        f_at_xstar=result.f_at_xstar,
        preflight_abs_err=result.abs_err,
        preflight_pass=result.passed,
    )
    audit.disposition = "preflight_ok" if result.passed else "cross_validating"
    return audit


def audit_runs_stage(audit: CellAudit, problem: Problem, best_f_all_runs: np.ndarray) -> CellAudit:
    """data-model.md B4: preflight_ok --runs, no run below f*--> validated
    \\--any run below f*--> cross_validating."""
    if audit.disposition != "preflight_ok":
        raise ValueError(f"audit_runs_stage requires disposition 'preflight_ok', got {audit.disposition!r}")
    passed, min_best_f = below_optimum_check(problem, best_f_all_runs)
    audit.min_best_f_all_runs = min_best_f
    audit.below_optimum_pass = passed
    audit.disposition = "validated" if passed else "cross_validating"
    return audit


def audit_cross_validation_stage(
    audit: CellAudit,
    reference_problem: Problem,
    best_f_all_runs: Optional[np.ndarray] = None,
    *,
    evidence_path: Optional[str] = None,
    pre_audit_numbers_path: Optional[str] = None,
    **preflight_kwargs,
) -> CellAudit:
    """data-model.md B4: cross_validating --passes on reference--> restored
    --fails on reference--> excluded (evidence and pre-audit numbers kept, FR-038)."""
    if audit.disposition != "cross_validating":
        raise ValueError(
            f"audit_cross_validation_stage requires disposition 'cross_validating', got {audit.disposition!r}"
        )
    ref_result = run_preflight(reference_problem, **preflight_kwargs)
    audit.cross_ref_implementation = reference_problem.implementation
    audit.cross_ref_preflight_pass = ref_result.passed

    ref_below_pass = True
    if best_f_all_runs is not None and len(best_f_all_runs):
        ref_below_pass, _ = below_optimum_check(reference_problem, best_f_all_runs)
    audit.cross_ref_below_optimum_pass = ref_below_pass

    passes_on_reference = ref_result.passed and ref_below_pass
    audit.disposition = "restored" if passes_on_reference else "excluded"
    # FR-038: pre-audit numbers are never deleted, whichever way this resolves.
    audit.evidence_path = evidence_path
    audit.pre_audit_numbers_path = pre_audit_numbers_path
    return audit


def apply_nd_rule(audit: CellAudit, is_non_discriminative: bool) -> CellAudit:
    """data-model.md B4: validated | restored --ND rule fires--> non_discriminative."""
    if is_non_discriminative and audit.disposition in ("validated", "restored"):
        audit.disposition = "non_discriminative"
    return audit


def retain_pre_audit_numbers(
    cell_id: str, suite: str, runs_csv_path: str | Path, results_root: str | Path
) -> Path:
    """FR-038 / data-model.md B4: "Pre-audit numbers are never deleted." Copies every `runs.csv`
    row for `cell_id` to `results/audit/pre_audit/<suite>/<cell_id>.csv`, a location that stays
    readable regardless of what the cell's disposition later becomes (`restored` or `excluded`).
    Called before any restoration re-run or exclusion, so the original numbers are preserved even
    though they never enter the analysis (G5) once the cell is dispositioned that way.
    """
    dest_dir = Path(results_root) / "audit" / "pre_audit" / suite
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{cell_id}.csv"

    with open(runs_csv_path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = [row for row in reader if row["cell_id"] == cell_id]
        fieldnames = reader.fieldnames

    with open(dest_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return dest_path


def classify_engineering_improvement(is_feasible: bool) -> str:
    """data-model.md B4's engineering variant: a run below f_ref is `improvement` if the point is
    feasible, `penalty_artifact` otherwise. Not grounds for exclusion (reported only)."""
    return "improvement" if is_feasible else "penalty_artifact"
