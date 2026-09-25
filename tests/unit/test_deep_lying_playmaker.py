"""Unit tests for the Deep-Lying Playmaker (tasks.md T024; mechanism-interface.md §2.4)."""

from __future__ import annotations

import numpy as np

from tfo.archetypes.deep_lying_playmaker import blx_alpha, choose_partner
from tfo.tactics.formation import Formation


def test_partner_graph_distance_at_least_d_max_minus_one():
    formation = Formation.build("stretched", n_out=29)
    filled = [s for s in range(formation.n_slots) if not formation.vacant[s]]
    d_max = int(np.max(formation.graph_dist[np.ix_(filled, filled)]))
    rng = np.random.default_rng(0)
    for slot_i in filled[:10]:
        partner = choose_partner(slot_i, formation, d_max, rng)
        assert formation.graph_dist[slot_i, partner] >= d_max - 1
        assert not formation.vacant[partner]
        assert partner != slot_i


def test_y_lies_in_alpha_widened_box():
    rng = np.random.default_rng(1)
    x1 = np.array([0.2, 0.8])
    x2 = np.array([0.6, 0.3])
    alpha = 0.5
    lo = np.minimum(x1, x2) - alpha * np.abs(x1 - x2)
    hi = np.maximum(x1, x2) + alpha * np.abs(x1 - x2)
    for _ in range(200):
        y = blx_alpha(x1, x2, alpha, rng)
        assert np.all(y >= lo - 1e-12) and np.all(y <= hi + 1e-12)
