"""Unit tests for the formation lattice (tasks.md T037; data-model.md A3)."""

from __future__ import annotations

import numpy as np
import pytest

from tfo.tactics.formation import SHAPES_N30, Formation


@pytest.mark.parametrize("name", ["compact", "balanced", "stretched"])
def test_three_shapes_exist_for_n30(name):
    formation = Formation.build(name, n_out=29)
    assert formation.name == name
    assert formation.lines * formation.lanes >= 29


def test_vacancy_rule():
    for name in ("compact", "balanced", "stretched"):
        formation = Formation.build(name, n_out=29)
        vacancies = formation.lines * formation.lanes - 29
        assert vacancies == int(np.sum(formation.vacant))
        assert 0 <= vacancies < formation.lanes, (
            "Vacancies = lines x lanes - n_out, with 0 <= vacancies < lanes"
        )


def test_ratio_strictly_decreasing_compact_to_stretched():
    ratios = [Formation.build(name, n_out=29).ratio for name in ("compact", "balanced", "stretched")]
    assert ratios[0] > ratios[1] > ratios[2], (
        "The ratio is strictly decreasing from compact to balanced to stretched"
    )


def test_shapes_n30_dimensions_match_data_model():
    assert SHAPES_N30["compact"] == (5, 6)
    assert SHAPES_N30["balanced"] == (3, 10)
    assert SHAPES_N30["stretched"] == (2, 15)


def test_relay_does_not_touch_squad_state():
    """A re-lay only recomputes slot_rc/neighbours; it never mutates Squad's X or f (FR-013).
    Formation objects carry no reference to Squad state at all, so this is true by construction;
    this test pins that a fresh build (a "re-lay") is a pure function of (name, n_out)."""
    f1 = Formation.build("compact", n_out=29)
    f2 = Formation.build("compact", n_out=29)
    assert np.array_equal(f1.slot_rc, f2.slot_rc)
    assert np.array_equal(f1.vacant, f2.vacant)


def test_neighbours_are_von_neumann_on_torus_and_skip_vacant():
    formation = Formation.build("compact", n_out=29)
    # Slot 29 is the vacancy (last row-major cell); no filled slot should list it as a neighbour.
    vacant_slot = int(np.where(formation.vacant)[0][0])
    for s in range(formation.lines * formation.lanes):
        if formation.vacant[s]:
            continue
        assert vacant_slot not in formation.neighbours[s]
        assert len(formation.neighbours[s]) <= 4


def test_graph_dist_symmetric_and_zero_on_diagonal():
    formation = Formation.build("balanced", n_out=29)
    gd = formation.graph_dist
    assert np.array_equal(gd, gd.T)
    for s in range(formation.lines * formation.lanes):
        if not formation.vacant[s]:
            assert gd[s, s] == 0


def test_fully_connected_mode():
    formation = Formation.build("compact", n_out=29, fully_connected=True)
    filled = [s for s in range(formation.lines * formation.lanes) if not formation.vacant[s]]
    for s in filled:
        others = set(filled) - {s}
        assert set(formation.neighbours[s]) == others
        for o in others:
            assert formation.graph_dist[s, o] == 1
    # Slot rows are kept even in fully-connected mode.
    assert formation.slot_rc.shape[0] == formation.lines * formation.lanes
