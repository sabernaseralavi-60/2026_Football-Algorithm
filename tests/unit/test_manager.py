"""Unit tests for the manager's tactical state machine (tasks.md T047; mechanism-interface.md
§2.19, data-model.md A8)."""

from __future__ import annotations

from tfo.config import ManagerConfig, TFOConfig
from tfo.manager import Manager, TacticalState


def _manager(**overrides):
    cfg = ManagerConfig(**overrides) if overrides else ManagerConfig()
    states = TFOConfig().states
    return Manager(cfg, states)


def test_oscillating_input_cannot_change_state_on_consecutive_iterations():
    mgr = _manager(dwell_min=5)
    states_seen = []
    for k in range(60):
        # div oscillates rapidly around the low-diversity threshold.
        div = 0.02 if k % 2 == 0 else 0.5
        mgr.update(div=div, poss=0.9, material_improvement=True, t=0.5)
        states_seen.append(mgr.state)

    # Count the run lengths of the observed state sequence; every run must be >= dwell_min, i.e.
    # the state can never change on two consecutive iterations (dwell_min > 1 enforces this).
    run_lengths = []
    current = states_seen[0]
    length = 1
    for s in states_seen[1:]:
        if s == current:
            length += 1
        else:
            run_lengths.append(length)
            current = s
            length = 1
    run_lengths.append(length)
    # Drop the first run (it may be shorter, since it started counting before update() calls began).
    for run in run_lengths[1:-1]:
        assert run >= 5, "the state cannot change on consecutive iterations because of noise"


def test_high_press_never_entered_before_t_press():
    mgr = _manager(dwell_min=1, t_press=0.5)
    for k in range(20):
        mgr.update(div=0.0, poss=1.0, material_improvement=True, t=0.1)
        assert mgr.state != TacticalState.HIGH_PRESS, "HIGH_PRESS is never entered before t_press"


def test_high_press_reachable_after_t_press():
    mgr = _manager(dwell_min=1, t_press=0.1, d_low_enter=0.1, d_low_exit=0.15, p_high_enter=0.5, p_high_exit=0.4)
    reached = False
    for k in range(20):
        mgr.update(div=0.0, poss=1.0, material_improvement=True, t=0.9)
        if mgr.state == TacticalState.HIGH_PRESS:
            reached = True
    assert reached


def test_chasing_present_only_when_manager_is_driven():
    """TFO-static never calls Manager.update() at all (engine.py's job); a Manager instance that
    is never updated stays in its initial CONTROL state, so CHASING can only appear in TFO."""
    mgr = _manager()
    assert mgr.state == TacticalState.CONTROL


def test_chasing_triggered_by_drought():
    mgr = _manager(dwell_min=1, g_max=3)
    for _ in range(3):
        mgr.update(div=0.2, poss=0.5, material_improvement=False, t=0.5)
    assert mgr.state == TacticalState.CHASING


def test_chasing_exits_on_material_improvement_subject_to_dwell():
    mgr = _manager(dwell_min=2, g_max=2)
    mgr.update(div=0.2, poss=0.5, material_improvement=False, t=0.5)
    mgr.update(div=0.2, poss=0.5, material_improvement=False, t=0.5)
    assert mgr.state == TacticalState.CHASING
    mgr.update(div=0.2, poss=0.5, material_improvement=True, t=0.5)  # resets drought
    # Dwell not yet satisfied (only 1 iteration in CHASING) -> stays in CHASING.
    assert mgr.state == TacticalState.CHASING
    mgr.update(div=0.2, poss=0.5, material_improvement=True, t=0.5)
    assert mgr.state != TacticalState.CHASING
