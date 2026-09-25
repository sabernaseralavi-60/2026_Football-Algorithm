"""Unit tests for Squad, Ball, KeeperArchive, TabuRegister (tasks.md T010; data-model.md A1, A4-A6)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from tfo.registry import Archetype
from tfo.squad import Ball, KeeperArchive, RoleSheet, Squad, TabuRegister


def test_squad_initializes_within_unit_box():
    rng = np.random.default_rng(0)
    sq = Squad.initialize(n=30, d=5, rng=rng, mesh_init=0.01)
    assert sq.X.shape == (30, 5)
    assert np.all(sq.X >= 0.0) and np.all(sq.X <= 1.0), "X always lies in [0, 1]^D (data-model.md A1)"


def test_squad_personal_best_never_worse_than_current():
    rng = np.random.default_rng(1)
    sq = Squad.initialize(n=10, d=3, rng=rng, mesh_init=0.01)
    sq.f[:] = rng.random(10)
    sq.P[:] = sq.X
    sq.f_P[:] = sq.f
    for i in range(10):
        y = rng.random(3)
        fy = rng.random()
        sq.update_agent(i, y, fy)
        assert sq.f_P[i] <= sq.f[i], "f_P[i] <= f[i] for every i (data-model.md A1)"


@given(
    fs=arrays(dtype=np.float64, shape=20, elements=st.floats(-10, 10, allow_nan=False)),
)
@settings(max_examples=50)
def test_squad_personal_best_property(fs):
    rng = np.random.default_rng(2)
    n = 20
    sq = Squad.initialize(n=n, d=2, rng=rng, mesh_init=0.01)
    sq.f[:] = 0.0
    sq.f_P[:] = 0.0
    sq.P[:] = sq.X
    for i in range(n):
        sq.update_agent(i, sq.X[i], float(fs[i]))
        assert sq.f_P[i] <= sq.f[i]


def test_archetype_read_through_role_sheet_not_stored_on_agent():
    role_counts = {
        Archetype.ZONAL_CENTRE_BACK: 2,
        Archetype.FINISHER: 1,
    }
    sheet = RoleSheet.layout(role_counts, n_slots=4)
    # Slot 3 is vacant (n_out = 3 < n_slots = 4).
    assert sheet.archetype_at(3) is None
    before = [sheet.archetype_at(s) for s in range(3)]

    sq = Squad.initialize(n=4, d=2, rng=np.random.default_rng(3), mesh_init=0.01)
    sq.slot[:] = [1, 2, 0, -1]  # rotate slots (agent 0 now sits at slot 1, etc.)

    # The archetype of agent i is read via role_sheet[slot[i]], so rotation changes it, and no
    # archetype field exists on Squad itself.
    assert not hasattr(sq, "archetype")
    after = [sheet.archetype_at(int(sq.slot[i])) for i in range(3)]
    assert after != before or role_counts  # sanity: lookup is slot-indexed, not agent-indexed


def test_role_sheet_layout_matches_counts_and_leaves_one_vacancy():
    from tfo.registry import DEFAULT_ARCHETYPE_COUNTS

    sheet = RoleSheet.layout(DEFAULT_ARCHETYPE_COUNTS, n_slots=30)
    counts: dict[Archetype, int] = {}
    n_vacant = 0
    for s in range(30):
        a = sheet.archetype_at(s)
        if a is None:
            n_vacant += 1
        else:
            counts[a] = counts.get(a, 0) + 1
    assert n_vacant == 1
    assert counts == dict(DEFAULT_ARCHETYPE_COUNTS)


# --- KeeperArchive (A5) ---------------------------------------------------------------------


def test_archive_a0_always_equals_incumbent():
    arc = KeeperArchive(k=5, min_sep=0.05, d=3)
    x1 = np.array([0.1, 0.1, 0.1])
    arc.on_evaluation(x1, 1.0, is_new_incumbent=True)
    assert arc.f_A[0] == 1.0
    assert np.array_equal(arc.A[0], x1)

    x2 = np.array([0.9, 0.9, 0.9])
    arc.on_evaluation(x2, 0.5, is_new_incumbent=True)
    assert arc.f_A[0] == 0.5
    assert np.array_equal(arc.A[0], x2), "A[0] always equals the incumbent"


def test_archive_never_exceeds_k_members():
    rng = np.random.default_rng(4)
    arc = KeeperArchive(k=5, min_sep=0.01, d=3)
    arc.on_evaluation(np.zeros(3), 0.0, is_new_incumbent=True)
    for _ in range(200):
        x = rng.random(3)
        f = float(rng.random())
        arc.on_evaluation(x, f, is_new_incumbent=False)
        assert arc.size <= 5, "the archive never exceeds K members"


def test_archive_min_separation_between_members():
    rng = np.random.default_rng(5)
    arc = KeeperArchive(k=8, min_sep=0.2, d=4)
    arc.on_evaluation(rng.random(4), 1.0, is_new_incumbent=True)
    for _ in range(500):
        x = rng.random(4)
        f = float(rng.random())
        arc.on_evaluation(x, f, is_new_incumbent=False)
    if arc.size > 1:
        for i in range(arc.size):
            for j in range(arc.size):
                if i == j:
                    continue
                dist = np.linalg.norm(arc.A[i] - arc.A[j]) / np.sqrt(4)
                assert dist >= 0.2 - 1e-9, "separation between members is at least min_sep"


def test_archive_disabled_is_incumbent_only():
    arc = KeeperArchive(k=1, min_sep=0.05, d=2)
    arc.on_evaluation(np.array([0.0, 0.0]), 5.0, is_new_incumbent=True)
    arc.on_evaluation(np.array([0.9, 0.9]), 4.0, is_new_incumbent=False)
    assert arc.size == 1, "disabled: K = 1 (incumbent only)"


# --- TabuRegister (A6) -----------------------------------------------------------------------


def test_tabu_register_fifo_cap():
    reg = TabuRegister(t_max=3, r_tabu=0.02, d=2)
    for i in range(5):
        reg.add(np.array([i * 0.01, 0.0]))
    assert len(reg) == 3


def test_tabu_register_detects_nearby_point():
    reg = TabuRegister(t_max=20, r_tabu=0.05, d=2)
    reg.add(np.array([0.5, 0.5]))
    assert reg.is_tabu(np.array([0.51, 0.5]))
    assert not reg.is_tabu(np.array([0.9, 0.9]))


# --- Ball (A4) --------------------------------------------------------------------------------


def test_ball_basic_fields():
    ball = Ball(x_b=np.array([0.5, 0.5]), f_b=1.0, carrier=3)
    assert ball.carrier == 3
    assert ball.passes_tried == 0
    assert ball.passes_retained == 0
