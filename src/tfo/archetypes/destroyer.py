"""Destroyer (mechanism-interface.md §2.6, FR-010).

Operator: among the pairs in N(i) union {i} that are closer than r_niche, the worse member w of
each pair is kicked: y = x_w + F*(x_r1 - x_r2), with r1 and r2 drawn from N(i). The kick is
accepted unconditionally, because clearing displaces the loser whatever its fitness, and the
better member is kept. If no pair is closer than r_niche, apply N (Clearing / crowding-based
niching; Petrowski 1996; Mahfoud 1995).
"""

from __future__ import annotations

import numpy as np

from tfo import neutral
from tfo.registry import MechanismTag
from tfo.squad import normalized_distance
from tfo.tactics import offside


def _slot_to_agent(squad) -> dict[int, int]:
    return {int(s): i for i, s in enumerate(squad.slot) if s >= 0}


def _kick(
    worse_agent: int, neighbour_slots: list[int], slot_to_agent: dict[int, int], ctx, rng
) -> None:
    squad = ctx.squad
    if len(neighbour_slots) >= 2:
        r1_slot, r2_slot = rng.choice(neighbour_slots, size=2, replace=False)
    elif len(neighbour_slots) == 1:
        r1_slot = r2_slot = neighbour_slots[0]
    else:
        r1_slot = r2_slot = None

    if r1_slot is None:
        kick_vec = np.zeros(squad.d)
    else:
        x_r1 = squad.X[slot_to_agent[int(r1_slot)]]
        x_r2 = squad.X[slot_to_agent[int(r2_slot)]]
        kick_vec = ctx.cfg.operators.de_f * (x_r1 - x_r2)

    x_w = squad.X[worse_agent]
    y = x_w + kick_vec
    y = offside.repair(y, x_w, rng)
    f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.DESTROYER)[0])
    squad.update_agent(worse_agent, y, f_y)  # unconditional


def move(i: int, ctx, rng: np.random.Generator) -> None:
    squad = ctx.squad
    formation = ctx.formation
    slot_i = int(squad.slot[i])
    slot_to_agent = _slot_to_agent(squad)
    neighbour_slots = list(formation.neighbours[slot_i])
    niche_radius = ctx.cfg.operators.niche_radius

    any_kick = False
    for nbr_slot in neighbour_slots:
        j = slot_to_agent.get(int(nbr_slot))
        if j is None or j == i:
            continue
        dist = float(normalized_distance(squad.X[i], squad.X[j]))
        if dist < niche_radius:
            any_kick = True
            worse = i if squad.f[i] > squad.f[j] else j
            _kick(worse, neighbour_slots, slot_to_agent, ctx, rng)

    if not any_kick:
        y = neutral.propose(squad.X[i], ctx.cfg.operators.neutral_sigma, squad.stamina[i], rng)
        y = offside.repair(y, squad.X[i], rng)
        f_y = float(ctx.account.evaluate(y[None, :], MechanismTag.DESTROYER)[0])
        if f_y <= squad.f[i]:
            squad.update_agent(i, y, f_y)
