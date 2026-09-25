"""Contract test for the `CellAudit` disposition state machine (T092; data-model.md B4).

    pending --preflight fail--------------------------------> cross_validating
    pending --preflight pass--> preflight_ok --runs, no run below f*--> validated
                                              \\--any run below f*-----> cross_validating
    cross_validating --passes on reference--> restored (re-run on the reference backend)
    cross_validating --fails on reference---> excluded (evidence and pre-audit numbers kept)
    validated | restored --ND rule (research.md R12) fires--> non_discriminative
"""

from __future__ import annotations

import numpy as np
import pytest

from tfo_bench.audit import (
    apply_nd_rule,
    audit_cross_validation_stage,
    audit_preflight_stage,
    audit_runs_stage,
)
from tfo_bench.problems.base import Problem


def _sphere(f_star=0.0, x_star=None, D=3):
    x_star = np.zeros(D) if x_star is None else x_star
    return Problem(
        problem_id="p",
        suite="tuning",
        name="sphere",
        D=D,
        lb=-10.0,
        ub=10.0,
        f_star=f_star,
        fn=lambda X: np.sum(X**2, axis=1),
        x_star=x_star,
    )


def test_pending_to_preflight_ok_on_pass_then_validated_when_no_run_below_fstar():
    problem = _sphere()
    audit = audit_preflight_stage(problem, "cell1")
    assert audit.disposition == "preflight_ok"
    assert audit.preflight_pass is True

    audit = audit_runs_stage(audit, problem, best_f_all_runs=np.array([0.1, 0.2, 0.05]))
    assert audit.disposition == "validated"
    assert audit.below_optimum_pass is True


def test_pending_to_cross_validating_on_preflight_fail():
    # x_star deliberately wrong: evaluating there does not give f_star.
    problem = _sphere(x_star=np.array([5.0, 5.0, 5.0]))
    audit = audit_preflight_stage(problem, "cell2")
    assert audit.disposition == "cross_validating"
    assert audit.preflight_pass is False


def test_preflight_ok_to_cross_validating_when_a_run_is_below_fstar():
    problem = _sphere()
    audit = audit_preflight_stage(problem, "cell3")
    assert audit.disposition == "preflight_ok"

    # a run claims best_f below f* - tolerance: definitionally impossible, triggers cross-check.
    audit = audit_runs_stage(audit, problem, best_f_all_runs=np.array([0.1, -5.0, 0.05]))
    assert audit.disposition == "cross_validating"
    assert audit.below_optimum_pass is False


def test_cross_validating_to_restored_when_reference_passes():
    problem = _sphere(x_star=np.array([5.0, 5.0, 5.0]))  # fails its own preflight
    audit = audit_preflight_stage(problem, "cell4")
    assert audit.disposition == "cross_validating"

    reference = _sphere()  # a correct reference implementation
    audit = audit_cross_validation_stage(audit, reference, evidence_path="ev.json")
    assert audit.disposition == "restored"
    assert audit.cross_ref_preflight_pass is True
    assert audit.evidence_path == "ev.json"


def test_cross_validating_to_excluded_when_reference_also_fails_and_evidence_is_kept():
    problem = _sphere(x_star=np.array([5.0, 5.0, 5.0]))
    audit = audit_preflight_stage(problem, "cell5")
    assert audit.disposition == "cross_validating"

    also_broken_reference = _sphere(x_star=np.array([9.0, 9.0, 9.0]))
    audit = audit_cross_validation_stage(
        audit,
        also_broken_reference,
        evidence_path="ev.json",
        pre_audit_numbers_path="results/audit/pre_audit/tuning/cell5",
    )
    assert audit.disposition == "excluded"
    assert audit.cross_ref_preflight_pass is False
    # FR-038: pre-audit numbers are never deleted, even when excluded.
    assert audit.pre_audit_numbers_path == "results/audit/pre_audit/tuning/cell5"
    assert audit.evidence_path == "ev.json"


@pytest.mark.parametrize("starting_disposition_fn", ["validated", "restored"])
def test_nd_rule_moves_validated_or_restored_to_non_discriminative(starting_disposition_fn):
    problem = _sphere()
    audit = audit_preflight_stage(problem, "cell6")
    audit.disposition = starting_disposition_fn  # simulate having reached validated/restored

    audit = apply_nd_rule(audit, is_non_discriminative=True)
    assert audit.disposition == "non_discriminative"


def test_nd_rule_is_a_noop_when_not_triggered():
    problem = _sphere()
    audit = audit_preflight_stage(problem, "cell7")
    audit = audit_runs_stage(audit, problem, best_f_all_runs=np.array([0.1]))
    assert audit.disposition == "validated"
    audit = apply_nd_rule(audit, is_non_discriminative=False)
    assert audit.disposition == "validated"


def test_stage_functions_reject_wrong_starting_disposition():
    problem = _sphere()
    audit = audit_preflight_stage(problem, "cell8")
    assert audit.disposition == "preflight_ok"
    with pytest.raises(ValueError):
        # cross-validation requires 'cross_validating', not 'preflight_ok'
        audit_cross_validation_stage(audit, problem)
