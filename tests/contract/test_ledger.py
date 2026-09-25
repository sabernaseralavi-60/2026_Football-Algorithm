"""Contract test for `tfo_bench.ledger.CountingObjective` (T065; evaluation-ledger.md invariants
L3, L4)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tfo_bench.ledger import BudgetExhausted, CountingObjective


class _SphereProblem:
    """Minimal stand-in for `tfo_bench.problems.base.Problem`: unit-box in, real f out."""

    def __init__(self, D: int, f_star: float = 0.0):
        self.D = D
        self.f_star = f_star

    def evaluate_unit(self, U: np.ndarray) -> np.ndarray:
        U = np.atleast_2d(U)
        X = 200.0 * U - 100.0  # decode to [-100, 100]^D, matching the CEC convention
        return np.sum(X**2, axis=1)


def test_L4_curve_has_100_nonincreasing_entries_at_exact_checkpoints():
    D, budget = 5, 137
    rng = np.random.default_rng(0)
    ledger = CountingObjective(_SphereProblem(D), budget)

    evals_done = 0
    while True:
        remaining = budget - evals_done
        if remaining <= 0:
            break
        batch = rng.integers(1, 7)
        U = rng.random((batch, D))
        try:
            ledger(U)
            evals_done += batch
        except BudgetExhausted:
            break

    assert ledger.evals_used == budget
    assert ledger.curve.shape == (100,)
    # non-increasing
    assert np.all(np.diff(ledger.curve) <= 1e-12)
    # no entry left at the sentinel +inf
    assert np.all(np.isfinite(ledger.curve))


def test_L4_checkpoint_k_is_bestsofar_after_ceil_k_budget_over_100():
    D, budget = 3, 250
    problem = _SphereProblem(D)
    rng = np.random.default_rng(1)
    U_all = rng.random((budget, D))
    f_all = problem.evaluate_unit(U_all)
    best_so_far = np.minimum.accumulate(f_all)

    ledger = CountingObjective(problem, budget)
    for row in U_all:
        try:
            ledger(row[None, :])
        except BudgetExhausted:
            pass

    for k in range(1, 101):
        target = int(np.ceil(k * budget / 100))
        expected = best_so_far[target - 1] - problem.f_star
        assert ledger.curve[k - 1] == pytest.approx(expected)


def test_L3_truncation_exactly_at_budget_then_raises():
    D, budget = 4, 10
    ledger = CountingObjective(_SphereProblem(D), budget)
    rng = np.random.default_rng(2)

    # A batch of 6 fits.
    ledger(rng.random((6, D)))
    assert ledger.evals_used == 6

    # A batch of 6 more only has room for 4: it must evaluate exactly the first 4 rows, record
    # them, and then raise BudgetExhausted -- not silently clip and continue.
    with pytest.raises(BudgetExhausted):
        ledger(rng.random((6, D)))
    assert ledger.evals_used == budget

    # Once exhausted, even a batch of size 0 evaluations raises immediately without evaluating.
    with pytest.raises(BudgetExhausted):
        ledger(rng.random((1, D)))
    assert ledger.evals_used == budget


def test_C3_rejects_rows_outside_unit_box():
    ledger = CountingObjective(_SphereProblem(2), 100)
    with pytest.raises(ValueError):
        ledger(np.array([[1.5, 0.2]]))
    with pytest.raises(ValueError):
        ledger(np.array([[-0.1, 0.2]]))


@given(
    budget=st.integers(min_value=1, max_value=50),
    batches=st.lists(st.integers(min_value=1, max_value=20), min_size=1, max_size=20),
)
@settings(max_examples=50, deadline=None)
def test_L1_evals_used_never_exceeds_budget_property(budget, batches):
    D = 2
    ledger = CountingObjective(_SphereProblem(D), budget)
    rng = np.random.default_rng(42)
    for b in batches:
        try:
            ledger(rng.random((b, D)))
        except BudgetExhausted:
            pass
        assert ledger.evals_used <= budget
    assert ledger.evals_used <= budget
