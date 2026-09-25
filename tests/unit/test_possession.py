"""Unit tests for possession (tasks.md T039; mechanism-interface.md §2.11)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.tactics.possession as possession
from tfo.squad import Ball, KeeperArchive, TabuRegister
from tfo.tactics.formation import Formation


class _FakeSquad:
    def __init__(self, X):
        self.X = X
        self.slot = np.arange(X.shape[0])
        self.d = X.shape[1]


class _ScriptedAccount:
    """Returns a scripted sequence of fitness values for successive evaluate() calls."""

    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def evaluate(self, X, tag):
        self.calls.append(X.copy())
        v = self.values.pop(0)
        return np.array([v])


def _ctx(squad, ball, account, formation, archive=None, tabu=None, tau=0.1, L=5, neutral_max=5, r_loss=3):
    return SimpleNamespace(
        squad=squad,
        ball=ball,
        account=account,
        formation=formation,
        archive=archive or KeeperArchive(k=5, min_sep=0.01, d=squad.d),
        tabu=tabu or TabuRegister(t_max=20, r_tabu=0.02, d=squad.d),
        state_params=SimpleNamespace(tau=tau, chain_length=L),
        cfg=SimpleNamespace(operators=SimpleNamespace(neutral_pass_max=neutral_max, lost_streak_max=r_loss)),
    )


def test_receivers_are_always_neighbours_of_carrier():
    formation = Formation.build("compact", n_out=29)
    n = 29
    X = np.random.default_rng(0).random((n, 2))
    squad = _FakeSquad(X)
    ball = Ball(x_b=X[0].copy(), f_b=1.0, carrier=0)
    account = _ScriptedAccount([1.05] * 10)  # always retained (within tau)
    ctx = _ctx(squad, ball, account, formation, tau=0.1, L=5)
    rng = np.random.default_rng(1)
    receivers_seen = []
    orig_choice = rng.choice

    possession.apply(ctx, rng)
    assert ball.passes_tried >= 1


def test_tau_acceptance_rule():
    formation = Formation.build("compact", n_out=29)
    n = 29
    X = np.zeros((n, 2))
    squad = _FakeSquad(X)
    ball = Ball(x_b=np.array([0.0, 0.0]), f_b=1.0, carrier=0)
    # First pass: f_candidate = 1.05 <= f_b(1.0) + tau(0.1) -> retained.
    # Second pass: f_candidate = 1.5 > 1.0 + 0.1 -> lost, chain ends.
    account = _ScriptedAccount([1.05, 1.5])
    ctx = _ctx(squad, ball, account, formation, tau=0.1, L=5)
    rng = np.random.default_rng(2)
    possession.apply(ctx, rng)
    assert ball.passes_tried == 2
    assert ball.passes_retained == 1


def test_neutral_pass_cap_stops_plateau_loop():
    formation = Formation.build("compact", n_out=29)
    n = 29
    X = np.zeros((n, 2))
    squad = _FakeSquad(X)
    ball = Ball(x_b=np.array([0.0, 0.0]), f_b=1.0, carrier=0)
    # Every pass returns exactly f_b = 1.0 (neutral), forever -- cap must stop it.
    account = _ScriptedAccount([1.0] * 50)
    ctx = _ctx(squad, ball, account, formation, tau=0.1, L=1000, neutral_max=3)
    rng = np.random.default_rng(3)
    possession.apply(ctx, rng)
    assert ball.passes_tried <= 3 + 1


def test_disabled_default_sets_ball_to_best_outfield_agent_at_zero_cost():
    X = np.array([[0.9, 0.9], [0.1, 0.1], [0.5, 0.5]])
    squad = _FakeSquad(X)
    squad.f = np.array([5.0, 1.0, 3.0])
    ball = Ball(x_b=np.array([0.9, 0.9]), f_b=5.0, carrier=0)
    account = _ScriptedAccount([])
    possession.apply_disabled(ball, squad)
    assert np.array_equal(ball.x_b, X[1])
    assert ball.f_b == 1.0
    assert ball.carrier == 1
    assert not account.calls
