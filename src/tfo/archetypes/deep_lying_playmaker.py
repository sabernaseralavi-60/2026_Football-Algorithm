"""Deep-Lying Playmaker (mechanism-interface.md §2.4, FR-008).

Operator: the partner p is drawn uniformly from the slots at graph distance >= d_max - 1 from
agent i on the formation lattice. y is the BLX-alpha blend of x_i and x_p, accepted greedily. This
is the declared long-range exception to FR-002 (BLX-alpha crossover over small-world long-range
links; Eshelman & Schaffer 1993; Watts & Strogatz 1998).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside


def graph_diameter(formation) -> int:
    filled = [s for s in range(formation.n_slots) if not formation.vacant[s]]
    return int(np.max(formation.graph_dist[np.ix_(filled, filled)]))


def choose_partner(slot_i: int, formation, d_max: int, rng: np.random.Generator) -> int:
    candidates = [
        s
        for s in range(formation.n_slots)
        if not formation.vacant[s] and s != slot_i and formation.graph_dist[slot_i, s] >= d_max - 1
    ]
    if not candidates:
        candidates = [s for s in range(formation.n_slots) if not formation.vacant[s] and s != slot_i]
    return int(rng.choice(candidates))


def blx_alpha(x1: np.ndarray, x2: np.ndarray, alpha: float, rng: np.random.Generator) -> np.ndarray:
    lo = np.minimum(x1, x2) - alpha * np.abs(x1 - x2)
    hi = np.maximum(x1, x2) + alpha * np.abs(x1 - x2)
    return lo + rng.random(x1.shape) * (hi - lo)


def move(i: int, ctx, rng: np.random.Generator) -> None:
    formation = ctx.formation
    slot_i = int(ctx.squad.slot[i])
    d_max = graph_diameter(formation)
    partner_slot = choose_partner(slot_i, formation, d_max, rng)

    # Find the outfield agent currently occupying partner_slot.
    partner_idx = int(np.where(ctx.squad.slot == partner_slot)[0][0])

    y = blx_alpha(ctx.squad.X[i], ctx.squad.X[partner_idx], ctx.cfg.operators.blx_alpha, rng)
    y = offside.repair(y, ctx.squad.X[i], rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.DEEP_LYING_PLAYMAKER)[0])
    if f_y <= ctx.squad.f[i]:
        ctx.squad.update_agent(i, y, f_y)
