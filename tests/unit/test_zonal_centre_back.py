"""Unit tests for the Zonal Centre-Back and its Latin-hypercube stratification (tasks.md T022;
mechanism-interface.md §2.2, data-model.md A9)."""

from __future__ import annotations

import numpy as np

from tfo.archetypes.zonal_centre_back import Zones, propose


def test_proposal_lies_inside_agents_stratum():
    rng = np.random.default_rng(0)
    m, d = 4, 3
    zones = Zones.redraw(m=m, d=d, rng=rng)
    for k in range(m):
        lo, hi = zones.stratum_bounds(k)
        for _ in range(20):
            y = propose(k, zones, rng)
            assert np.all(y >= lo - 1e-12) and np.all(y <= hi + 1e-12)


def test_strata_pairwise_disjoint_after_redraw():
    rng = np.random.default_rng(1)
    m, d = 5, 2
    zones = Zones.redraw(m=m, d=d, rng=rng)
    boxes = [zones.stratum_bounds(k) for k in range(m)]
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            lo_i, hi_i = boxes[i]
            lo_j, hi_j = boxes[j]
            # Disjoint iff they do not overlap in every dimension simultaneously.
            overlap = np.all((lo_i < hi_j) & (lo_j < hi_i))
            assert not overlap, "the m strata are pairwise disjoint"


def test_projections_tile_unit_interval_on_every_coordinate():
    rng = np.random.default_rng(2)
    m, d = 6, 3
    zones = Zones.redraw(m=m, d=d, rng=rng)
    for j in range(d):
        intervals = sorted(
            (zones.stratum_bounds(k)[0][j], zones.stratum_bounds(k)[1][j]) for k in range(m)
        )
        # Sub-intervals of width 1/m, contiguous, covering [0, 1] exactly once each.
        assert intervals[0][0] == 0.0
        assert intervals[-1][1] == 1.0
        for a, b in zip(intervals, intervals[1:]):
            assert abs(a[1] - b[0]) < 1e-12
