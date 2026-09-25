"""Property-based tests for EvalAccount (tasks.md T013; evaluation-ledger.md invariants L1, L2,
L5, L6, L7)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tfo.account import BudgetExhausted, EvalAccount
from tfo.registry import ALL_TAGS, MechanismTag


def _sphere(X: np.ndarray) -> np.ndarray:
    return np.sum(X**2, axis=1)


def test_l1_evals_used_never_exceeds_budget_simple():
    acc = EvalAccount(budget=10, objective=_sphere, d=3)
    acc.evaluate(np.zeros((4, 3)), MechanismTag.VIRTUOSO)
    acc.evaluate(np.zeros((4, 3)), MechanismTag.VIRTUOSO)
    with pytest.raises(BudgetExhausted):
        acc.evaluate(np.zeros((4, 3)), MechanismTag.VIRTUOSO)
    assert acc.evals_used <= 10


@given(batch_sizes=st.lists(st.integers(min_value=1, max_value=15), min_size=1, max_size=20))
@settings(max_examples=100)
def test_l1_property_batches_larger_than_remaining_budget(batch_sizes):
    budget = 20
    acc = EvalAccount(budget=budget, objective=_sphere, d=2)
    for size in batch_sizes:
        try:
            acc.evaluate(np.zeros((size, 2)), MechanismTag.VIRTUOSO)
        except BudgetExhausted:
            assert acc.evals_used <= budget
            return
        assert acc.evals_used <= budget
    assert acc.evals_used <= budget


def test_l2_tag_counts_sum_to_evals_used():
    acc = EvalAccount(budget=50, objective=_sphere, d=2)
    acc.evaluate(np.zeros((3, 2)), MechanismTag.VIRTUOSO)
    acc.evaluate(np.zeros((4, 2)), MechanismTag.FINISHER)
    acc.evaluate(np.zeros((2, 2)), MechanismTag.VIRTUOSO)
    assert sum(acc.evals_by_tag.values()) == acc.evals_used


def test_l2_all_21_tags_present_with_zero_default():
    acc = EvalAccount(budget=50, objective=_sphere, d=2)
    assert set(acc.evals_by_tag.keys()) == set(ALL_TAGS)
    assert acc.evals_by_tag[MechanismTag.FORMATION] == 0


def test_l5_best_f_is_minimum_of_every_returned_value():
    rng = np.random.default_rng(0)
    acc = EvalAccount(budget=100, objective=_sphere, d=3)
    seen = []
    for _ in range(10):
        X = rng.random((5, 3))
        f = acc.evaluate(X, MechanismTag.DESTROYER)
        seen.extend(f.tolist())
    assert acc.f_best == pytest.approx(min(seen))


def test_l6_zero_cost_operations_do_not_change_evals_used():
    acc = EvalAccount(budget=50, objective=_sphere, d=2)
    acc.evaluate(np.zeros((3, 2)), MechanismTag.VIRTUOSO)
    before = acc.evals_used
    # Rollback / archive-update-only paths must not call evaluate at all.
    acc.record_zero_cost(MechanismTag.VAR_REVIEW)
    assert acc.evals_used == before
    assert acc.evals_by_tag[MechanismTag.VAR_REVIEW] == 0


def test_l7_objective_never_called_outside_unit_box():
    calls: list[np.ndarray] = []

    def spy(X):
        calls.append(X.copy())
        return _sphere(X)

    acc = EvalAccount(budget=20, objective=spy, d=2)
    with pytest.raises(ValueError):
        acc.evaluate(np.array([[1.5, 0.2]]), MechanismTag.VIRTUOSO)


def test_incumbent_survives_var_rollback_aspiration():
    """Every improving evaluation updates (x_best, f_best) inside the account, so a later VAR
    rollback of the agent's stored (X, f) cannot remove the incumbent (FR-021)."""
    acc = EvalAccount(budget=50, objective=_sphere, d=2)
    acc.evaluate(np.array([[0.1, 0.1]]), MechanismTag.VIRTUOSO)
    best_before = (acc.x_best.copy(), acc.f_best)
    # Simulate a VAR rollback happening elsewhere (Squad.rollback) -- the account is untouched.
    assert np.array_equal(acc.x_best, best_before[0])
    assert acc.f_best == best_before[1]
