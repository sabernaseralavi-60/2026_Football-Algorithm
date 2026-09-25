"""Unit test for the Sweeper-Keeper (tasks.md T021; mechanism-interface.md §2.1)."""

from __future__ import annotations

import numpy as np

from tfo.archetypes.sweeper_keeper import on_evaluation
from tfo.squad import KeeperArchive


def test_a0_always_incumbent_min_sep_and_bounded():
    rng = np.random.default_rng(0)
    archive = KeeperArchive(k=5, min_sep=0.1, d=3)
    incumbent_x, incumbent_f = rng.random(3), 10.0
    on_evaluation(archive, incumbent_x, incumbent_f, is_new_incumbent=True)

    for _ in range(300):
        x = rng.random(3)
        f = float(rng.random() * 10)
        is_best = f < archive.f_A[0]
        on_evaluation(archive, x, f, is_new_incumbent=is_best)
        assert archive.size <= 5, "the archive never exceeds K members"
        assert archive.f_A[0] == min(archive.f_A), "A[0] always equals the incumbent"

    for i in range(archive.size):
        for j in range(archive.size):
            if i != j:
                d = np.linalg.norm(archive.A[i] - archive.A[j]) / np.sqrt(3)
                assert d >= 0.1 - 1e-9
