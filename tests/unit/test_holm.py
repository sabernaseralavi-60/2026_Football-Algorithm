"""Unit test for the in-house Holm correction against a published worked example (T097;
research.md R12.7).

Worked example (Holm-Bonferroni step-down method, the standard textbook illustration also given
on Wikipedia's "Holm-Bonferroni method" page): p = [0.01, 0.04, 0.03, 0.005], m = 4.

Sorted ascending: 0.005, 0.01, 0.03, 0.04 (ranks 1..4).
Step-down multipliers (m - rank + 1): 4, 3, 2, 1.
Raw Holm values:  0.005*4=0.02,  0.01*3=0.03,  0.03*2=0.06,  0.04*1=0.04.
Enforced monotone (running maximum, since Holm-adjusted p-values must be non-decreasing in the
sorted order): 0.02, 0.03, 0.06, max(0.04, 0.06)=0.06.
So, in the ORIGINAL order [0.01, 0.04, 0.03, 0.005], the Holm-adjusted p-values are:
[0.03, 0.06, 0.06, 0.02].
"""

from __future__ import annotations

import pytest

from tfo_bench.stats import holm_correction


def test_holm_correction_matches_worked_example():
    p_values = [0.01, 0.04, 0.03, 0.005]
    expected = [0.03, 0.06, 0.06, 0.02]
    got = holm_correction(p_values)
    for g, e in zip(got, expected):
        assert g == pytest.approx(e, abs=1e-12)


def test_holm_is_never_less_conservative_than_raw_p():
    p_values = [0.001, 0.2, 0.03, 0.049, 0.5]
    adjusted = holm_correction(p_values)
    for raw, adj in zip(p_values, adjusted):
        assert adj >= raw


def test_holm_adjusted_values_are_capped_at_1():
    p_values = [0.9, 0.8, 0.99]
    adjusted = holm_correction(p_values)
    assert all(a <= 1.0 for a in adjusted)


def test_holm_empty_input():
    assert holm_correction([]) == []


def test_holm_single_pvalue_is_unchanged():
    assert holm_correction([0.03]) == pytest.approx([0.03])
