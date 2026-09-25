"""Unit tests for the Destroyer (tasks.md T026; mechanism-interface.md §2.6)."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np

import tfo.archetypes.destroyer as destroyer
from tfo.tactics.formation import Formation


class _FakeSquad:
    def __init__(self, X, f, slot):
        self.X = X
        self.f = f
        self.slot = slot
        self.stamina = np.ones(X.shape[0])
        self.d = X.shape[1]
        self.moved = []

    def update_agent(self, i, x_new, f_new):
        self.moved.append(i)
        self.X[i] = x_new
        self.f[i] = f_new


class _FakeAccount:
    def evaluate(self, X, tag):
        return np.sum(X**2, axis=1)


class _FakeOperators:
    de_f = 0.5
    niche_radius = 0.5  # large, to guarantee the pair counts as a niche collision
    neutral_sigma = 0.1


def _ctx(squad):
    return SimpleNamespace(
        squad=squad,
        formation=Formation.build("compact", n_out=29),
        account=_FakeAccount(),
        cfg=SimpleNamespace(operators=_FakeOperators()),
    )


def test_better_member_of_pair_never_moved():
    formation = Formation.build("compact", n_out=29)
    slot_i = 0
    neighbour_slots = formation.neighbours[slot_i]
    assert neighbour_slots, "compact formation slot 0 must have at least one neighbour"
    slot_j = neighbour_slots[0]

    n = formation.n_slots
    slot = np.arange(n)  # agent k occupies slot k, for simplicity
    X = np.full((n, 2), 0.5)
    # Give every neighbour of slot_i a distinct position, so the kick's differential vector
    # (drawn from two of them) is generically nonzero.
    for offset, s in enumerate(neighbour_slots):
        X[s] = [0.1 * (offset + 1), 0.9 - 0.1 * offset]
    X[slot_i] = [0.50, 0.50]
    X[slot_j] = [0.51, 0.50]  # very close: within niche radius
    f = np.full(n, 100.0)
    f[slot_i] = 1.0  # agent at slot_i is BETTER (lower f)
    f[slot_j] = 5.0  # agent at slot_j is WORSE

    squad = _FakeSquad(X.copy(), f.copy(), slot)
    rng = np.random.default_rng(0)
    destroyer.move(slot_i, _ctx(squad), rng)

    assert slot_i not in squad.moved, "the better member of each pair is never moved"
    assert slot_j in squad.moved, "the worse member is kicked"
    assert not np.array_equal(squad.X[slot_j], [0.51, 0.50])


def test_neutral_fallback_when_no_pair_within_niche():
    formation = Formation.build("compact", n_out=29)
    slot_i = 0
    n = formation.n_slots
    slot = np.arange(n)
    X = rng_positions(n)
    X[slot_i] = 0.1
    for s in formation.neighbours[slot_i]:
        X[s] = 0.9  # far away: no niche collision
    f = np.full(n, 1.0)
    squad = _FakeSquad(X.copy(), f.copy(), slot)
    ctx = _ctx(squad)
    ctx.cfg.operators.niche_radius = 0.001  # tiny, so nothing collides
    rng = np.random.default_rng(1)
    destroyer.move(slot_i, ctx, rng)
    assert slot_i in squad.moved, "falls back to the neutral move N when idle"


def rng_positions(n):
    return np.full((n, 2), 0.5)
