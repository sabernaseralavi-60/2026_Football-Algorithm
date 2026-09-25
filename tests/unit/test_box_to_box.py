"""Unit tests for the Box-to-Box Engine (tasks.md T025; mechanism-interface.md §2.5)."""

from __future__ import annotations

import numpy as np

from tfo.archetypes.box_to_box import binomial_crossover, pick_deepest_and_advanced
from tfo.tactics.formation import Formation


def test_donors_come_only_from_neighbourhood_plus_self():
    formation = Formation.build("balanced", n_out=29)
    slot_i = 5
    neighbourhood = list(formation.neighbours[slot_i]) + [slot_i]
    rng = np.random.default_rng(0)
    d_slot, a_slot = pick_deepest_and_advanced(slot_i, formation, rng)
    assert d_slot in neighbourhood
    assert a_slot in neighbourhood


def test_deepest_line_at_most_advanced_line():
    formation = Formation.build("compact", n_out=29)
    rng = np.random.default_rng(1)
    for slot_i in range(formation.n_slots):
        if formation.vacant[slot_i]:
            continue
        d_slot, a_slot = pick_deepest_and_advanced(slot_i, formation, rng)
        assert formation.row_of(d_slot) <= formation.row_of(a_slot)


def test_binomial_crossover_keeps_at_least_one_donor_coordinate():
    rng = np.random.default_rng(2)
    x = np.zeros(5)
    v = np.ones(5)
    y = binomial_crossover(x, v, cr=0.0, rng=rng)
    # CR = 0 still forces exactly one coordinate (j_rand) from v.
    assert np.sum(y == 1.0) == 1
    assert np.sum(y == 0.0) == 4
