"""Zonal Centre-Back (mechanism-interface.md §2.2, FR-006; data-model.md A9).

Operator: y ~ U(stratum_k), where stratum_k is agent k's cell of the current Latin-hypercube
stratification; greedy against the agent's own fitness (Stratified / Latin-hypercube sampling,
space partitioning; McKay et al. 1979).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from tfo.registry import Archetype, MechanismTag
from tfo.tactics import offside


@dataclass(frozen=True)
class Zones:
    """The Latin-hypercube stratification (data-model.md A9). `perm[j, k]` is pi_j(k)."""

    perm: np.ndarray  # (D, m)

    @property
    def m(self) -> int:
        return self.perm.shape[1]

    @property
    def d(self) -> int:
        return self.perm.shape[0]

    @classmethod
    def redraw(cls, m: int, d: int, rng: np.random.Generator) -> "Zones":
        perm = np.stack([rng.permutation(m) for _ in range(d)], axis=0)
        return cls(perm=perm)

    def stratum_bounds(self, k: int) -> tuple[np.ndarray, np.ndarray]:
        idx = self.perm[:, k]
        lo = idx / self.m
        hi = (idx + 1) / self.m
        return lo, hi


def propose(k: int, zones: Zones, rng: np.random.Generator) -> np.ndarray:
    """y ~ U(stratum_k)."""
    lo, hi = zones.stratum_bounds(k)
    return lo + rng.random(zones.d) * (hi - lo)


def move(i: int, ctx, rng: np.random.Generator) -> None:
    """Full mechanism: propose inside the agent's stratum, repair, evaluate, accept greedily."""
    slot_i = int(ctx.squad.slot[i])
    k = ctx.role_sheet.ordinal_within(Archetype.ZONAL_CENTRE_BACK, slot_i)
    y = propose(k, ctx.zones, rng)
    y = offside.repair(y, ctx.squad.X[i], rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.ZONAL_CENTRE_BACK)[0])
    if f_y <= ctx.squad.f[i]:
        ctx.squad.update_agent(i, y, f_y)
