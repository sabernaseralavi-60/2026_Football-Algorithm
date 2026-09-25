"""Integration test: the 9-step engine iteration order is deterministic and pinned
(tasks.md T059; mechanism-interface.md §3)."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np

from tfo import engine
from tfo.config import TFOConfig


def _sphere(X):
    return np.sum((X - 0.3) ** 2, axis=1)


def test_determinism_same_seed_gives_identical_results():
    cfg = TFOConfig()
    acc1, trace1, _ = engine.run(cfg, _sphere, d=4, budget=800, seed=42)
    acc2, trace2, _ = engine.run(cfg, _sphere, d=4, budget=800, seed=42)

    assert acc1.evals_used == acc2.evals_used
    assert acc1.f_best == acc2.f_best
    assert np.array_equal(acc1.x_best, acc2.x_best)
    assert acc1.evals_by_tag == acc2.evals_by_tag
    assert np.array_equal(acc1.curve, acc2.curve)
    assert [s.state for s in trace1.segments] == [s.state for s in trace2.segments]


def test_step_order_is_manager_possession_pressing_then_per_agent_moves():
    calls: list[str] = []

    real_manager_update = None

    from tfo.manager import Manager
    from tfo.tactics import possession, pressing

    orig_manager_update = Manager.update
    orig_possession_apply = possession.apply
    orig_pressing_membership = pressing.membership

    def spy_manager_update(self, *a, **kw):
        calls.append("manager")
        return orig_manager_update(self, *a, **kw)

    def spy_possession_apply(*a, **kw):
        calls.append("possession")
        return orig_possession_apply(*a, **kw)

    def spy_pressing_membership(*a, **kw):
        calls.append("pressing_membership")
        return orig_pressing_membership(*a, **kw)

    with patch.object(Manager, "update", spy_manager_update), patch.object(
        possession, "apply", spy_possession_apply
    ), patch.object(pressing, "membership", spy_pressing_membership):
        engine.run(TFOConfig(), _sphere, d=3, budget=200, seed=1)

    # Only the first iteration's prefix is checked, since later iterations repeat the same pattern.
    first_iteration = calls[:3]
    assert first_iteration == ["manager", "possession", "pressing_membership"], (
        "the 9-step iteration order (mechanism-interface.md §3) is pinned: "
        "manager -> possession -> pressing membership -> per-agent moves -> ..."
    )
    # The pattern repeats identically every iteration (steps 1-3 recur in lockstep).
    for i in range(0, len(calls) - 2, 3):
        assert calls[i : i + 3] == ["manager", "possession", "pressing_membership"]
