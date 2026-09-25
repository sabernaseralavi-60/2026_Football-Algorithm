"""Unit/property tests for the offside line (tasks.md T043; mechanism-interface.md §2.15)."""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tfo.tactics import offside


@given(
    x_old=st.floats(0.0, 1.0),
    y=st.floats(-5.0, 5.0),
    u=st.floats(0.0, 1.0),
)
@settings(max_examples=300)
def test_repaired_point_in_box_and_between_old_and_bound(x_old, y, u):
    rng = _FixedRng(u)
    repaired = offside.repair(np.array([y]), np.array([x_old]), rng)[0]
    assert 0.0 <= repaired <= 1.0, "repaired point lies in [0, 1]^D"
    if y < 0.0:
        bound = 0.0
        lo, hi = min(x_old, bound), max(x_old, bound)
        assert lo - 1e-9 <= repaired <= hi + 1e-9
    elif y > 1.0:
        bound = 1.0
        lo, hi = min(x_old, bound), max(x_old, bound)
        assert lo - 1e-9 <= repaired <= hi + 1e-9
    else:
        assert repaired == pytest.approx(y)


class _FixedRng:
    """Minimal stand-in exposing `.random(shape)` returning a fixed value, for property tests."""

    def __init__(self, u: float):
        self.u = u

    def random(self, shape):
        return np.full(shape, self.u)


def test_points_near_bound_remain_reachable():
    # With U -> 0, the repaired point can land arbitrarily close to x_old (near the bound).
    rng = _FixedRng(1e-9)
    x_old = np.array([0.999])
    y = np.array([1.5])
    repaired = offside.repair(y, x_old, rng)
    assert repaired[0] == pytest.approx(0.999, abs=1e-6)


def test_clip_is_plain_clipping():
    y = np.array([-0.3, 0.5, 1.8])
    clipped = offside.clip(y)
    assert np.array_equal(clipped, [0.0, 0.5, 1.0])


def test_epsilon_zero_after_tc():
    assert offside.epsilon(t=0.9, eps0=1.0, t_c=0.8, cp=5.0) == 0.0
    assert offside.epsilon(t=1.0, eps0=1.0, t_c=0.8, cp=5.0) == 0.0


def test_epsilon_positive_before_tc_and_decreasing():
    e0 = offside.epsilon(t=0.0, eps0=1.0, t_c=0.8, cp=5.0)
    e1 = offside.epsilon(t=0.4, eps0=1.0, t_c=0.8, cp=5.0)
    assert e0 > e1 > 0.0


def test_epsilon_lexicographic_prefers_feasible_when_within_eps():
    # Both within eps of feasibility: compare on f.
    better = offside.epsilon_lex_better(f_a=1.0, v_a=0.01, f_b=2.0, v_b=0.02, eps=0.05)
    assert better == "a"


def test_epsilon_lexicographic_prefers_less_violation_when_outside_eps():
    # Neither within eps: compare on violation first.
    better = offside.epsilon_lex_better(f_a=5.0, v_a=0.5, f_b=1.0, v_b=1.0, eps=0.05)
    assert better == "a"
