"""Unit test for the neutral (1+1)-ES fallback move (research.md R14)."""

from __future__ import annotations

import numpy as np

from tfo.neutral import propose


def test_neutral_move_is_deterministic_given_rng_state():
    x = np.array([0.5, 0.5])
    rng1 = np.random.default_rng(0)
    rng2 = np.random.default_rng(0)
    y1 = propose(x, sigma=0.1, stamina_i=1.0, rng=rng1)
    y2 = propose(x, sigma=0.1, stamina_i=1.0, rng=rng2)
    assert np.array_equal(y1, y2)


def test_neutral_move_scales_with_stamina():
    x = np.zeros(2)
    rng_full = np.random.default_rng(1)
    rng_low = np.random.default_rng(1)
    y_full = propose(x, sigma=1.0, stamina_i=1.0, rng=rng_full)
    y_low = propose(x, sigma=1.0, stamina_i=0.1, rng=rng_low)
    assert np.allclose(y_low, 0.1 * y_full)
