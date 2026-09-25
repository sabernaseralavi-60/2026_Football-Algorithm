"""Unit tests for set pieces (tasks.md T042; mechanism-interface.md §2.14)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

import tfo.tactics.set_pieces as set_pieces
from tfo.registry import MechanismTag


class _RecordingAccount:
    def __init__(self, objective):
        self.objective = objective
        self.calls = 0
        self.x_best = None
        self.f_best = np.inf

    def evaluate(self, X, tag):
        assert tag == MechanismTag.SET_PIECES
        self.calls += X.shape[0]
        f = self.objective(X)
        for row, fx in zip(X, f):
            if fx < self.f_best:
                self.f_best = float(fx)
                self.x_best = row.copy()
        return f


def _ctx(account, h=0.1):
    return SimpleNamespace(account=account, cfg=SimpleNamespace(operators=SimpleNamespace(set_piece_h=h)))


def test_schedule_alternates_corner_then_free_kick_fixed():
    calls = []
    account = _RecordingAccount(lambda X: np.sum(X**2, axis=1))
    account.x_best = np.array([0.3, 0.3, 0.3])
    account.f_best = float(np.sum(account.x_best**2))
    ctx = _ctx(account)
    rng = np.random.default_rng(0)

    orig_corner, orig_free = set_pieces.corner, set_pieces.free_kick
    set_pieces.corner = lambda ctx, rng: calls.append("corner")
    set_pieces.free_kick = lambda ctx, rng: calls.append("free_kick")
    try:
        for call_index in range(4):
            set_pieces.apply(call_index, ctx, rng)
    finally:
        set_pieces.corner, set_pieces.free_kick = orig_corner, orig_free

    assert calls == ["corner", "free_kick", "corner", "free_kick"], (
        "the schedule and the rotation order are fixed"
    )


def test_corner_evaluates_8_new_points():
    account = _RecordingAccount(lambda X: np.sum(X**2, axis=1))
    account.x_best = np.array([0.3, 0.3, 0.3])
    account.f_best = float(np.sum(account.x_best**2))
    ctx = _ctx(account, h=0.05)
    rng = np.random.default_rng(1)
    set_pieces.corner(ctx, rng)
    assert account.calls == 8


def test_free_kick_hits_vertex_exactly_on_1d_quadratic():
    x0 = 0.37

    def objective(X):
        return (X[:, 0] - x0) ** 2

    account = _RecordingAccount(objective)
    account.x_best = np.array([0.5])
    account.f_best = float(objective(account.x_best[None, :])[0])
    ctx = _ctx(account, h=0.1)
    set_pieces.free_kick(ctx, np.random.default_rng(2))
    assert account.x_best is not None
    assert account.x_best[0] == pytest.approx(x0, abs=1e-9)
