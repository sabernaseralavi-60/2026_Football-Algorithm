"""Unit tests for pressing (tasks.md T040; mechanism-interface.md §2.12).

Squad indexing convention (data-model.md A1): index 0 is the Sweeper-Keeper; indices 1..n_out are
outfield agents. Pressing membership is drawn only from the outfield indices.
"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.tactics.pressing as pressing


class _FakeSquad:
    def __init__(self, X_outfield, f_outfield):
        n_out = X_outfield.shape[0]
        d = X_outfield.shape[1]
        self.X = np.vstack([np.zeros((1, d)), X_outfield])
        self.f = np.concatenate([[np.inf], f_outfield])
        self.n = n_out + 1

    @property
    def n_out(self) -> int:
        return self.n - 1

    def update_agent(self, i, x_new, f_new):
        self.X[i] = x_new
        self.f[i] = f_new


def test_cap_on_membership_size():
    rng = np.random.default_rng(0)
    n_out = 20
    X = rng.random((n_out, 3))
    squad = _FakeSquad(X, np.zeros(n_out))
    ball = SimpleNamespace(x_b=np.array([0.5, 0.5, 0.5]))
    # rho huge, so every agent qualifies by distance; the cap must still bind.
    ctx = SimpleNamespace(squad=squad, ball=ball, state_params=SimpleNamespace(rho=10.0))
    P = pressing.membership(ctx)
    assert len(P) <= int(0.5 * n_out)
    assert all(1 <= i <= n_out for i in P), "membership is drawn only from outfield agents"


def test_rho_zero_means_no_agent_presses():
    rng = np.random.default_rng(1)
    n_out = 10
    X = rng.random((n_out, 2))
    squad = _FakeSquad(X, np.zeros(n_out))
    ball = SimpleNamespace(x_b=np.array([0.5, 0.5]))
    ctx = SimpleNamespace(squad=squad, ball=ball, state_params=SimpleNamespace(rho=0.0))
    P = pressing.membership(ctx)
    assert P == []


def test_pressing_step_is_greedy():
    squad = _FakeSquad(np.array([[0.9, 0.9]]), np.array([100.0]))
    ball = SimpleNamespace(x_b=np.array([0.5, 0.5]))

    class _Account:
        def evaluate(self, X, tag):
            return np.array([0.0])  # always an improvement

    ctx = SimpleNamespace(
        squad=squad,
        ball=ball,
        account=_Account(),
        clock=SimpleNamespace(t=0.5),
    )
    rng = np.random.default_rng(2)
    pressing.step(1, ctx, rng)
    assert squad.f[1] == 0.0
