"""Unit tests for the Finisher (tasks.md T028; mechanism-interface.md §2.8)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.archetypes.finisher as finisher
from tfo.squad import Ball, KeeperArchive


class _FakeSquad:
    def __init__(self, n=1, d=2):
        self.X = np.full((n, d), 0.2)
        self.f = np.full(n, 10.0)
        self.stamina = np.ones(n)
        self.fin_fail = np.zeros(n, dtype=int)
        self.fin_last_restart = np.full(n, -1, dtype=int)
        self.d = d

    def update_agent(self, i, x_new, f_new):
        self.X[i] = x_new
        self.f[i] = f_new


class _FakeAccount:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def evaluate(self, X, tag):
        self.calls.append(X.copy())
        v = self.values.pop(0)
        return np.array([v])


def _ctx(squad, ball, archive, account, F_fail=3):
    return SimpleNamespace(
        squad=squad,
        ball=ball,
        archive=archive,
        account=account,
        cfg=SimpleNamespace(
            operators=SimpleNamespace(
                levy_beta=1.5, levy_sigma=0.0, finisher_fail_limit=F_fail
            )
        ),
    )


def test_jump_is_centred_on_the_ball_not_the_incumbent():
    squad = _FakeSquad()
    ball = Ball(x_b=np.array([0.7, 0.8]), f_b=1.0, carrier=0)
    archive = KeeperArchive(k=5, min_sep=0.05, d=2)
    account = _FakeAccount(values=[20.0])  # worse than current f=10, so no accept
    ctx = _ctx(squad, ball, archive, account)
    rng = np.random.default_rng(0)
    finisher.move(0, ctx, rng)
    assert np.allclose(account.calls[0][0], ball.x_b), "jumps are centred on the ball"


def test_restart_never_reuses_last_restart_index():
    squad = _FakeSquad()
    ball = Ball(x_b=np.array([0.5, 0.5]), f_b=1.0, carrier=0)
    archive = KeeperArchive(k=5, min_sep=0.01, d=2)
    rng_seed = np.random.default_rng(1)
    for idx, (x, f) in enumerate(
        [
            (np.array([0.1, 0.1]), 5.0),
            (np.array([0.9, 0.9]), 4.0),
            (np.array([0.1, 0.9]), 3.0),
            (np.array([0.9, 0.1]), 2.0),
        ]
    ):
        archive.on_evaluation(x, f, is_new_incumbent=(idx == 0))
    assert archive.size >= 3

    squad.fin_fail[0] = 2  # one more failure triggers the first restart (F_fail = 3)
    account = _FakeAccount(values=[100.0, 50.0])  # jump fails, then the restart's own evaluation
    ctx = _ctx(squad, ball, archive, account, F_fail=3)
    rng = np.random.default_rng(2)
    finisher.move(0, ctx, rng)
    assert squad.fin_fail[0] == 0, "a restart resets the failure counter"
    first_restart_idx = squad.fin_last_restart[0]
    assert first_restart_idx != -1

    squad.fin_fail[0] = 2
    account2 = _FakeAccount(values=[100.0, 60.0])
    ctx2 = _ctx(squad, ball, archive, account2, F_fail=3)
    finisher.move(0, ctx2, rng)
    second_restart_idx = squad.fin_last_restart[0]
    assert second_restart_idx != first_restart_idx, "a restart never reuses the last restart index"
