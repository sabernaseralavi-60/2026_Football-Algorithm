"""Golden test: every tuning function passes the preflight audit at its known optimum (T077).

Preflight tolerance quoted verbatim from research.md R12: "|f(x*) - f*| <= 1e-6*max(1, |f*|)".
"""

from __future__ import annotations

import numpy as np
import pytest

from tfo_bench.problems import tuning

PREFLIGHT_TOLERANCE = 1e-6


def _preflight_ok(problem) -> tuple[bool, float]:
    f_at_xstar = float(problem.evaluate(problem.x_star[None, :])[0])
    tol = PREFLIGHT_TOLERANCE * max(1.0, abs(problem.f_star))
    return abs(f_at_xstar - problem.f_star) <= tol, f_at_xstar


@pytest.mark.parametrize("D", tuning.DIMS)
def test_unconstrained_tuning_functions_pass_preflight(D):
    problems = tuning.build_problems(D)
    assert len(problems) == 7
    for name, problem in problems.items():
        ok, f_at_xstar = _preflight_ok(problem)
        assert ok, f"{name} D={D}: f(x*)={f_at_xstar} vs f*={problem.f_star}"


def test_constrained_tuning_problems_pass_preflight_and_are_feasible():
    problems = tuning.build_constrained_problems()
    assert set(problems) == {"G04", "TubularColumn"}
    for name, problem in problems.items():
        ok, f_at_xstar = _preflight_ok(problem)
        assert ok, f"{name}: f(x*)={f_at_xstar} vs f*={problem.f_star}"
        G = problem.constraints_real(problem.x_star[None, :])[0]
        assert np.all(G <= 1e-6), f"{name}: x* violates constraints {G}"


def test_tuning_dimensions_and_functions_are_disjoint_from_test_suites():
    # FR-040 / data-model.md B3: the tuning dims {15, 40} and function list must not collide with
    # any test-suite (cell_id) dimension/name.
    from tfo_bench.problems import cec2017, cec2022

    test_dims = {30} | set(cec2022.SUPPORTED_DIMS)  # {30, 10, 20}
    assert test_dims.isdisjoint(tuning.DIMS)

    test_names = set(cec2017.OFFICIAL_NUMBERS) | set(cec2022.NUMBERS)
    tuning_names = {spec.name for spec in tuning._TUNING_SPECS} | {"G04", "TubularColumn"}
    # names live in different namespaces (ints vs strings) by construction, but check no accidental
    # collision through string reuse:
    assert not tuning_names & {str(n) for n in test_names}
