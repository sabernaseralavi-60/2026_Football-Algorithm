"""Contract test for the optimizer interface (T078), parametrised over all 9 roster adapters
(optimizer-interface.md §3, invariants C1-C6, C8)."""

from __future__ import annotations

import numpy as np
import pytest

from tfo_bench.algorithms.base import ROSTER_LABELS
from tfo_bench.algorithms.cmaes import CMAESAdapter
from tfo_bench.algorithms.lshade import LSHADEAdapter
from tfo_bench.algorithms.sibling import CAAdapter, GAAdapter, GWOAdapter, PSOAdapter
from tfo_bench.algorithms.tfo_adapter import TFOAdapter, static_adapter
from tfo_bench.algorithms.woa import WOAAdapter
from tfo_bench.ledger import CountingObjective
from tfo_bench.problems.base import Problem, ProblemView

D = 5
BUDGET = 400
SEED = 20260925


def _sphere_problem() -> Problem:
    return Problem(
        problem_id="contract_test_sphere",
        suite="tuning",
        name="sphere",
        D=D,
        lb=-100.0,
        ub=100.0,
        f_star=0.0,
        fn=lambda X: np.sum(np.atleast_2d(X) ** 2, axis=1),
    )


def _make_view(experiment="main"):
    problem = _sphere_problem()
    ledger = CountingObjective(problem, BUDGET)
    return ProblemView(ledger, problem, experiment), ledger


def _adapter_factories():
    return {
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


ADAPTER_FACTORIES = _adapter_factories()


def test_all_9_roster_labels_covered():
    assert set(ADAPTER_FACTORIES) == set(ROSTER_LABELS)


@pytest.fixture(params=list(ADAPTER_FACTORIES.items()), ids=list(ADAPTER_FACTORIES))
def adapter_and_result(request):
    label, factory = request.param
    adapter = factory()
    view, ledger = _make_view()
    result = adapter.run(view, BUDGET, SEED)
    return label, adapter, result, ledger


def test_C1_evals_used_at_most_budget_and_equals_budget_unless_self_terminated(adapter_and_result):
    label, adapter, result, ledger = adapter_and_result
    assert ledger.evals_used <= BUDGET
    if result.status != "self_terminated":
        assert ledger.evals_used == BUDGET, f"{label}: status=ok but evals_used={ledger.evals_used}"


def test_C4_algo_reported_best_f_never_beats_the_ledger(adapter_and_result):
    label, adapter, result, ledger = adapter_and_result
    if result.algo_reported_best_f is not None:
        tol = 1e-12 * max(1.0, abs(ledger.best_f))
        assert result.algo_reported_best_f >= ledger.best_f - tol, (
            f"{label}: algo claimed {result.algo_reported_best_f} < ledger.best_f "
            f"{ledger.best_f} (an algorithm cannot claim a value it never evaluated)"
        )


def test_C5_no_exception_other_than_handled_ones_escapes():
    # Implicit: adapter_and_result fixture above already calls .run() for every adapter; if any
    # exception other than BudgetExhausted escaped, the fixture itself would fail. This test
    # exists to document C5 as a named, explicit check.
    for label, factory in ADAPTER_FACTORIES.items():
        adapter = factory()
        view, ledger = _make_view()
        result = adapter.run(view, BUDGET, SEED)
        assert result.status in ("ok", "self_terminated")


def test_C2_determinism_same_view_budget_seed_gives_bit_identical_ledger_outputs():
    for label, factory in ADAPTER_FACTORIES.items():
        view1, ledger1 = _make_view()
        factory().run(view1, BUDGET, SEED)

        view2, ledger2 = _make_view()
        factory().run(view2, BUDGET, SEED)

        assert ledger1.evals_used == ledger2.evals_used, label
        assert ledger1.best_f == ledger2.best_f, label
        np.testing.assert_array_equal(ledger1.curve, ledger2.curve)


def test_C8_TFO_family_mechanism_evals_sum_to_ledger_evals_used():
    for label in ("TFO", "TFO-static"):
        adapter = ADAPTER_FACTORIES[label]()
        view, ledger = _make_view()
        result = adapter.run(view, BUDGET, SEED)
        total = sum(result.extras["evals_by_mechanism"].values())
        assert total == ledger.evals_used, label


class _RecordingLedger(CountingObjective):
    """A `CountingObjective` that also records every `U` it was called with, so the test can
    inspect the *actual* first rows an algorithm asked to evaluate."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls: list[np.ndarray] = []

    def __call__(self, U):
        self.calls.append(np.atleast_2d(np.asarray(U, dtype=float)).copy())
        return super().__call__(U)


def test_C6_shared_initial_population_TFO_GA_PSO_GWO_CA():
    """TFO and the vendored GA, PSO, GWO and CA all make `default_rng(seed).random((30, D))`
    their first draw (contract C6; research.md R11): with a budget of exactly 30 (one population),
    the first (and only, since the next call is truncated to 0 rows and raises) batch each
    actually evaluates must be exactly that draw."""
    expected_first_30 = np.random.default_rng(SEED).random((30, D))
    small_budget = 30

    factories = {
        "TFO": lambda: TFOAdapter(),
        "GA": GAAdapter,
        "PSO": PSOAdapter,
        "GWO": GWOAdapter,
        "CA": CAAdapter,
    }
    for label, factory in factories.items():
        problem = _sphere_problem()
        ledger = _RecordingLedger(problem, small_budget)
        view = ProblemView(ledger, problem, "main")
        factory().run(view, small_budget, SEED)

        assert ledger.calls, f"{label}: no evaluation was recorded"
        first_call_first_30 = ledger.calls[0][:30]
        np.testing.assert_array_equal(
            first_call_first_30, expected_first_30, err_msg=f"{label}: first draw mismatch"
        )
