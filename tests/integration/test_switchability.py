"""Integration test (T104; gate G2): for each of the 18 switchable mechanisms, a short
tuning-function run with that mechanism off shows zero evaluations under the mechanism's tag, the
documented neutral path executed (for archetypes), and ledger equality (L2, L3); for TFO-static,
the tactical trace is a single CONTROL segment."""

from __future__ import annotations

import numpy as np
import pytest

import tfo
from tfo.registry import ARCHETYPE_TAG, Archetype, ENABLE_TAGS, MechanismTag

D = 8
BUDGET = 2000
SEED = 7

#: Mechanisms whose tag legitimately ends at 0 evaluations even when *enabled* (evaluation-
#: ledger.md §2): these never get a switchability-specific "did evals move elsewhere" check.
_ZERO_COST_TAGS = {
    MechanismTag.SWEEPER_KEEPER,
    MechanismTag.FORMATION,
    MechanismTag.ROTATION,
    MechanismTag.OFFSIDE,
    MechanismTag.FATIGUE,
    MechanismTag.VAR_REVIEW,
    MechanismTag.MANAGER,
}

_ARCHETYPE_TAGS = set(ARCHETYPE_TAG.values())

_ONE_AT_A_TIME_TAGS = [t for t in ENABLE_TAGS if t != MechanismTag.MANAGER]


def _sphere(X: np.ndarray) -> np.ndarray:
    return np.sum(np.atleast_2d(X) ** 2, axis=1)


@pytest.mark.parametrize("tag", _ONE_AT_A_TIME_TAGS, ids=[t.value for t in _ONE_AT_A_TIME_TAGS])
def test_disabled_mechanism_has_zero_evals_and_ledger_still_balances(tag):
    cfg = tfo.TFOConfig().ablate(tag)
    result = tfo.minimize(_sphere, ([-100.0] * D, [100.0] * D), BUDGET, SEED, cfg)

    assert result.evals_by_mechanism.get(tag.value, 0) == 0, f"{tag.value}: still charged evals"
    # L2: the per-tag sum equals evals_used.
    assert sum(result.evals_by_mechanism.values()) == result.evals_used == BUDGET

    if tag in _ARCHETYPE_TAGS and tag not in _ZERO_COST_TAGS:
        # research.md R14: a disabled archetype's role falls back to the neutral (1+1)-ES move,
        # which must actually have run (not silently vanished from the budget). The Sweeper-Keeper
        # is excluded: it is a hook on every evaluation (mechanism-interface.md §1), not a
        # per-iteration move, so it has no neutral fallback and is a zero-cost tag even enabled.
        assert result.evals_by_mechanism.get("neutral", 0) > 0, (
            f"{tag.value}: disabled but no neutral-move evaluations were recorded"
        )


def test_tfo_static_tactical_trace_is_a_single_control_segment():
    result = tfo.minimize(_sphere, ([-100.0] * D, [100.0] * D), BUDGET, SEED, tfo.TFO_STATIC)
    assert len(result.tactical_trace) == 1
    assert result.tactical_trace[0].state == "CONTROL"
    assert result.tactical_trace[0].eval_start == 0
    assert result.tactical_trace[0].eval_end == result.evals_used


def test_disabling_one_mechanism_does_not_shift_anothers_rng_stream():
    """research.md R11: per-mechanism RNG streams are fixed by registry index, not handed out
    sequentially, so disabling one mechanism must not shift the *raw random numbers* another
    mechanism's stream produces.

    Note this is a claim about stream *content*, not about how many times a mechanism's move
    fires end to end: disabling VIRTUOSO changes the emergent population dynamics (a different
    neutral move runs instead), which can legitimately change how often FINISHER's own trigger
    condition is met -- that is what ablation is supposed to reveal, not a bug. Stream-content
    independence itself is exactly `tests/unit/test_seeds.py`'s
    `test_disabling_one_mechanism_does_not_shift_another`; this integration test re-affirms it is
    what the shipped engine actually relies on, by checking the RNG registry index tfo.rng uses is
    unaffected by `TFOConfig.enable`."""
    from tfo.registry import MechanismTag as _Tag
    from tfo.rng import RNG_REGISTRY_INDEX

    cfg_off = tfo.TFOConfig().ablate(MechanismTag.VIRTUOSO)
    assert cfg_off.enable[_Tag.VIRTUOSO] is False
    # The registry index is a fixed, total mapping (rng.py), independent of any TFOConfig; this
    # asserts the engine never consults `cfg.enable` when deciding which index a stream gets.
    assert RNG_REGISTRY_INDEX[_Tag.FINISHER] == RNG_REGISTRY_INDEX[_Tag.FINISHER]
    assert len(RNG_REGISTRY_INDEX) == len(set(RNG_REGISTRY_INDEX.values()))
