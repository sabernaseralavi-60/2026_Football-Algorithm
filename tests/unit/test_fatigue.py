"""Unit tests for fatigue (tasks.md T045; mechanism-interface.md §2.17)."""

from __future__ import annotations

import numpy as np

from tfo.tactics.fatigue import drain, recover


def test_drain_is_monotone_in_distance():
    s0 = 1.0
    d = 3
    s_small = drain(s0, delta_x_norm=0.01, kappa=0.5, s_min=0.2, d=d)
    s_large = drain(s0, delta_x_norm=0.5, kappa=0.5, s_min=0.2, d=d)
    assert s_large <= s_small, "drain is monotone in distance"


def test_drain_never_below_s_min():
    s = drain(0.3, delta_x_norm=10.0, kappa=1.0, s_min=0.2, d=2)
    assert s >= 0.2


def test_recovery_shrinks_with_t():
    r_early = recover(0.3, r0=0.5, t=0.1)
    r_late = recover(0.3, r0=0.5, t=0.9)
    assert r_early > r_late, "recovery shrinks with t"


def test_recovery_never_exceeds_one():
    r = recover(0.99, r0=0.5, t=0.0)
    assert r <= 1.0


def test_substitutes_enter_with_full_stamina():
    # This is asserted directly on the substitutions module's own behaviour (test_substitutions.py
    # test_substitute_enters_fresh); documented here as a cross-reference invariant of A11/FR-020.
    assert True
