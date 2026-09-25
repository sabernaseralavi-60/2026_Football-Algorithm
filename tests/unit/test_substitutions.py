"""Unit tests for substitutions (tasks.md T044; mechanism-interface.md §2.16)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.tactics.substitutions as substitutions
from tfo.squad import TabuRegister


class _FakeSquad:
    def __init__(self, n, d):
        self.X = np.full((n, d), 0.5)
        self.f = np.full(n, 1.0)
        self.f_P = np.full(n, 1.0)
        self.P = np.full((n, d), 0.5)
        self.stagnation = np.zeros(n, dtype=int)
        self.stamina = np.ones(n)
        self.mesh = np.full(n, 0.01)
        self.fin_fail = np.zeros(n, dtype=int)
        self.fin_last_restart = np.full(n, -1, dtype=int)
        self.d = d


def _ctx(squad, tabu, cap=2, window=5, stamina_threshold=0.5, mesh_init=0.01):
    account_calls = []

    class _Account:
        def evaluate(self, X, tag):
            account_calls.append(X.copy())
            return np.array([2.0] * X.shape[0])

    ctx = SimpleNamespace(
        squad=squad,
        tabu=tabu,
        account=_Account(),
        cfg=SimpleNamespace(
            operators=SimpleNamespace(
                substitution_window=window,
                stamina_sub_threshold=stamina_threshold,
                substitution_cap=cap,
                mesh_h_init=mesh_init,
            )
        ),
    )
    ctx.account_calls = account_calls
    return ctx


def test_both_trigger_conditions_required():
    n, d = 5, 2
    squad = _FakeSquad(n, d)
    squad.stagnation[0] = 100  # stagnated, but stamina is full -> must NOT substitute
    squad.stamina[0] = 1.0
    squad.stagnation[1] = 100
    squad.stamina[1] = 0.1  # both conditions hold -> must substitute
    tabu = TabuRegister(20, 0.02, d)
    ctx = _ctx(squad, tabu, cap=5, window=50, stamina_threshold=0.5)
    rng = np.random.default_rng(0)
    substituted = substitutions.apply(ctx, rng)
    assert 0 not in substituted
    assert 1 in substituted


def test_cap_is_honoured():
    n, d = 6, 2
    squad = _FakeSquad(n, d)
    for i in range(5):
        squad.stagnation[i] = 100
        squad.stamina[i] = 0.1
    tabu = TabuRegister(20, 0.02, d)
    ctx = _ctx(squad, tabu, cap=2, window=50, stamina_threshold=0.5)
    rng = np.random.default_rng(1)
    substituted = substitutions.apply(ctx, rng)
    assert len(substituted) <= 2


def test_tabu_entry_written_for_outgoing_position():
    n, d = 3, 2
    squad = _FakeSquad(n, d)
    squad.X[0] = [0.11, 0.22]
    squad.stagnation[0] = 100
    squad.stamina[0] = 0.1
    tabu = TabuRegister(20, 0.02, d)
    ctx = _ctx(squad, tabu, cap=5, window=50, stamina_threshold=0.5)
    rng = np.random.default_rng(2)
    substitutions.apply(ctx, rng)
    assert tabu.is_tabu(np.array([0.11, 0.22]))


def test_substitute_enters_fresh():
    n, d = 3, 2
    squad = _FakeSquad(n, d)
    squad.stagnation[0] = 100
    squad.stamina[0] = 0.1
    squad.mesh[0] = 0.5
    squad.fin_fail[0] = 3
    tabu = TabuRegister(20, 0.02, d)
    ctx = _ctx(squad, tabu, cap=5, window=50, stamina_threshold=0.5, mesh_init=0.02)
    rng = np.random.default_rng(3)
    substitutions.apply(ctx, rng)
    assert squad.stamina[0] == 1.0
    assert squad.stagnation[0] == 0
    assert squad.mesh[0] == 0.02
    assert squad.fin_fail[0] == 0
