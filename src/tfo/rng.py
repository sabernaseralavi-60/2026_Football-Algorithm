"""Per-mechanism RNG streams, spawned from one SeedSequence at fixed registry indices.

research.md R11: every mechanism draws from its own independent stream, so switching a mechanism
off never shifts another mechanism's draws (the streams are indexed by a fixed per-tag slot, not
handed out sequentially on first use).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import ALL_TAGS, MechanismTag

#: Fixed registry index for each tag's RNG stream (research.md R11). The mapping is the ALL_TAGS
#: order itself, so it is total, stable, and never reassigned.
RNG_REGISTRY_INDEX: dict[MechanismTag, int] = {tag: i for i, tag in enumerate(ALL_TAGS)}


class StreamBank:
    """Spawns one independent `Generator` per mechanism tag from a single `SeedSequence(seed)`."""

    def __init__(self, seed: int):
        self._seed_sequence = np.random.SeedSequence(seed)
        # Spawn every stream up front, at its fixed index, so no stream's state depends on the
        # order or the subset of tags actually queried at runtime.
        children = self._seed_sequence.spawn(len(RNG_REGISTRY_INDEX))
        self._generators: dict[MechanismTag, np.random.Generator] = {
            tag: np.random.Generator(np.random.PCG64(children[idx]))
            for tag, idx in RNG_REGISTRY_INDEX.items()
        }

    def stream(self, tag: MechanismTag) -> np.random.Generator:
        return self._generators[tag]
