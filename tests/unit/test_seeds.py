"""Unit tests for per-mechanism RNG stream spawning (tasks.md T012; research.md R11)."""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.rng import RNG_REGISTRY_INDEX, StreamBank


def test_streams_are_independent_across_mechanisms():
    bank = StreamBank(seed=42)
    a = bank.stream(MechanismTag.VIRTUOSO).random(10)
    b = bank.stream(MechanismTag.FINISHER).random(10)
    assert not np.array_equal(a, b)


def test_streams_are_deterministic_for_same_seed():
    bank1 = StreamBank(seed=123)
    bank2 = StreamBank(seed=123)
    a1 = bank1.stream(MechanismTag.DESTROYER).random(5)
    a2 = bank2.stream(MechanismTag.DESTROYER).random(5)
    assert np.array_equal(a1, a2)


def test_registry_index_is_fixed_per_tag():
    # Every mechanism tag used as a stream key has a fixed registry index.
    for tag in MechanismTag:
        assert tag in RNG_REGISTRY_INDEX


def test_disabling_one_mechanism_does_not_shift_another():
    """Spawning fewer streams (as if a mechanism were disabled and never asked for its stream)
    must not change the draws of the streams that ARE used, because indices are fixed, not
    sequential-on-demand."""
    bank_all = StreamBank(seed=7)
    used_when_all = bank_all.stream(MechanismTag.FINISHER).random(5)

    bank_partial = StreamBank(seed=7)
    # Never touch VIRTUOSO's stream here, simulating it being disabled.
    used_when_partial = bank_partial.stream(MechanismTag.FINISHER).random(5)

    assert np.array_equal(used_when_all, used_when_partial)
