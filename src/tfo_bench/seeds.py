"""tfo_bench.seeds: common-random-numbers (CRN) seed derivation (research.md R11).

`derive_seed` is deliberately the *only* place a run seed is computed. It is a pure function of
(master_seed, suite_code, function_id, dim, run): every algorithm and every ablation/sensitivity
variant at the same (cell, run) therefore gets the identical seed just by calling it with the same
arguments, with no special-casing needed anywhere else.
"""

from __future__ import annotations

import numpy as np

#: Fixed, stable integer codes for each suite (part of the derivation key, not secret; any stable
#: total mapping satisfies research.md R11, since what matters is that it never changes once used).
SUITE_CODE: dict[str, int] = {
    "cec2017": 1,
    "cec2022": 2,
    "engineering": 3,
    "tuning": 4,
}


def derive_seed(master_seed: int, suite_code: int, function_id: int, dim: int, run: int) -> int:
    """`SeedSequence([MASTER_SEED, suite_code, function_id, dim, run]).generate_state(1)[0] &
    0x7FFFFFFF`, kept nonzero (research.md R11)."""
    state = np.random.SeedSequence(
        [int(master_seed), int(suite_code), int(function_id), int(dim), int(run)]
    ).generate_state(1)[0]
    seed = int(state) & 0x7FFFFFFF
    if seed == 0:
        # "kept nonzero": 0x7FFFFFFF is itself nonzero and outside the reserved value, so this
        # substitution can never collide with a seed produced by a different key.
        seed = 0x7FFFFFFF
    return seed


def cell_seed(master_seed: int, suite: str, function_id: int, dim: int, run: int) -> int:
    """Convenience wrapper keyed by suite name instead of its numeric code."""
    return derive_seed(master_seed, SUITE_CODE[suite], function_id, dim, run)
