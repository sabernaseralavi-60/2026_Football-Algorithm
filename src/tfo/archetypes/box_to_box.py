"""Box-to-Box Engine (mechanism-interface.md §2.5, FR-009).

Operator: v = x_nbest(i) + F*(x_d - x_a). x_d is the neighbourhood member in the deepest line and
x_a the one in the most advanced line (neighbourhood includes i; ties broken at random). Then
y = binomial crossover(x_i, v, CR), accepted greedily (Neighbourhood-based differential mutation,
DEGL-style local DE; Das et al. 2009).
"""

from __future__ import annotations

import numpy as np

from tfo.registry import MechanismTag
from tfo.tactics import offside


def _slot_to_agent(squad) -> dict[int, int]:
    return {int(s): i for i, s in enumerate(squad.slot) if s >= 0}


def pick_deepest_and_advanced(
    slot_i: int, formation, rng: np.random.Generator
) -> tuple[int, int]:
    neighbourhood = list(formation.neighbours[slot_i]) + [slot_i]
    rows = {s: formation.row_of(s) for s in neighbourhood}
    min_row = min(rows.values())
    max_row = max(rows.values())
    deepest = [s for s, r in rows.items() if r == min_row]
    advanced = [s for s, r in rows.items() if r == max_row]
    d_slot = int(rng.choice(deepest))
    a_slot = int(rng.choice(advanced))
    return d_slot, a_slot


def binomial_crossover(
    x: np.ndarray, v: np.ndarray, cr: float, rng: np.random.Generator
) -> np.ndarray:
    d = x.shape[0]
    j_rand = rng.integers(d)
    mask = rng.random(d) < cr
    mask[j_rand] = True
    return np.where(mask, v, x)


def move(i: int, ctx, rng: np.random.Generator) -> None:
    formation = ctx.formation
    squad = ctx.squad
    slot_i = int(squad.slot[i])
    slot_to_agent = _slot_to_agent(squad)

    d_slot, a_slot = pick_deepest_and_advanced(slot_i, formation, rng)
    x_d = squad.X[slot_to_agent[d_slot]]
    x_a = squad.X[slot_to_agent[a_slot]]

    neighbourhood_agents = [slot_to_agent[s] for s in list(formation.neighbours[slot_i]) + [slot_i]]
    nbest_idx = min(neighbourhood_agents, key=lambda a: squad.f[a])

    F = ctx.cfg.operators.de_f
    v = squad.X[nbest_idx] + F * (x_d - x_a)
    y = binomial_crossover(squad.X[i], v, ctx.cfg.operators.de_cr, rng)
    y = offside.repair(y, squad.X[i], rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.BOX_TO_BOX)[0])
    if f_y <= squad.f[i]:
        squad.update_agent(i, y, f_y)
