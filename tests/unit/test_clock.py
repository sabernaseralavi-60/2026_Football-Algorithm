"""Unit tests for MatchClock (tasks.md T011; data-model.md A7)."""

from __future__ import annotations

from tfo.clock import MatchClock


def test_fixture_boundary_by_evaluations_not_iterations():
    clock = MatchClock(budget=100, n_fixtures=10)
    # Fixture 0 should end at the first iteration-end with evals_used >= 1*100/10 = 10.
    crossed = []
    for evals in [3, 4, 5]:  # cumulative 3, 7, 12 -> crosses 10 on the third call
        crossed.append(clock.advance(evals))
    assert crossed == [False, False, True]
    assert clock.fixture == 1
    assert clock.evals_used == 12


def test_t_is_budget_fraction_elapsed():
    clock = MatchClock(budget=100, n_fixtures=10)
    clock.advance(50)
    assert abs(clock.t - 0.5) < 1e-9


def test_iteration_counter_increments():
    clock = MatchClock(budget=100, n_fixtures=10)
    clock.tick_iteration()
    clock.tick_iteration()
    assert clock.iteration == 2


def test_boundary_hooks_fire_in_documented_order():
    clock = MatchClock(budget=100, n_fixtures=4)
    order: list[str] = []
    clock.on_boundary(
        rotation=lambda: order.append("rotation"),
        zonal_redraw=lambda: order.append("zonal_redraw"),
        stamina_recovery=lambda: order.append("stamina_recovery"),
        substitution_cap_reset=lambda: order.append("substitution_cap_reset"),
    )
    clock.advance(25)  # crosses the first fixture boundary (100/4 = 25)
    assert order == ["rotation", "zonal_redraw", "stamina_recovery", "substitution_cap_reset"]


def test_no_boundary_crossed_mid_fixture():
    clock = MatchClock(budget=100, n_fixtures=4)
    order: list[str] = []
    clock.on_boundary(
        rotation=lambda: order.append("rotation"),
        zonal_redraw=lambda: order.append("zonal_redraw"),
        stamina_recovery=lambda: order.append("stamina_recovery"),
        substitution_cap_reset=lambda: order.append("substitution_cap_reset"),
    )
    clock.advance(10)
    assert order == []
