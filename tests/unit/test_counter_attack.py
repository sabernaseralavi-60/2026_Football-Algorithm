"""Unit tests for counter-attack (tasks.md T041; mechanism-interface.md §2.13)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

import tfo.tactics.counter_attack as counter_attack
from tfo.account import BudgetExhausted, EvalAccount
from tfo.squad import Ball, TabuRegister
from tfo.tactics.formation import Formation


def _ops(**overrides):
    base = dict(
        counter_attack_delta_mat=1e-4,
        counter_attack_d_trans=0.1,
        burst_len=4,
        burst_gamma=0.5,
        burst_s0=0.1,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


class _FakeSquad:
    def __init__(self, X, f):
        self.X = X
        self.f = f
        self.d = X.shape[1]
        self.slot = np.arange(X.shape[0])

    def update_agent(self, i, x_new, f_new):
        self.X[i] = x_new
        self.f[i] = f_new


def test_trigger_requires_both_improvement_and_distance():
    ball = Ball(x_b=np.array([0.5, 0.5]), f_b=1.0, carrier=0)
    ctx = SimpleNamespace(ball=ball, cfg=SimpleNamespace(operators=_ops()), tabu=TabuRegister(20, 0.02, 2))

    # Improves enough but too close (distance <= d_trans): must not trigger.
    assert not counter_attack.check_trigger(y=np.array([0.55, 0.5]), f_y=0.0, ball=ball, ops=ctx.cfg.operators)
    # Far enough but does not improve enough (delta_mat = 1e-4, so 0.99995 is too small a gain):
    # must not trigger.
    assert not counter_attack.check_trigger(
        y=np.array([0.95, 0.95]), f_y=0.99995, ball=ball, ops=ctx.cfg.operators
    )
    # Both hold: must trigger.
    assert counter_attack.check_trigger(y=np.array([0.95, 0.95]), f_y=0.0, ball=ball, ops=ctx.cfg.operators)


def test_burst_step_sizes_decay_geometrically():
    steps = [counter_attack.burst_step_scale(k, s0=0.1, gamma=0.5) for k in range(4)]
    for a, b in zip(steps, steps[1:]):
        assert b == pytest.approx(a * 0.5)


def test_burst_truncated_exactly_at_budget():
    formation = Formation.build("compact", n_out=29)
    n = 29
    X = np.full((n, 2), 0.5)
    f = np.full(n, 1.0)
    squad = _FakeSquad(X, f)
    ball = Ball(x_b=np.array([0.5, 0.5]), f_b=1.0, carrier=0)
    tabu = TabuRegister(20, 0.02, 2)

    account = EvalAccount(budget=2, objective=lambda X: np.sum(X**2, axis=1), d=2)
    ctx = SimpleNamespace(
        squad=squad,
        ball=ball,
        formation=formation,
        account=account,
        tabu=tabu,
        cfg=SimpleNamespace(operators=_ops(burst_len=10)),
    )
    rng = np.random.default_rng(0)
    y = np.array([0.95, 0.95])
    with pytest.raises(BudgetExhausted):
        counter_attack.fire(0, y, 0.0, ctx, rng)
    assert account.evals_used <= 2
