"""Unit tests for the Virtuoso compass poll (tasks.md T027; mechanism-interface.md §2.7)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.archetypes.virtuoso as virtuoso


class _FakeSquad:
    def __init__(self, x, mesh):
        self.X = np.array([x])
        self.f = np.array([np.sum(x**2)])
        self.mesh = np.array([mesh])
        self.stamina = np.array([1.0])
        self.d = x.shape[0]

    def update_agent(self, i, x_new, f_new):
        self.X[i] = x_new
        self.f[i] = f_new


class _FakeAccount:
    def __init__(self):
        self.calls = []

    def evaluate(self, X, tag):
        self.calls.append(X.copy())
        return np.sum(X**2, axis=1)


def _ctx(squad, account, k=2, h_min=1e-6, h_max=0.5):
    return SimpleNamespace(
        squad=squad,
        account=account,
        cfg=SimpleNamespace(
            operators=SimpleNamespace(mesh_k=k, mesh_h_min=h_min, mesh_h_max=h_max)
        ),
    )


def test_mesh_expands_on_success_and_stays_in_bounds():
    # x has a negative coordinate; stepping further negative on that coordinate improves sum of
    # squares only if it moves toward 0. Use x = [0.5, 0.5]; stepping -h on coord 0 improves.
    x = np.array([0.5, 0.5])
    squad = _FakeSquad(x, mesh=0.1)
    ctx = _ctx(squad, _FakeAccount())
    rng = np.random.default_rng(0)
    virtuoso.move(0, ctx, rng)
    assert squad.mesh[0] == min(2 * 0.1, 0.5), "on success, h_i <- min(2 h_i, h_max)"
    assert squad.mesh[0] <= 0.5


def test_mesh_contracts_when_whole_poll_fails():
    # x = [0, 0] is the sphere's minimum: every poll step in either direction makes it worse.
    x = np.array([0.0, 0.0])
    squad = _FakeSquad(x, mesh=0.1)
    ctx = _ctx(squad, _FakeAccount())
    rng = np.random.default_rng(0)
    virtuoso.move(0, ctx, rng)
    assert squad.mesh[0] == max(0.1 / 2, 1e-6), "on failure, h_i <- max(h_i/2, h_min)"
    assert np.array_equal(squad.X[0], x), "a failed poll does not move the agent"


def test_mesh_never_leaves_bounds():
    x = np.array([0.0, 0.0])
    squad = _FakeSquad(x, mesh=1e-6)
    ctx = _ctx(squad, _FakeAccount(), h_min=1e-6, h_max=0.5)
    rng = np.random.default_rng(0)
    virtuoso.move(0, ctx, rng)
    assert squad.mesh[0] >= 1e-6


def test_poll_stops_at_first_improvement():
    x = np.array([0.5, 0.5, 0.5])
    squad = _FakeSquad(x, mesh=0.1)
    account = _FakeAccount()
    ctx = _ctx(squad, account, k=3)
    rng = np.random.default_rng(0)
    virtuoso.move(0, ctx, rng)
    # x = [0.5]*3 is symmetric under coordinate choice: the +h probe always worsens sum-of-squares
    # and the -h probe always improves it, so the poll must stop after exactly 2 evaluate() calls
    # (the failed +h probe, then the successful -h probe on the same coordinate), never continuing
    # to a second coordinate.
    assert len(account.calls) == 2, "the poll stops at the first improvement"
