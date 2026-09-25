"""Sweeper-Keeper (mechanism-interface.md §2.1, FR-005): the bounded, distance-diverse archive.

Operator: elitism with a bounded hall-of-fame archive (De Jong 1975; Rosin & Belew 1997). The
Sweeper-Keeper does not itself take a `move(i, ctx, rng)` step charged to any evaluation: it is a
hook that fires on every `EvalAccount.evaluate` call (mechanism-interface.md §1, "The keeper-archive
update is a hook on every account.evaluate call, so it runs continuously, not at a numbered step").
"""

from __future__ import annotations

import numpy as np

from tfo.squad import KeeperArchive


def on_evaluation(
    archive: KeeperArchive, x: np.ndarray, f: float, is_new_incumbent: bool
) -> None:
    """The archive-update hook: delegates to `KeeperArchive.on_evaluation` (data-model.md A5)."""
    archive.on_evaluation(x, f, is_new_incumbent)
