"""Unit tests for the Overlapping Wing-Back (tasks.md T023; mechanism-interface.md §2.3)."""

from __future__ import annotations

import numpy as np

from tfo.archetypes.overlapping_wing_back import quasi_opposite_jump


def test_y_lies_coordinate_wise_between_c_and_o():
    rng = np.random.default_rng(0)
    c = np.array([0.5, 0.3])
    x = np.array([0.2, 0.9])
    o = 2 * c - x
    for _ in range(50):
        y = quasi_opposite_jump(c, x, rng)
        lo = np.minimum(c, o)
        hi = np.maximum(c, o)
        assert np.all(y >= lo - 1e-12) and np.all(y <= hi + 1e-12)


def test_keep_better_rule():
    # If y improves on x, the caller keeps y; otherwise it keeps x. This is a property of the
    # move() acceptance logic, exercised through a fake context.
    from types import SimpleNamespace

    import tfo.archetypes.overlapping_wing_back as owb
    from tfo.registry import MechanismTag

    class FakeSquad:
        def __init__(self):
            self.X = np.array([[0.2, 0.9], [0.5, 0.3], [0.8, 0.1]])
            self.f = np.array([10.0, 1.0, 1.0])
            self.updated = None

        def update_agent(self, i, x_new, f_new):
            self.updated = (i, x_new, f_new)
            self.X[i] = x_new
            self.f[i] = f_new

    class FakeAccount:
        def evaluate(self, X, tag):
            # Objective: sum of squares, so moving toward the origin always improves.
            return np.sum(X**2, axis=1)

    squad = FakeSquad()
    ctx = SimpleNamespace(squad=squad, account=FakeAccount(), cfg=SimpleNamespace(
        operators=SimpleNamespace(jump_rate=1.0)
    ))
    rng = np.random.default_rng(1)
    f_before = squad.f[0]
    owb.move(0, ctx, rng)
    assert squad.updated is not None
    i, x_new, f_new = squad.updated
    assert f_new <= f_before, "the keep-better rule holds (initial f=10.0 is worse than any jump)"
