"""Integration test (T106; contract C2): two runs with the same `(view, budget, seed)` give
bit-identical ledger outputs on the reference environment, with `NPY_DISABLE_CPU_FEATURES` fixed
(research.md R20)."""

from __future__ import annotations

import os

import numpy as np
import pytest

from tfo_bench.algorithms.cmaes import CMAESAdapter
from tfo_bench.algorithms.lshade import LSHADEAdapter
from tfo_bench.algorithms.sibling import CAAdapter, GAAdapter, GWOAdapter, PSOAdapter
from tfo_bench.algorithms.tfo_adapter import TFOAdapter
from tfo_bench.algorithms.woa import WOAAdapter
from tfo_bench.ledger import CountingObjective
from tfo_bench.problems.base import Problem, ProblemView

D = 6
BUDGET = 350
SEED = 555


@pytest.fixture(autouse=True)
def _fixed_cpu_features(monkeypatch):
    # research.md R20: NPY_DISABLE_CPU_FEATURES fixed in the runner to exclude AVX-512 dispatch,
    # so SIMD-dispatched transcendental functions don't differ in the last ULP between runs.
    monkeypatch.setenv("NPY_DISABLE_CPU_FEATURES", "AVX512F AVX512CD AVX512_SKX")


def _make_view():
    problem = Problem(
        problem_id="repro_test",
        suite="tuning",
        name="rastrigin_like",
        D=D,
        lb=-100.0,
        ub=100.0,
        f_star=0.0,
        fn=lambda X: np.sum(np.atleast_2d(X) ** 2 - 10 * np.cos(2 * np.pi * np.atleast_2d(X)) + 10, axis=1),
    )
    ledger = CountingObjective(problem, BUDGET)
    return ProblemView(ledger, problem, "main"), ledger


@pytest.mark.parametrize(
    "factory",
    [TFOAdapter, CAAdapter, GAAdapter, PSOAdapter, GWOAdapter, WOAAdapter, LSHADEAdapter, CMAESAdapter],
    ids=["TFO", "CA", "GA", "PSO", "GWO", "WOA", "L-SHADE", "CMA-ES (IPOP)"],
)
def test_two_runs_same_view_budget_seed_give_bit_identical_ledger_outputs(factory):
    view1, ledger1 = _make_view()
    factory().run(view1, BUDGET, SEED)

    view2, ledger2 = _make_view()
    factory().run(view2, BUDGET, SEED)

    assert ledger1.evals_used == ledger2.evals_used
    assert ledger1.best_f == ledger2.best_f
    np.testing.assert_array_equal(ledger1.best_u, ledger2.best_u)
    np.testing.assert_array_equal(ledger1.curve, ledger2.curve)
