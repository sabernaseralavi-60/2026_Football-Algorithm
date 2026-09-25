"""Unit tests for VAR review (tasks.md T046; mechanism-interface.md §2.18)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.tactics.var_review as var_review
from tfo.squad import Squad, TabuRegister


def _squad(n=3, d=2):
    sq = Squad.initialize(n=n, d=d, rng=np.random.default_rng(0), mesh_init=0.01)
    sq.set_initial_fitness(np.array([1.0, 2.0, 3.0][:n]))
    return sq


def _ctx(squad, tabu, collision_radius=0.05):
    return SimpleNamespace(
        squad=squad,
        tabu=tabu,
        cfg=SimpleNamespace(operators=SimpleNamespace(collision_radius=collision_radius)),
    )


def test_rollback_costs_zero_evals():
    squad = _squad()
    tabu = TabuRegister(20, 0.05, squad.d)
    squad.X[0] = np.array([0.9, 0.9])
    squad.f[0] = 0.5
    squad.moved_since_rev[0] = True
    tabu.add(np.array([0.9, 0.9]))  # agent 0's new position is inside a tabu zone

    calls = []

    class _Account:
        def evaluate(self, X, tag):
            calls.append(X)
            raise AssertionError("VAR rollback must not evaluate")

    ctx = _ctx(squad, tabu)
    var_review.apply(ctx)
    assert not calls, "the rollback costs 0 evals"
    assert np.array_equal(squad.X[0], squad.X_rev[0]), "the agent was rolled back"


def test_aspiration_keeps_a_move_that_set_a_new_best():
    squad = _squad()
    tabu = TabuRegister(20, 0.05, squad.d)
    squad.X[0] = np.array([0.9, 0.9])
    squad.f[0] = 0.01  # a new best
    squad.moved_since_rev[0] = True
    squad.produced_best_since_rev[0] = True
    tabu.add(np.array([0.9, 0.9]))  # would otherwise fail the tabu check

    ctx = _ctx(squad, tabu)
    var_review.apply(ctx)
    assert np.array_equal(squad.X[0], [0.9, 0.9]), "aspiration keeps the move despite the flag"


def test_incumbent_survives_any_rollback():
    """The incumbent lives in EvalAccount (x_best/f_best), untouched by Squad.rollback -- this is
    exercised directly in test_account.py's aspiration test; VAR review itself never writes to the
    account at all (0 evals), so it cannot touch the incumbent."""
    squad = _squad()
    tabu = TabuRegister(20, 0.05, squad.d)
    squad.X[1] = np.array([0.9, 0.9])
    squad.f[1] = 50.0
    squad.moved_since_rev[1] = True
    tabu.add(np.array([0.9, 0.9]))
    ctx = _ctx(squad, tabu)
    var_review.apply(ctx)
    assert not hasattr(ctx, "account"), "var_review never touches EvalAccount"


def test_review_refreshes_snapshot_afterward():
    squad = _squad()
    tabu = TabuRegister(20, 0.05, squad.d)
    squad.moved_since_rev[0] = True
    ctx = _ctx(squad, tabu)
    var_review.apply(ctx)
    assert not np.any(squad.moved_since_rev)
    assert not np.any(squad.produced_best_since_rev)
    assert np.array_equal(squad.X_rev, squad.X)
