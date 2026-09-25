"""Contract test for information parity (T069; C7)."""

from __future__ import annotations

import numpy as np
import pytest

from tfo_bench.ledger import CountingObjective
from tfo_bench.problems.base import CapabilityError, Problem, ProblemView


def _make_view(experiment: str) -> ProblemView:
    problem = Problem(
        problem_id="engineering_WeldedBeam",
        suite="engineering",
        name="WeldedBeam",
        D=4,
        lb=np.array([0.1, 0.1, 0.1, 0.1]),
        ub=np.array([2.0, 10.0, 10.0, 2.0]),
        f_star=1.7249,
        fn=lambda X: np.sum(X, axis=1),
        implementation="test-double",
        has_constraints=True,
        constraints_fn=lambda X: np.zeros((X.shape[0], 7)),
    )
    ledger = CountingObjective(problem, budget=1000)
    return ProblemView(ledger, problem, experiment)


@pytest.mark.parametrize("experiment", ["main", "ablation", "sensitivity", "tuning", "pilot"])
def test_constraints_raises_capability_error_unless_epsilon(experiment):
    view = _make_view(experiment)
    with pytest.raises(CapabilityError):
        _ = view.constraints


def test_constraints_available_for_epsilon_experiment():
    view = _make_view("epsilon")
    g = view.constraints(np.full((3, 4), 0.5))
    assert g.shape == (3, 7)
